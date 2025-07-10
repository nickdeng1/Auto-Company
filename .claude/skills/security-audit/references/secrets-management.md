# Secrets Management

Secure handling of sensitive configuration and credentials.

## Secret Detection

### Common Secret Patterns

| Type | Regex Pattern | Example |
|------|---------------|---------|
| AWS Access Key | `AKIA[0-9A-Z]{16}` | `AKIAIOSFODNN7EXAMPLE` |
| AWS Secret Key | `[A-Za-z0-9/+=]{40}` | 40-char base64 string |
| GitHub Token | `ghp_[a-zA-Z0-9]{36}` | `ghp_xxxxxxxxxxxx...` |
| GitHub OAuth | `gho_[a-zA-Z0-9]{36}` | `gho_xxxxxxxxxxxx...` |
| Slack Token | `xox[baprs]-[0-9a-zA-Z]{10,}` | `xoxb-123456789-...` |
| Stripe Key | `sk_live_[0-9a-zA-Z]{24,}` | `sk_live_51H...` |
| Google API | `AIza[0-9A-Za-z-_]{35}` | `AIzaSyA...` |
| Private Key | `-----BEGIN.*PRIVATE KEY-----` | PEM format |
| Connection String | `(mongodb|postgres|mysql)://` | DB URLs |
| Generic API Key | `[aA]pi[_-]?[kK]ey.*['\"][a-zA-Z0-9]{16,}` | Various |

### Detection Tools

```bash
# Gitleaks - scan repository
gitleaks detect --source . --verbose
gitleaks detect --source . --report-format json --report-path leaks.json

# Git-secrets (AWS-focused)
git secrets --scan
git secrets --scan-history

# Trufflehog - deep history scan
trufflehog git file://. --json
trufflehog github --org=myorg --json

# Custom grep patterns
grep -rn "AKIA[0-9A-Z]{16}" --include="*.ts" --include="*.js" --include="*.env*"
grep -rn "-----BEGIN.*PRIVATE KEY" --include="*"
grep -rn "password\s*=\s*['\"][^'\"]\+" --include="*.ts"
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run gitleaks
if command -v gitleaks &> /dev/null; then
  gitleaks protect --staged --verbose
  if [ $? -ne 0 ]; then
    echo "Secrets detected! Commit blocked."
    exit 1
  fi
fi
```

---

## Environment Variables

### Secure .env Handling

```bash
# .env file structure
# Use descriptive names, never commit real values

# Database
DATABASE_URL=postgres://user:password@localhost:5432/myapp

# API Keys
STRIPE_SECRET_KEY=sk_test_...
SENDGRID_API_KEY=SG....

# JWT
JWT_SECRET=your-256-bit-secret-here
JWT_REFRESH_SECRET=your-other-256-bit-secret

# External Services  
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

### .gitignore Patterns

```gitignore
# Environment files
.env
.env.local
.env.*.local
.env.development
.env.production

# Never commit these
*.pem
*.key
*.crt
*.p12
*.pfx

# IDE secrets
.idea/
.vscode/*.json

# Local config
config/local.json
secrets/
```

### Validation

```typescript
import { z } from 'zod';

// Define required environment variables
const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  STRIPE_SECRET_KEY: z.string().startsWith('sk_'),
  AWS_ACCESS_KEY_ID: z.string().regex(/^AKIA[A-Z0-9]{16}$/),
  AWS_SECRET_ACCESS_KEY: z.string().length(40)
});

// Validate at startup
function validateEnv() {
  const result = envSchema.safeParse(process.env);
  
  if (!result.success) {
    console.error('Invalid environment configuration:');
    console.error(result.error.format());
    process.exit(1);
  }
  
  return result.data;
}

