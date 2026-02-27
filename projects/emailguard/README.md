# EmailGuard

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

**Self-hosted Email Validation API** - Validate emails without sending data to third parties

## ✨ Features

- 🔒 **Privacy-first** - No data leaves your server (GDPR compliant)
- ⚡ **Fast** - Syntax + DNS MX validation in <200ms
- 🐳 **Docker-ready** - Deploy in 30 seconds
- 📦 **RESTful API** - Simple HTTP endpoints with batch support
- 🔧 **Zero dependencies** - No external APIs for core validation

## 🚀 Quick Start

### Docker Deploy (Recommended)

```bash
# Clone and run
git clone https://github.com/nickdeng1/Auto-Company.git
cd Auto-Company/projects/emailguard
docker-compose up -d

# Test it
curl -X POST http://localhost:8000/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### Local Development

```bash
# Clone repository
git clone https://github.com/nickdeng1/Auto-Company.git
cd Auto-Company/projects/emailguard

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看 Swagger API 文档

## 💻 Code Examples

### Python

```python
import httpx

# Single validation
response = httpx.post(
    "http://localhost:8000/v1/verify",
    json={"email": "user@example.com"}
)
result = response.json()
print(f"Valid: {result['valid']}, Score: {result['score']}")

# Batch validation
emails = ["user1@gmail.com", "admin@company.com", "test@tempmail.com"]
response = httpx.post(
    "http://localhost:8000/v1/verify/batch",
    json={"emails": emails}
)
for r in response.json()["results"]:
    print(f"{r['email']}: {r['valid']} ({r['score']})")
```

### JavaScript / Node.js

```javascript
// Single validation
const response = await fetch('http://localhost:8000/v1/verify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com' })
});
const result = await response.json();
console.log(`Valid: ${result.valid}, Score: ${result.score}`);

// Batch validation
const emails = ['user1@gmail.com', 'admin@company.com'];
const batchResponse = await fetch('http://localhost:8000/v1/verify/batch', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ emails })
});
const { results } = await batchResponse.json();
results.forEach(r => console.log(`${r.email}: ${r.valid}`));
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

type VerifyRequest struct {
    Email string `json:"email"`
}

func main() {
    body, _ := json.Marshal(VerifyRequest{Email: "user@example.com"})
    resp, _ := http.Post(
        "http://localhost:8000/v1/verify",
        "application/json",
        bytes.NewBuffer(body),
    )
    defer resp.Body.Close()
    
    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)
    fmt.Printf("Valid: %v, Score: %v\n", result["valid"], result["score"])
}
```

## 📖 API Reference

### Validate Single Email

```bash
curl -X POST http://localhost:8000/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Response:**

```json
{
  "email": "user@example.com",
  "valid": true,
  "reason": "valid",
  "checks": {
    "syntax": true,
    "mx": true,
    "disposable": false,
    "role": false
  },
  "score": 95,
  "suggestion": null
}
```

### Batch Validation

```bash
curl -X POST http://localhost:8000/v1/verify/batch \
  -H "Content-Type: application/json" \
  -d '{"emails": ["user1@gmail.com", "admin@company.com", "test@tempmail.com"]}'
```

**Response:**

```json
{
  "results": [
    {
      "email": "user1@gmail.com",
      "valid": true,
      "score": 95,
      "checks": {"syntax": true, "mx": true, "disposable": false, "role": false}
    },
    {
      "email": "admin@company.com",
      "valid": true,
      "score": 85,
      "checks": {"syntax": true, "mx": true, "disposable": false, "role": true}
    },
    {
      "email": "test@tempmail.com",
      "valid": false,
      "score": 30,
      "checks": {"syntax": true, "mx": true, "disposable": true, "role": false}
    }
  ],
  "summary": {
    "total": 3,
    "valid": 2,
    "invalid": 1
  }
}
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/verify` | POST | Validate single email |
| `/v1/verify/batch` | POST | Batch validation (max 1000) |
| `/health` | GET | Health check |
| `/v1/disposable-domains` | GET | List blocked disposable domains |
| `/v1/role-prefixes` | GET | List role-based prefixes |

## 🔍 Validation Logic

| Check | Description | Score Impact |
|-------|-------------|--------------|
| Syntax | RFC 5322 format check | +40 |
| DNS MX | Domain MX record exists | +30 |
| Disposable | Temp email domain detection | +25 |
| Role-based | admin@, info@, etc. | +5 (if not role) |

**Score range**: 0-100, recommend 80+ for valid emails

## 🛠️ Configuration

Environment variables (prefix `EMAILGUARD_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `EMAILGUARD_DEBUG` | false | Debug mode |
| `EMAILGUARD_RATE_LIMIT_REQUESTS` | 100 | Rate limit requests |
| `EMAILGUARD_RATE_LIMIT_WINDOW` | 60 | Rate limit window (seconds) |
| `EMAILGUARD_DNS_TIMEOUT` | 5.0 | DNS query timeout (seconds) |
| `EMAILGUARD_MAX_BATCH_SIZE` | 1000 | Max batch size |

## 📦 Tech Stack

- **Python 3.11+** - Modern Python features
- **FastAPI** - High-performance async web framework
- **dnspython** - DNS lookup library
- **Pydantic** - Data validation
- **Docker** - Containerized deployment

## 🧪 Testing

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
python -m pytest tests/ --cov=app --cov-report=html
```

## 📄 License

MIT License - Free for commercial use

## 🤝 Contributing

Issues and PRs welcome!

---

**Built with ❤️ by [Auto Company](https://github.com/nickdeng1/Auto-Company)**