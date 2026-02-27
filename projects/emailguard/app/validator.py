"""
EmailGuard Validator Engine
Core email validation logic with multiple verification methods
"""

import re
import dns.resolver
from typing import Tuple, Optional
from functools import lru_cache

from app.config import Settings
from app.models import ValidationReason, EmailCheckResult


class EmailValidator:
    """
    Email validation engine with multiple verification methods:
    - Syntax validation (RFC 5322)
    - DNS MX record validation
    - Disposable email detection
    - Role-based email detection
    """
    
    # RFC 5322 compliant email regex (simplified but practical)
    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    
    # Common typo corrections
    DOMAIN_CORRECTIONS = {
        "gmail.co": "gmail.com",
        "gmail.cm": "gmail.com",
        "gmail.cmo": "gmail.com",
        "gmial.com": "gmail.com",
        "gmal.com": "gmail.com",
        "gmail.comm": "gmail.com",
        "yahoo.co": "yahoo.com",
        "yahoo.cm": "yahoo.com",
        "yaho.com": "yahoo.com",
        "hotmail.co": "hotmail.com",
        "hotmal.com": "hotmail.com",
        "outlook.co": "outlook.com",
        "outloo.com": "outlook.com",
    }
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._dns_resolver = dns.resolver.Resolver()
        self._dns_resolver.timeout = settings.dns_timeout
        self._dns_resolver.lifetime = settings.dns_timeout
    
    def validate_email(self, email: str) -> Tuple[bool, ValidationReason, EmailCheckResult, int, Optional[str]]:
        """
        Validate an email address through multiple checks.
        
        Returns:
            Tuple of (is_valid, reason, check_results, score, suggestion)
        """
        email = email.lower().strip()
        
        # Initialize check results
        checks = EmailCheckResult(
            syntax=False,
            mx=False,
            disposable=False,
            role=False
        )
        
        score = 0
        suggestion = None
        
        # Step 1: Syntax validation
        syntax_valid, syntax_score = self._validate_syntax(email)
        checks.syntax = syntax_valid
        
        if not syntax_valid:
            return False, ValidationReason.INVALID_SYNTAX, checks, syntax_score, None
        
        score += syntax_score
        
        # Extract domain
        local_part, domain = email.split("@", 1)
        
        # Check for domain typos
        if domain in self.DOMAIN_CORRECTIONS:
            suggestion = email.replace(domain, self.DOMAIN_CORRECTIONS[domain])
        
        # Step 2: Check for disposable email
        is_disposable = self._is_disposable(domain)
        checks.disposable = is_disposable
        
        if is_disposable:
            score -= 50
            # Still continue with other checks
        
        # Step 3: Check for role-based email
        is_role = self._is_role_email(local_part)
        checks.role = is_role
        
        if is_role:
            score -= 20
        
        # Step 4: DNS MX validation
        mx_valid, mx_score = self._validate_mx(domain)
        checks.mx = mx_valid
        
        if not mx_valid:
            score += mx_score
            return False, ValidationReason.NO_MX_RECORD, checks, max(0, score), suggestion
        
        score += mx_score
        
        # Calculate final result
        score = max(0, min(100, score))
        
        # Determine validity
        if is_disposable:
            return False, ValidationReason.DISPOSABLE, checks, score, suggestion
        
        valid = score >= 50
        reason = ValidationReason.VALID if valid else ValidationReason.INVALID_DOMAIN
        
        return valid, reason, checks, score, suggestion
    
    def _validate_syntax(self, email: str) -> Tuple[bool, int]:
        """
        Validate email syntax.
        
        Returns:
            Tuple of (is_valid, score_contribution)
        """
        if not email or len(email) > 254:
            return False, 0
        
        if not self.EMAIL_REGEX.match(email):
            return False, 0
        
        # Check for consecutive dots
        if ".." in email:
            return False, 0
        
        local, domain = email.rsplit("@", 1)
        
        # Local part checks
        if local.startswith(".") or local.endswith("."):
            return False, 0
        
        # Domain checks
        if domain.startswith("-") or domain.endswith("-"):
            return False, 0
        
        if domain.startswith(".") or domain.endswith("."):
            return False, 0
        
        return True, 40
    
    def _validate_mx(self, domain: str) -> Tuple[bool, int]:
        """
        Validate MX record exists for domain.
        
        Returns:
            Tuple of (has_mx, score_contribution)
        """
        try:
            # Try MX records first
            mx_records = self._dns_resolver.resolve(domain, "MX")
            if mx_records:
                return True, 60
            
            # Fallback to A record (some domains accept email without MX)
            a_records = self._dns_resolver.resolve(domain, "A")
            if a_records:
                return True, 50
            
            return False, 0
            
        except dns.resolver.NXDOMAIN:
            return False, 0
        except dns.resolver.NoAnswer:
            # No MX record, check for A record
            try:
                self._dns_resolver.resolve(domain, "A")
                return True, 50
            except:
                return False, 0
        except (dns.resolver.Timeout, dns.exception.DNSException):
            # DNS timeout - give benefit of doubt but lower score
            return True, 30
        except Exception:
            return False, 0
    
    def _is_disposable(self, domain: str) -> bool:
        """Check if domain is a known disposable email provider"""
        return domain in self.settings.disposable_domains
    
    def _is_role_email(self, local_part: str) -> bool:
        """Check if email is a role-based address"""
        return local_part in self.settings.role_prefixes


# Utility function for quick validation
def validate_email_quick(email: str, settings: Optional[Settings] = None) -> Tuple[bool, str]:
    """
    Quick validation for use without full app context.
    
    Returns:
        Tuple of (is_valid, reason)
    """
    if settings is None:
        settings = Settings()
    
    validator = EmailValidator(settings)
    valid, reason, _, _, _ = validator.validate_email(email)
    return valid, reason.value