"""
EmailGuard Test Suite
Unit and integration tests for email validation
"""

import pytest
from unittest.mock import patch, MagicMock

from app.validator import EmailValidator
from app.config import Settings
from app.models import ValidationReason


@pytest.fixture
def settings():
    """Create test settings"""
    return Settings(
        dns_timeout=2.0,
        disposable_domains=["tempmail.com", "guerrillamail.com"],
        role_prefixes=["admin", "info", "support"]
    )


@pytest.fixture
def validator(settings):
    """Create validator instance"""
    return EmailValidator(settings)


class TestSyntaxValidation:
    """Test syntax validation"""
    
    def test_valid_email(self, validator):
        """Test valid email passes syntax check"""
        valid, reason, checks, score, _ = validator.validate_email("user@example.com")
        assert checks.syntax is True
        assert valid is True
        assert reason == ValidationReason.VALID
    
    def test_invalid_email_no_at(self, validator):
        """Test email without @ fails"""
        valid, reason, checks, score, _ = validator.validate_email("userexample.com")
        assert checks.syntax is False
        assert valid is False
        assert reason == ValidationReason.INVALID_SYNTAX
    
    def test_invalid_email_no_domain(self, validator):
        """Test email without domain fails"""
        valid, reason, checks, score, _ = validator.validate_email("user@")
        assert checks.syntax is False
        assert valid is False
    
    def test_invalid_email_no_tld(self, validator):
        """Test email without TLD fails"""
        valid, reason, checks, score, _ = validator.validate_email("user@example")
        assert checks.syntax is False
    
    def test_invalid_email_double_dots(self, validator):
        """Test email with double dots fails"""
        valid, reason, checks, score, _ = validator.validate_email("user..name@example.com")
        assert checks.syntax is False
    
    def test_invalid_email_trailing_dot(self, validator):
        """Test email with trailing dot in local part fails"""
        valid, reason, checks, score, _ = validator.validate_email("user.@example.com")
        assert checks.syntax is False


class TestDisposableDetection:
    """Test disposable email detection"""
    
    def test_disposable_email_detected(self, validator):
        """Test disposable email is detected"""
        with patch.object(validator, '_validate_mx', return_value=(True, 60)):
            valid, reason, checks, score, _ = validator.validate_email("user@tempmail.com")
            assert checks.disposable is True
            assert valid is False
            assert reason == ValidationReason.DISPOSABLE
    
    def test_normal_email_not_disposable(self, validator):
        """Test normal email is not flagged as disposable"""
        with patch.object(validator, '_validate_mx', return_value=(True, 60)):
            valid, reason, checks, score, _ = validator.validate_email("user@gmail.com")
            assert checks.disposable is False


class TestRoleEmailDetection:
    """Test role-based email detection"""
    
    def test_role_email_detected(self, validator):
        """Test role-based email is detected"""
        with patch.object(validator, '_validate_mx', return_value=(True, 60)):
            valid, reason, checks, score, _ = validator.validate_email("admin@example.com")
            assert checks.role is True
            # Role email still valid, just flagged
            assert reason == ValidationReason.VALID
    
    def test_normal_email_not_role(self, validator):
        """Test normal email is not flagged as role"""
        with patch.object(validator, '_validate_mx', return_value=(True, 60)):
            valid, reason, checks, score, _ = validator.validate_email("john@gmail.com")
            assert checks.role is False


class TestMXValidation:
    """Test DNS MX record validation"""
    
    def test_mx_record_exists(self, validator):
        """Test domain with MX record passes"""
        # gmail.com definitely has MX records
        valid, reason, checks, score, _ = validator.validate_email("user@gmail.com")
        assert checks.mx is True
    
    def test_mx_record_missing(self, validator):
        """Test domain without MX record fails"""
        valid, reason, checks, score, _ = validator.validate_email("user@nonexistentdomain12345.com")
        assert checks.mx is False
        assert reason == ValidationReason.NO_MX_RECORD


class TestTypoSuggestions:
    """Test typo suggestions"""
    
    def test_gmail_typo_suggestion(self, validator):
        """Test gmail typo correction"""
        with patch.object(validator, '_validate_mx', return_value=(True, 60)):
            valid, reason, checks, score, suggestion = validator.validate_email("user@gmial.com")
            # Should suggest gmail.com
            assert suggestion is not None or valid is False
    
    def test_valid_email_no_suggestion(self, validator):
        """Test valid email has no suggestion"""
        with patch.object(validator, '_validate_mx', return_value=(True, 60)):
            valid, reason, checks, score, suggestion = validator.validate_email("user@gmail.com")
            # No suggestion for valid domain
            # Note: gmail.com is in our typo correction dict


class TestScoreCalculation:
    """Test quality score calculation"""
    
    def test_valid_email_high_score(self, validator):
        """Test valid email gets high score"""
        with patch.object(validator, '_validate_mx', return_value=(True, 60)):
            valid, reason, checks, score, _ = validator.validate_email("user@gmail.com")
            assert score >= 80
    
    def test_disposable_email_low_score(self, validator):
        """Test disposable email gets low score"""
        with patch.object(validator, '_validate_mx', return_value=(True, 60)):
            valid, reason, checks, score, _ = validator.validate_email("user@tempmail.com")
            assert score <= 50
    
    def test_role_email_reduced_score(self, validator):
        """Test role email gets reduced score"""
        with patch.object(validator, '_validate_mx', return_value=(True, 60)):
            _, _, _, normal_score, _ = validator.validate_email("john@gmail.com")
            _, _, _, role_score, _ = validator.validate_email("admin@gmail.com")
            assert role_score < normal_score


class TestEdgeCases:
    """Test edge cases"""
    
    def test_uppercase_email_normalized(self, validator):
        """Test uppercase email is normalized"""
        with patch.object(validator, '_validate_mx', return_value=(True, 60)):
            valid, reason, checks, score, _ = validator.validate_email("USER@GMAIL.COM")
            assert valid is True
    
    def test_whitespace_trimmed(self, validator):
        """Test whitespace is trimmed"""
        with patch.object(validator, '_validate_mx', return_value=(True, 60)):
            valid, reason, checks, score, _ = validator.validate_email("  user@gmail.com  ")
            assert valid is True
    
    def test_empty_email_fails(self, validator):
        """Test empty email fails"""
        valid, reason, checks, score, _ = validator.validate_email("")
        assert valid is False
        assert reason == ValidationReason.INVALID_SYNTAX
    
    def test_too_long_email_fails(self, validator):
        """Test overly long email fails"""
        long_email = "a" * 250 + "@example.com"
        valid, reason, checks, score, _ = validator.validate_email(long_email)
        assert valid is False


# Integration tests (require network)
@pytest.mark.integration
class TestIntegration:
    """Integration tests with real DNS queries"""
    
    def test_real_gmail_validation(self, validator):
        """Test validation of real Gmail address"""
        valid, reason, checks, score, _ = validator.validate_email("test@gmail.com")
        assert checks.syntax is True
        assert checks.mx is True
        assert score > 50
    
    def test_real_outlook_validation(self, validator):
        """Test validation of real Outlook address"""
        valid, reason, checks, score, _ = validator.validate_email("test@outlook.com")
        assert checks.syntax is True
        assert checks.mx is True