# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-27

### Added
- Initial MVP release
- Core email validation engine with 4 check types:
  - Syntax validation (RFC 5322 compliant)
  - DNS MX record verification
  - Disposable email detection
  - Role-based email detection
- RESTful API endpoints:
  - `POST /v1/verify` - Single email verification
  - `POST /v1/verify/batch` - Batch verification (up to 1000 emails)
  - `GET /health` - Health check endpoint
  - `GET /v1/disposable-domains` - List disposable domains
  - `GET /v1/role-prefixes` - List role prefixes
- Scoring system (0-100) for email quality assessment
- Typo suggestions for common misspellings (gmail.com, outlook.com, etc.)
- Docker support with Dockerfile and docker-compose
- Configuration via environment variables
- Comprehensive test suite (23 tests)
- OpenAPI/Swagger documentation auto-generated

### Technical Details
- Built with Python 3.11+ and FastAPI
- Uses dnspython for DNS queries
- Pydantic for data validation
- Fully async-ready architecture

---

## Roadmap

### [0.2.0] - Planned
- SMTP mailbox verification
- Extended disposable domain database
- Rate limiting middleware
- Redis caching layer

### [0.3.0] - Planned  
- Web dashboard UI
- API key authentication
- Usage analytics
- Email webhook notifications

### [1.0.0] - Future
- Cluster deployment support
- Enterprise features (SSO, audit logs)
- Official SDKs (Python, JavaScript, Go)