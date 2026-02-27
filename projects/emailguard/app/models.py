from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict
from enum import Enum


class ValidationReason(str, Enum):
    """Validation result reason"""
    VALID = "valid"
    INVALID_SYNTAX = "invalid_syntax"
    INVALID_DOMAIN = "invalid_domain"
    NO_MX_RECORD = "no_mx_record"
    DISPOSABLE = "disposable_email"
    ROLE_EMAIL = "role_email"


class EmailCheckResult(BaseModel):
    """Individual check results"""
    syntax: bool = Field(description="Syntax validation passed")
    mx: bool = Field(description="MX record exists")
    disposable: bool = Field(description="Is a disposable email")
    role: bool = Field(description="Is a role-based email")


class VerifyResponse(BaseModel):
    """Single email verification response"""
    email: str = Field(description="The email address verified")
    valid: bool = Field(description="Overall validity")
    reason: ValidationReason = Field(description="Reason for the result")
    checks: EmailCheckResult = Field(description="Individual check results")
    score: int = Field(ge=0, le=100, description="Quality score 0-100")
    suggestion: Optional[str] = Field(default=None, description="Suggested correction if applicable")


class VerifyRequest(BaseModel):
    """Single email verification request"""
    email: EmailStr = Field(description="Email address to verify")


class BatchVerifyRequest(BaseModel):
    """Batch verification request"""
    emails: List[EmailStr] = Field(
        description="List of email addresses to verify",
        max_length=1000
    )


class BatchVerifyResponse(BaseModel):
    """Batch verification response"""
    total: int = Field(description="Total emails processed")
    valid: int = Field(description="Valid emails count")
    invalid: int = Field(description="Invalid emails count")
    results: List[VerifyResponse] = Field(description="Individual results")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "ok"
    version: str
    uptime_seconds: float