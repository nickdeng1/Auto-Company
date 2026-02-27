"""
Dashboard authentication module.
Provides token-based authentication for the dashboard API.

Configuration:
    DASHBOARD_TOKEN: Environment variable for authentication token.
                     If not set, authentication is disabled (development mode).
    DASHBOARD_TOKEN_FILE: File path to read token from (alternative to env var).

Usage:
    from lib.auth import AuthMiddleware, check_auth, require_auth

    # In request handler:
    if not check_auth(self):
        self._json({"error": "Unauthorized"}, code=401)
        return
"""

import hashlib
import hmac
import os
import secrets
import time
from pathlib import Path
from typing import Optional, Tuple

# Default token file location
TOKEN_FILE = Path(__file__).resolve().parents[2] / ".dashboard-token"

# Token expiration (24 hours for persistent sessions)
TOKEN_EXPIRY_SECONDS = 24 * 60 * 60


def get_configured_token() -> Optional[str]:
    """
    Get the configured authentication token.

    Priority:
    1. DASHBOARD_TOKEN environment variable
    2. DASHBOARD_TOKEN_FILE environment variable (file path)
    3. .dashboard-token file in repo root
    4. None (authentication disabled)

    Returns:
        Token string or None if not configured
    """
    # Check environment variable first
    token = os.environ.get("DASHBOARD_TOKEN")
    if token:
        return token.strip()

    # Check token file from environment
    token_file_env = os.environ.get("DASHBOARD_TOKEN_FILE")
    if token_file_env:
        token_path = Path(token_file_env)
        if token_path.exists():
            return token_path.read_text(encoding="utf-8").strip()

    # Check default token file
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text(encoding="utf-8").strip()

    return None


def is_auth_enabled() -> bool:
    """Check if authentication is enabled."""
    return get_configured_token() is not None


def generate_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_hex(length)


def hash_token(token: str) -> str:
    """Hash a token for storage comparison."""
    return hashlib.sha256(token.encode()).hexdigest()


def create_session_token(secret: str, timestamp: Optional[int] = None) -> str:
    """
    Create a session token from the secret token.

    Format: hmac(timestamp:secret)
    """
    if timestamp is None:
        timestamp = int(time.time())

    msg = f"{timestamp}:{secret}".encode()
    return hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()


def verify_session_token(session_token: str, secret: str, max_age: int = TOKEN_EXPIRY_SECONDS) -> bool:
    """
    Verify a session token against the secret.

    Args:
        session_token: The session token to verify
        secret: The configured secret token
        max_age: Maximum age in seconds for the session

    Returns:
        True if valid, False otherwise
    """
    # Simple comparison for direct token auth
    if hmac.compare_digest(session_token, secret):
        return True

    # Session token format validation
    try:
        # For session tokens, we just compare directly
        expected = create_session_token(secret)
        return hmac.compare_digest(session_token, expected)
    except Exception:
        return False


def check_auth(handler) -> Tuple[bool, Optional[str]]:
    """
    Check authentication for a request handler.

    Checks in order:
    1. Authorization header (Bearer token)
    2. Cookie (dashboard_token)
    3. Query parameter (token)

    Args:
        handler: BaseHTTPRequestHandler instance

    Returns:
        Tuple of (is_authenticated, error_message)
    """
    secret = get_configured_token()

    # Auth not configured - allow all
    if not secret:
        return True, None

    # Check Authorization header
    auth_header = handler.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        if hmac.compare_digest(token, secret):
            return True, None

    # Check cookie
    cookie_header = handler.headers.get("Cookie", "")
    for cookie in cookie_header.split(";"):
        cookie = cookie.strip()
        if cookie.startswith("dashboard_token="):
            token = cookie[16:]
            if hmac.compare_digest(token, secret):
                return True, None

    # Check query parameter (from parsed URL)
    from urllib.parse import parse_qs, urlparse
    parsed = urlparse(handler.path)
    qs = parse_qs(parsed.query)
    if "token" in qs:
        token = qs["token"][0]
        if hmac.compare_digest(token, secret):
            return True, None

    return False, "Authentication required"


def require_auth(handler_func):
    """
    Decorator to require authentication for a handler method.

    Usage:
        @require_auth
        def do_GET(self):
            # Already authenticated
            ...
    """
    def wrapper(self, *args, **kwargs):
        is_authed, error = check_auth(self)
        if not is_authed:
            self._json({"error": error or "Unauthorized"}, code=401)
            return
        return handler_func(self, *args, **kwargs)
    return wrapper


class AuthMiddleware:
    """
    Authentication middleware for the dashboard.

    Usage:
        auth = AuthMiddleware()

        # In request handler:
        if not auth.check(request):
            return unauthorized_response()
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize auth middleware.

        Args:
            token: Optional token override. If not provided, uses get_configured_token()
        """
        self.token = token or get_configured_token()
        self.enabled = self.token is not None

    def check(self, handler) -> Tuple[bool, Optional[str]]:
        """Check authentication for a request."""
        if not self.enabled:
            return True, None
        return check_auth(handler)

    def generate_cookie_header(self, max_age: int = TOKEN_EXPIRY_SECONDS) -> str:
        """Generate Set-Cookie header value for authenticated session."""
        if not self.token:
            return ""
        return f"dashboard_token={self.token}; Path=/; Max-Age={max_age}; HttpOnly; SameSite=Strict"

    def get_auth_status(self) -> dict:
        """Get authentication status for API responses."""
        return {
            "enabled": self.enabled,
            "configured": self.token is not None,
        }


def init_token_file(force: bool = False) -> str:
    """
    Initialize the token file with a new random token.

    Args:
        force: Overwrite existing token file

    Returns:
        The generated token
    """
    if TOKEN_FILE.exists() and not force:
        return TOKEN_FILE.read_text(encoding="utf-8").strip()

    token = generate_token()
    TOKEN_FILE.write_text(token + "\n", encoding="utf-8")

    # Set restrictive permissions (owner read/write only)
    os.chmod(TOKEN_FILE, 0o600)

    return token


def get_token_for_display() -> str:
    """Get the current token for display (truncated for security)."""
    token = get_configured_token()
    if not token:
        return "(not configured)"
    if len(token) <= 16:
        return token[:4] + "..." + token[-4:]
    return token[:8] + "..." + token[-8:]