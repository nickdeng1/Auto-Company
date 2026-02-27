"""
EmailGuard API Routes
FastAPI endpoints for email validation
"""

import time
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from app.models import (
    VerifyRequest, VerifyResponse,
    BatchVerifyRequest, BatchVerifyResponse,
    HealthResponse, EmailCheckResult, ValidationReason
)
from app.validator import EmailValidator
from app.config import Settings

router = APIRouter()

# Global start time for health check
START_TIME = time.time()


def get_settings() -> Settings:
    """Dependency to get settings"""
    return Settings()


def get_validator(settings: Settings = Depends(get_settings)) -> EmailValidator:
    """Dependency to get validator instance"""
    return EmailValidator(settings)


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.
    Returns service status and uptime.
    """
    return HealthResponse(
        status="ok",
        version="0.1.0",
        uptime_seconds=time.time() - START_TIME
    )


@router.post("/v1/verify", response_model=VerifyResponse, tags=["Validation"])
async def verify_email(
    request: VerifyRequest,
    validator: EmailValidator = Depends(get_validator)
):
    """
    Verify a single email address.
    
    Performs multiple validation checks:
    - Syntax validation (RFC 5322)
    - DNS MX record validation
    - Disposable email detection
    - Role-based email detection
    
    Returns detailed results including:
    - Overall validity
    - Individual check results
    - Quality score (0-100)
    - Suggestion for typo corrections
    """
    email = request.email.lower().strip()
    
    valid, reason, checks, score, suggestion = validator.validate_email(email)
    
    return VerifyResponse(
        email=email,
        valid=valid,
        reason=reason,
        checks=checks,
        score=score,
        suggestion=suggestion
    )


@router.post("/v1/verify/batch", response_model=BatchVerifyResponse, tags=["Validation"])
async def verify_batch(
    request: BatchVerifyRequest,
    validator: EmailValidator = Depends(get_validator)
):
    """
    Verify multiple email addresses in a single request.
    
    Maximum 1000 emails per batch.
    
    Returns:
    - Total count
    - Valid/invalid counts
    - Individual results for each email
    """
    if len(request.emails) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Maximum batch size is 1000 emails"
        )
    
    results: List[VerifyResponse] = []
    valid_count = 0
    
    for email in request.emails:
        email = email.lower().strip()
        valid, reason, checks, score, suggestion = validator.validate_email(email)
        
        results.append(VerifyResponse(
            email=email,
            valid=valid,
            reason=reason,
            checks=checks,
            score=score,
            suggestion=suggestion
        ))
        
        if valid:
            valid_count += 1
    
    return BatchVerifyResponse(
        total=len(results),
        valid=valid_count,
        invalid=len(results) - valid_count,
        results=results
    )


@router.get("/v1/disposable-domains", tags=["Data"])
async def list_disposable_domains(
    settings: Settings = Depends(get_settings)
):
    """
    List all known disposable email domains.
    
    Useful for client-side validation.
    """
    return {
        "domains": settings.disposable_domains,
        "count": len(settings.disposable_domains)
    }


@router.get("/v1/role-prefixes", tags=["Data"])
async def list_role_prefixes(
    settings: Settings = Depends(get_settings)
):
    """
    List all known role-based email prefixes.
    
    Useful for client-side validation.
    """
    return {
        "prefixes": settings.role_prefixes,
        "count": len(settings.role_prefixes)
    }