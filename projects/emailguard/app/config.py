from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Server
    app_name: str = "EmailGuard"
    app_version: str = "0.1.0"
    debug: bool = False

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Validation settings
    dns_timeout: float = 5.0
    max_batch_size: int = 1000

    # Disposable email domains (built-in list)
    disposable_domains: List[str] = [
        "tempmail.com", "guerrillamail.com", "10minutemail.com",
        "mailinator.com", "throwaway.email", "temp-mail.org",
        "fakeinbox.com", "sharklasers.com", "grr.la", "pokemail.net",
        "spam4.me", "gustr.com", "getairmail.com", "dropmail.me",
    ]

    # Role-based email prefixes
    role_prefixes: List[str] = [
        "admin", "administrator", "info", "support", "sales",
        "contact", "help", "webmaster", "postmaster", "hostmaster",
        "abuse", "noc", "security", "marketing", "pr", "press",
        "billing", "orders", "root", "system", "mail", "office",
    ]

    class Config:
        env_prefix = "EMAILGUARD_"
