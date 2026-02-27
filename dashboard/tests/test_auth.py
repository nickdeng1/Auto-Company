#!/usr/bin/env python3
"""
Tests for dashboard authentication module.
Run with: python3 -m pytest dashboard/tests/test_auth.py -v
Or: python3 dashboard/tests/test_auth.py
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add dashboard to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.auth import (
    get_configured_token,
    is_auth_enabled,
    generate_token,
    hash_token,
    check_auth,
    AuthMiddleware,
    init_token_file,
    get_token_for_display,
)


class TestTokenConfiguration(unittest.TestCase):
    """Test token configuration retrieval."""

    def test_no_token_configured(self):
        """Test when no token is configured."""
        with patch.dict(os.environ, {}, clear=True):
            with tempfile.TemporaryDirectory() as tmpdir:
                with patch('lib.auth.TOKEN_FILE', Path(tmpdir) / '.dashboard-token'):
                    token = get_configured_token()
                    self.assertIsNone(token)
                    self.assertFalse(is_auth_enabled())

    def test_token_from_environment(self):
        """Test token from DASHBOARD_TOKEN environment variable."""
        with patch.dict(os.environ, {'DASHBOARD_TOKEN': 'test-secret-token'}):
            with tempfile.TemporaryDirectory() as tmpdir:
                with patch('lib.auth.TOKEN_FILE', Path(tmpdir) / '.dashboard-token'):
                    token = get_configured_token()
                    self.assertEqual(token, 'test-secret-token')
                    self.assertTrue(is_auth_enabled())

    def test_token_from_file(self):
        """Test token from file."""
        with patch.dict(os.environ, {}, clear=True):
            with tempfile.TemporaryDirectory() as tmpdir:
                token_file = Path(tmpdir) / '.dashboard-token'
                token_file.write_text('file-secret-token\n')
                with patch('lib.auth.TOKEN_FILE', token_file):
                    token = get_configured_token()
                    self.assertEqual(token, 'file-secret-token')
                    self.assertTrue(is_auth_enabled())

    def test_env_takes_priority_over_file(self):
        """Test that environment variable takes priority over file."""
        with patch.dict(os.environ, {'DASHBOARD_TOKEN': 'env-token'}):
            with tempfile.TemporaryDirectory() as tmpdir:
                token_file = Path(tmpdir) / '.dashboard-token'
                token_file.write_text('file-token\n')
                with patch('lib.auth.TOKEN_FILE', token_file):
                    token = get_configured_token()
                    self.assertEqual(token, 'env-token')


class TestTokenGeneration(unittest.TestCase):
    """Test token generation and hashing."""

    def test_generate_token_default_length(self):
        """Test default token length (64 hex chars)."""
        token = generate_token()
        self.assertEqual(len(token), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in token))

    def test_generate_token_custom_length(self):
        """Test custom token length."""
        token = generate_token(16)
        self.assertEqual(len(token), 32)  # 16 bytes = 32 hex chars

    def test_generate_token_uniqueness(self):
        """Test that generated tokens are unique."""
        tokens = {generate_token() for _ in range(100)}
        self.assertEqual(len(tokens), 100)

    def test_hash_token_consistency(self):
        """Test that hash is consistent."""
        token = "test-token"
        hash1 = hash_token(token)
        hash2 = hash_token(token)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA-256


class TestCheckAuth(unittest.TestCase):
    """Test authentication checking."""

    def test_auth_disabled_allows_all(self):
        """Test that disabled auth allows all requests."""
        handler = MagicMock()
        handler.headers = {}
        handler.path = "/api/status"

        with patch('lib.auth.get_configured_token', return_value=None):
            is_authed, error = check_auth(handler)
            self.assertTrue(is_authed)
            self.assertIsNone(error)

    def test_auth_via_bearer_header(self):
        """Test authentication via Bearer header."""
        handler = MagicMock()
        handler.headers = {"Authorization": "Bearer my-secret-token"}
        handler.path = "/api/status"

        with patch('lib.auth.get_configured_token', return_value='my-secret-token'):
            is_authed, error = check_auth(handler)
            self.assertTrue(is_authed)

    def test_auth_via_cookie(self):
        """Test authentication via cookie."""
        handler = MagicMock()
        handler.headers = {"Cookie": "dashboard_token=my-secret-token; other=cookie"}
        handler.path = "/api/status"

        with patch('lib.auth.get_configured_token', return_value='my-secret-token'):
            is_authed, error = check_auth(handler)
            self.assertTrue(is_authed)

    def test_auth_failure(self):
        """Test authentication failure."""
        handler = MagicMock()
        handler.headers = {"Authorization": "Bearer wrong-token"}
        handler.path = "/api/status"

        with patch('lib.auth.get_configured_token', return_value='correct-token'):
            is_authed, error = check_auth(handler)
            self.assertFalse(is_authed)
            self.assertEqual(error, "Authentication required")


class TestAuthMiddleware(unittest.TestCase):
    """Test AuthMiddleware class."""

    def test_middleware_disabled(self):
        """Test middleware when auth is disabled."""
        middleware = AuthMiddleware(token=None)
        self.assertFalse(middleware.enabled)
        self.assertTrue(middleware.check(MagicMock())[0])

    def test_middleware_enabled(self):
        """Test middleware when auth is enabled."""
        middleware = AuthMiddleware(token='secret')
        self.assertTrue(middleware.enabled)

        handler = MagicMock()
        handler.headers = {}
        handler.path = "/api/status"

        # When middleware is enabled with token, but get_configured_token returns None,
        # check_auth will allow access. This tests the middleware state, not auth logic.
        with patch('lib.auth.get_configured_token', return_value=None):
            is_authed, _ = middleware.check(handler)
            # Auth disabled when no configured token
            self.assertTrue(is_authed)

    def test_middleware_enabled_with_token(self):
        """Test middleware blocks unauthenticated requests when token configured."""
        middleware = AuthMiddleware(token='secret')

        handler = MagicMock()
        handler.headers = {}  # No auth headers
        handler.path = "/api/status"

        with patch('lib.auth.get_configured_token', return_value='secret'):
            is_authed, error = middleware.check(handler)
            self.assertFalse(is_authed)
            self.assertEqual(error, "Authentication required")

    def test_auth_status(self):
        """Test auth status response."""
        middleware = AuthMiddleware(token='secret')
        status = middleware.get_auth_status()
        self.assertTrue(status['enabled'])
        self.assertTrue(status['configured'])


class TestInitTokenFile(unittest.TestCase):
    """Test token file initialization."""

    def test_init_creates_file(self):
        """Test that init creates token file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            token_file = Path(tmpdir) / '.dashboard-token'
            with patch('lib.auth.TOKEN_FILE', token_file):
                token = init_token_file()
                self.assertTrue(token_file.exists())
                self.assertEqual(token_file.read_text().strip(), token)

    def test_init_force_overwrites(self):
        """Test that force=True overwrites existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            token_file = Path(tmpdir) / '.dashboard-token'
            token_file.write_text('old-token\n')
            with patch('lib.auth.TOKEN_FILE', token_file):
                new_token = init_token_file(force=True)
                self.assertNotEqual(token_file.read_text().strip(), 'old-token')
                self.assertEqual(token_file.read_text().strip(), new_token)

    def test_init_no_force_preserves(self):
        """Test that force=False preserves existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            token_file = Path(tmpdir) / '.dashboard-token'
            token_file.write_text('existing-token\n')
            with patch('lib.auth.TOKEN_FILE', token_file):
                token = init_token_file(force=False)
                self.assertEqual(token, 'existing-token')


class TestTokenDisplay(unittest.TestCase):
    """Test token display formatting."""

    def test_display_not_configured(self):
        """Test display when no token configured."""
        with patch('lib.auth.get_configured_token', return_value=None):
            display = get_token_for_display()
            self.assertEqual(display, "(not configured)")

    def test_display_short_token(self):
        """Test display of short token."""
        with patch('lib.auth.get_configured_token', return_value='short'):
            display = get_token_for_display()
            self.assertEqual(display, "shor...hort")

    def test_display_long_token(self):
        """Test display of long token (truncated)."""
        with patch('lib.auth.get_configured_token', return_value='a' * 64):
            display = get_token_for_display()
            self.assertTrue('...' in display)
            self.assertTrue(len(display) < 70)


if __name__ == '__main__':
    unittest.main(verbosity=2)