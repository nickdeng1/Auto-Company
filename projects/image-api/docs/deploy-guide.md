# Image API Deployment Guide

## Quick Deploy Options

### Option 1: Railway (Recommended)

Railway provides the simplest Docker deployment with automatic HTTPS.

#### Prerequisites
- Railway account (free tier available)
- GitHub repository connected

#### Steps

1. **Connect GitHub Repo**
   ```bash
   # Go to railway.app
   # Click "New Project" → "Deploy from GitHub repo"
   # Select: nickdeng1/Auto-Company
   ```

2. **Configure Service**
   - Root Directory: `projects/image-api`
   - Builder: Dockerfile
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   ```
   MAX_FILE_SIZE_MB=20
   MAX_MEMORY_PER_REQUEST_MB=100
   RATE_LIMIT_PER_MINUTE=100
   ```

4. **Deploy**
   - Railway auto-deploys on push to main
   - Health check: `/v1/health`

#### Using Railway CLI (Alternative)
```bash
# Install CLI
npm install -g @railway/cli

# Login (requires browser)
railway login

# Deploy
cd projects/image-api
railway up
```

### Option 2: Render

1. Create new Web Service on render.com
2. Connect GitHub repo
3. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set environment variables

### Option 3: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
cd projects/image-api
fly launch
fly deploy
```

### Option 4: Docker Hub + Any Platform

```bash
# Build and push
docker build -t your-username/image-api:latest .
docker push your-username/image-api:latest

# Deploy anywhere that supports Docker
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_FILE_SIZE_MB` | 20 | Maximum upload file size |
| `MAX_MEMORY_PER_REQUEST_MB` | 100 | Memory limit per request |
| `RATE_LIMIT_PER_MINUTE` | 100 | Requests per minute per IP |
| `REDIS_URL` | - | Redis connection URL (optional) |

## Health Check

All platforms should use:
- **Path**: `/v1/health`
- **Expected Response**: `{"status": "ok", "version": "0.1.0"}`

## Post-Deployment Verification

```bash
# Health check
curl https://your-domain.com/v1/health

# Test optimize endpoint
curl -X POST https://your-domain.com/v1/optimize \
  -F "image=@test.jpg" \
  -o optimized.jpg

# Check metrics
curl https://your-domain.com/v1/metrics
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: slowapi**
   - Solution: Ensure `requirements.txt` includes `slowapi>=0.1.9`

2. **pyvips not found**
   - Solution: Pillow fallback is automatic, no action needed

3. **Port binding error**
   - Solution: Use `$PORT` environment variable (required by most platforms)

4. **Memory limit exceeded**
   - Solution: Reduce `MAX_FILE_SIZE_MB` or `MAX_MEMORY_PER_REQUEST_MB`

## Cost Estimates

| Platform | Free Tier | Paid Tier |
|----------|-----------|-----------|
| Railway | $5 credit/month | $0.000463/GB-hour |
| Render | 750 hours/month | $7/month starter |
| Fly.io | 3 VMs, 3GB | $1.94/GB-month |

## Recommended Configuration

For production use:
- **Memory**: 512MB minimum
- **CPU**: 0.5 vCPU minimum
- **Instances**: 2 for high availability
- **Redis**: Add for caching (optional)