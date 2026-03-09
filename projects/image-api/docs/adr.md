# Image Optimization API - Architecture Decision Record

**Date**: February 27, 2026
**Author**: CTO Vogels (Auto Company)
**Status**: Implemented

---

## Context

We need to build a self-hosted image optimization API as our next product. The key requirements are:

1. **Self-hosted first** - Avoid CDN infrastructure competition, target privacy/compliance market
2. **Memory efficient** - Critical for solo operation without dedicated ops team
3. **Simple deployment** - Docker one-command setup
4. **Python/FastAPI stack** - Leverage existing EmailGuard knowledge

## Decision

### Technology Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Image Processing** | libvips via pyvips | Best memory efficiency, streaming architecture, 2-3x faster than Pillow |
| **Web Framework** | FastAPI | Async, automatic OpenAPI docs, proven with EmailGuard |
| **Deployment** | Docker + docker-compose | One-command deployment, reproducible |
| **Caching** | Redis (optional) | Edge caching without external CDN |
| **Metrics** | Prometheus | Standard observability |

### Why libvips over Alternatives

| Library | Memory | Speed | Format Support | Decision |
|---------|--------|-------|----------------|----------|
| **libvips/pyvips** | Best (streaming) | Fastest | JPEG, PNG, WebP, AVIF, HEIC | ✅ Selected |
| Pillow | High (loads full image) | Medium | JPEG, PNG, WebP, GIF | ❌ Higher memory |
| Sharp | Low | Fast | Full support | ❌ Node.js stack |
| ImageMagick | Highest | Medium | All formats | ❌ Security concerns |

### API Design

```
POST /v1/optimize   - Full optimization with resize, compress, format convert
POST /v1/convert    - Format conversion only
POST /v1/resize     - Resize only
POST /v1/crop       - Crop only
GET  /v1/health     - Health check
GET  /v1/metrics    - Prometheus metrics
```

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT REQUEST                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI APPLICATION                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ENDPOINTS:                                          │   │
│  │  - /v1/optimize (resize + compress + convert)      │   │
│  │  - /v1/convert (format only)                       │   │
│  │  - /v1/resize (dimensions only)                    │   │
│  │  - /v1/crop (region selection)                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  VALIDATION:                                         │   │
│  │  - Magic bytes check                                │   │
│  │  - File size limit (20MB default)                   │   │
│  │  - Dimension limit (10,000 x 10,000)               │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  PROCESSOR (pyvips):                                │   │
│  │  - auto_orient() - EXIF rotation                    │   │
│  │  - crop() - Region selection                        │   │
│  │  - resize() - Scale with fit modes                  │   │
│  │  - compress() - Quality + format encode             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
┌───────────────────┐     ┌───────────────────────────┐
│   REDIS (optional)│     │   PROMETHEUS METRICS      │
│   - Cache results │     │   - Processing time       │
│   - TTL: 1-24h    │     │   - Compression ratio     │
│                   │     │   - Error rate            │
└───────────────────┘     └───────────────────────────┘
```

### Fit Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| `cover` | Fill area, crop overflow | Thumbnails, cards |
| `contain` | Fit within, preserve aspect | Galleries, previews |
| `fill` | Stretch to exact dimensions | Specific slot sizes |
| `inside` | Never exceed bounds | Maximum size limits |
| `outside` | Cover bounds, may exceed | Minimum size guarantees |

### Security Measures

1. **Input Validation**
   - Magic bytes verification (not just extension)
   - File size limits before loading
   - Dimension limits before processing

2. **Resource Protection**
   - Memory limits via pyvips cache
   - Request timeout (30s)
   - Max concurrent requests

3. **Format Handling**
   - JPEG: Progressive encoding, strip metadata
   - PNG: Max compression, strip metadata
   - WebP: Efficient encoding with quality control
   - Alpha to RGB: Composite onto white for JPEG output

## Consequences

### Positive
- Memory-efficient processing enables solo operation
- Simple API surface (4 operations) for easy adoption
- Docker deployment reduces ops burden
- Prometheus metrics provide observability out of the box

### Negative
- No CDN edge caching (self-hosted limitation)
- No AI features (smart crop, auto-tag) in MVP
- Single-node architecture (horizontal scaling requires work)

### Risks Mitigated
- Memory exhaustion → Strict limits, streaming
- DoS → Rate limiting (external), size limits
- Malicious images → Magic bytes validation

## Future Considerations

| Phase | Addition | Trigger |
|-------|----------|---------|
| Phase 2 | Async batch processing | >50 customers |
| Phase 2 | AI smart crop | Enterprise demand |
| Phase 3 | Multi-node support | Scale requirements |
| Phase 3 | AVIF output | Browser adoption |

---

**Document Version**: 1.0
**Last Updated**: February 27, 2026