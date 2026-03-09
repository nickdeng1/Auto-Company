# Image Optimization API

Self-hosted image optimization API with excellent performance and memory efficiency.

## Features

- **Resize**: Scale images to specific dimensions with fit modes (cover, contain, fill)
- **Compress**: Reduce file size with quality control
- **Convert**: Transform between JPEG, PNG, WebP formats
- **Crop**: Basic and smart cropping
- **Memory Efficient**: Uses libvips streaming architecture (with Pillow fallback)
- **Prometheus Metrics**: Built-in observability
- **Rate Limiting**: IP-based rate limiting to prevent abuse

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Docker

```bash
# Build
docker build -t image-api .

# Run
docker run -p 8000:8000 image-api

# Or with docker-compose (includes Redis)
docker-compose up -d
```

## Deployment

### Railway

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Deploy: `railway up`

Or connect your GitHub repo to Railway for automatic deployments.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_PER_MINUTE` | 100 | Max requests per minute per IP |
| `MAX_FILE_SIZE_MB` | 20 | Maximum upload file size |
| `PORT` | 8000 | Server port |

## API Endpoints

### POST /v1/optimize
Optimize an image with multiple operations.

**Request** (multipart/form-data):
- `image`: Image file (required)
- `width`: Target width (optional)
- `height`: Target height (optional)
- `quality`: Quality 1-100 (default: 85)
- `format`: Output format - jpeg/png/webp (optional)
- `fit`: Fit mode - cover/contain/fill (default: cover)

**Response**: Optimized image binary with metadata headers

### POST /v1/convert
Convert image to another format.

**Request** (multipart/form-data):
- `image`: Image file (required)
- `format`: Target format - jpeg/png/webp (required)
- `quality`: Quality 1-100 (default: 85)

### GET /v1/health
Health check endpoint.

### GET /v1/metrics
Prometheus metrics.

## Limits

- Max file size: 20MB
- Max dimensions: 10,000 x 10,000 pixels
- Rate limit: 100 requests/minute/IP (configurable)
- Supported formats: JPEG, PNG, WebP

## License

MIT