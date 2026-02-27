"""
EmailGuard - Self-hosted email validation service
Main FastAPI application
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.routes import router
from app.config import Settings


def create_app(settings: Settings = None) -> FastAPI:
    """Create and configure FastAPI application"""
    
    if settings is None:
        settings = Settings()
    
    app = FastAPI(
        title=settings.app_name,
        description="""
## EmailGuard API

Self-hosted email validation service for developers.

### Features

- 🔒 **Privacy-first**: Self-host, control your data
- ⚡ **Fast**: <200ms validation response
- 🎯 **Accurate**: Multi-layer validation (syntax, DNS MX, disposable detection)
- 🐳 **Easy deploy**: Docker-ready

### Validation Methods

1. **Syntax validation** - RFC 5322 compliant
2. **DNS MX validation** - Check domain mail exchange records
3. **Disposable email detection** - Block temporary email services
4. **Role email detection** - Identify admin@, info@ etc.

### Quick Start

```bash
# Docker
docker run -p 8000:8000 emailguard/emailguard:latest

# Verify email
curl -X POST http://localhost:8000/v1/verify \\
  -H "Content-Type: application/json" \\
  -d '{"email": "user@example.com"}'
```
        """,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(router)
    
    # Exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "detail": exc.errors(),
                "body": exc.body
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": str(exc) if settings.debug else "An unexpected error occurred"
            }
        )
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API info"""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health"
        }
    
    return app


# Create default app instance
app = create_app()