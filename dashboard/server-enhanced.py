#!/usr/bin/env python3
"""
Auto Company Dashboard Server - Enhanced Edition (Refactored)
==============================================================
Web-based monitoring and control panel for Auto Company loop.

Features:
- Real-time status monitoring
- Log tail viewing with cycle selection
- Consensus file preview
- Start/Stop controls
- File browser (docs, projects)
- Cycle history viewer
- Prometheus metrics endpoint
- Real-time progress tracking
- Token-based authentication (optional)

Authentication:
    Set DASHBOARD_TOKEN environment variable or create .dashboard-token file
    to enable authentication. Without token, dashboard runs in open mode.

Usage:
    python3 dashboard/server-enhanced.py --port 8787
    DASHBOARD_TOKEN=secret python3 dashboard/server-enhanced.py --port 8787
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse, unquote

# Import from lib modules
from lib.utils import read_text_file, read_tail, read_activities, get_agent_stats
from lib.status import (
    REPO_ROOT, CONSENSUS_FILE, ACTIVITIES_FILE,
    QWEN_LOG_FILE, OPENCODE_LOG_FILE, CODEX_LOG_FILE,
    QWEN_JSONL_FILE, OPENCODE_JSONL_FILE, CODEX_JSONL_FILE,
    gather_status, start_loop, stop_loop, find_cycle_logs, browse_directory,
    BROWSE_DIRS,
)
from lib.metrics import format_prometheus_metrics
from lib.auth import (
    check_auth, is_auth_enabled, get_configured_token,
    AuthMiddleware, init_token_file, TOKEN_FILE,
)

DASHBOARD_DIR = Path(__file__).resolve().parent


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the enhanced dashboard."""

    # Paths that don't require authentication
    PUBLIC_PATHS = {"/api/auth/status", "/login.html"}

    def _check_auth(self) -> bool:
        """Check authentication. Returns True if authenticated or auth disabled."""
        if not is_auth_enabled():
            return True
        is_authed, _ = check_auth(self)
        return is_authed

    def _unauthorized(self) -> None:
        """Return 401 Unauthorized response."""
        self._json({"error": "Unauthorized", "authRequired": True}, code=401)

    def _json(self, data: dict, code: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _text(self, text: str, code: int = 200, content_type: str = "text/plain; charset=utf-8") -> None:
        body = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self._text("Not found", code=404)
            return
        self._text(path.read_text(encoding="utf-8"), content_type=content_type)

    def _binary_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self._text("Not found", code=404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", f'attachment; filename="{path.name}"')
        self.end_headers()
        self.wfile.write(data)

    def _handle_login(self) -> None:
        """Handle login POST request."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}
        except (json.JSONDecodeError, ValueError):
            self._json({"error": "Invalid request body"}, code=400)
            return

        token = data.get("token", "")
        secret = get_configured_token()

        if not secret:
            # Auth not configured - allow login
            self._json({"success": True, "message": "Authentication not configured"})
            return

        import hmac
        if hmac.compare_digest(token, secret):
            # Success - set cookie and return
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Set-Cookie", f"dashboard_token={token}; Path=/; Max-Age=86400; HttpOnly; SameSite=Strict")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": "Login successful"}).encode())
        else:
            self._json({"error": "Invalid token"}, code=401)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        qs = parse_qs(parsed.query)

        # === Public Paths (no auth required) ===
        if path in self.PUBLIC_PATHS:
            if path == "/api/auth/status":
                self._json({
                    "authEnabled": is_auth_enabled(),
                    "tokenConfigured": get_configured_token() is not None,
                })
                return
            if path == "/login.html":
                login_file = DASHBOARD_DIR / "login.html"
                if login_file.exists():
                    self._serve_file(login_file, "text/html; charset=utf-8")
                else:
                    self._text("Login page not found", code=404)
                return

        # === Authentication Check ===
        if not self._check_auth():
            # Redirect to login for HTML requests
            if path == "/" or path == "/index.html":
                self.send_response(302)
                self.send_header("Location", "/login.html")
                self.end_headers()
                return
            # Return 401 for API requests
            self._unauthorized()
            return

        # === Static Files ===
        if path == "/" or path == "/index.html":
            dashboard_file = DASHBOARD_DIR / "index-enhanced.html"
            if dashboard_file.exists():
                self._serve_file(dashboard_file, "text/html; charset=utf-8")
            else:
                self._serve_file(DASHBOARD_DIR / "index-macos.html", "text/html; charset=utf-8")
            return

        if path == "/app.js":
            js_file = DASHBOARD_DIR / "app-enhanced.js"
            if js_file.exists():
                self._serve_file(js_file, "application/javascript; charset=utf-8")
            else:
                self._serve_file(DASHBOARD_DIR / "app-macos.js", "application/javascript; charset=utf-8")
            return

        if path == "/styles.css":
            self._serve_file(DASHBOARD_DIR / "styles.css", "text/css; charset=utf-8")
            return

        if path == "/favicon.svg":
            self._serve_file(DASHBOARD_DIR / "favicon.svg", "image/svg+xml")
            return

        # === API: Prometheus Metrics ===
        if path == "/metrics":
            status = gather_status()
            metrics = format_prometheus_metrics(status)
            self._text(metrics, content_type="text/plain; version=0.0.4; charset=utf-8")
            return

        # === API: Status ===
        if path == "/api/status":
            self._json(gather_status())
            return

        # === API: Consensus ===
        if path == "/api/consensus":
            self._json({"timestamp": datetime.now(timezone.utc).isoformat(), "content": read_text_file(CONSENSUS_FILE, "")})
            return

        # === API: Activities ===
        if path == "/api/activities":
            limit = int(qs.get("limit", ["100"])[0])
            activities = read_activities(ACTIVITIES_FILE, limit)
            agent_stats = get_agent_stats(activities)
            self._json({"timestamp": datetime.now(timezone.utc).isoformat(), "activities": activities, "agentStats": agent_stats})
            return

        # === API: Cycle Logs ===
        if path == "/api/cycles":
            engine = qs.get("engine", [None])[0]
            cycles = find_cycle_logs(engine)
            self._json({"timestamp": datetime.now(timezone.utc).isoformat(), "engine": engine, "cycles": cycles, "total": len(cycles)})
            return

        if path.startswith("/api/cycle/"):
            filename = path[len("/api/cycle/"):]
            log_path = REPO_ROOT / "logs" / filename
            if not log_path.exists():
                self._json({"error": f"Cycle log not found: {filename}"}, code=404)
                return
            content = read_text_file(log_path, "")
            self._json({"timestamp": datetime.now(timezone.utc).isoformat(), "filename": filename, "content": content})
            return

        # === API: Main Log ===
        if path == "/api/log":
            lines = int(qs.get("lines", ["200"])[0])
            engine = qs.get("engine", [None])[0]
            if engine == "qwen":
                log_file = QWEN_LOG_FILE
            elif engine == "opencode":
                log_file = OPENCODE_LOG_FILE if OPENCODE_LOG_FILE.exists() else CODEX_LOG_FILE
            else:
                log_file = QWEN_LOG_FILE if QWEN_LOG_FILE.exists() else CODEX_LOG_FILE
            self._json({"timestamp": datetime.now(timezone.utc).isoformat(), "lines": lines, "logTail": read_tail(log_file, lines)})
            return

        # === API: Structured JSON Logs ===
        if path == "/api/logs/json":
            limit = int(qs.get("limit", ["500"])[0])
            engine = qs.get("engine", [None])[0]
            if engine == "qwen":
                jsonl_file = QWEN_JSONL_FILE
            elif engine == "opencode":
                jsonl_file = OPENCODE_JSONL_FILE if OPENCODE_JSONL_FILE.exists() else CODEX_JSONL_FILE
            else:
                jsonl_file = QWEN_JSONL_FILE if QWEN_JSONL_FILE.exists() else CODEX_JSONL_FILE
            from lib.utils import read_structured_logs, get_log_stats
            logs = read_structured_logs(jsonl_file, limit)
            stats = get_log_stats(logs)
            self._json({"timestamp": datetime.now(timezone.utc).isoformat(), "engine": engine or "qwen", "logs": logs, "stats": stats})
            return

        # === API: File Browser ===
        if path == "/api/files":
            dir_name = qs.get("dir", ["docs"])[0]
            if dir_name not in BROWSE_DIRS:
                self._json({"error": f"Invalid directory: {dir_name}. Allowed: {BROWSE_DIRS}"}, code=400)
                return
            dir_path = REPO_ROOT / dir_name
            result = browse_directory(dir_path, REPO_ROOT)
            result["dir"] = dir_name
            self._json({"timestamp": datetime.now(timezone.utc).isoformat(), **result})
            return

        if path.startswith("/api/files/"):
            subpath = path[len("/api/files/"):]
            if ".." in subpath or subpath.startswith("/"):
                self._json({"error": "Invalid path"}, code=400)
                return
            full_path = REPO_ROOT / subpath
            if full_path.is_dir():
                result = browse_directory(full_path, REPO_ROOT)
                self._json({"timestamp": datetime.now(timezone.utc).isoformat(), **result})
                return
            else:
                self._json({"error": f"Not a directory: {subpath}"}, code=400)
                return

        # === API: File Content ===
        if path.startswith("/api/file/"):
            subpath = path[len("/api/file/"):]
            if ".." in subpath or subpath.startswith("/"):
                self._json({"error": "Invalid path"}, code=400)
                return
            full_path = REPO_ROOT / subpath
            if not full_path.exists():
                self._json({"error": f"File not found: {subpath}"}, code=404)
                return
            if full_path.is_dir():
                self._json({"error": f"Is a directory: {subpath}"}, code=400)
                return
            content = read_text_file(full_path, "")
            ext = full_path.suffix.lower()
            file_type = "text"
            if ext in [".md", ".markdown"]:
                file_type = "markdown"
            elif ext in [".json", ".jsonl"]:
                file_type = "json"
            elif ext in [".py", ".js", ".ts", ".sh", ".bash"]:
                file_type = "code"
            elif ext in [".log"]:
                file_type = "log"
            self._json({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": subpath,
                "name": full_path.name,
                "type": file_type,
                "size": full_path.stat().st_size,
                "content": content
            })
            return

        # === API: File Download ===
        if path.startswith("/api/download/"):
            subpath = path[len("/api/download/"):]
            if ".." in subpath or subpath.startswith("/"):
                self._text("Invalid path", code=400)
                return
            full_path = REPO_ROOT / subpath
            if not full_path.exists():
                self._text("File not found", code=404)
                return
            if full_path.is_dir():
                self._text("Is a directory", code=400)
                return
            mime_type, _ = mimetypes.guess_type(str(full_path))
            if mime_type is None:
                mime_type = "application/octet-stream"
            self._binary_file(full_path, mime_type)
            return

        self._text("Not found", code=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        # === Public POST endpoints ===
        if path == "/api/auth/login":
            self._handle_login()
            return

        # === Authentication Check ===
        if not self._check_auth():
            self._unauthorized()
            return

        if path == "/api/action/start":
            engine = qs.get("engine", [None])[0]
            result = start_loop(engine)
            self._json({"timestamp": datetime.now(timezone.utc).isoformat(), "action": "start", **result})
            return

        if path == "/api/action/stop":
            result = stop_loop()
            self._json({"timestamp": datetime.now(timezone.utc).isoformat(), "action": "stop", **result})
            return

        if path == "/api/action/refresh":
            self._json({"timestamp": datetime.now(timezone.utc).isoformat(), "action": "refresh", "ok": True, "status": gather_status()})
            return

        self._text("Not found", code=404)

    def log_message(self, fmt: str, *args) -> None:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto Company Enhanced Dashboard Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8787, help="Port to bind (default: 8787)")
    parser.add_argument("--generate-token", action="store_true", help="Generate a new token file and exit")
    args = parser.parse_args()

    if args.generate_token:
        token = init_token_file(force=True)
        print(f"Generated token: {token}")
        print(f"Token file: {TOKEN_FILE}")
        return

    (REPO_ROOT / "logs").mkdir(parents=True, exist_ok=True)

    auth_status = "enabled" if is_auth_enabled() else "disabled"
    token_info = "(set DASHBOARD_TOKEN env or create .dashboard-token file to enable)"

    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)

    print("=" * 60)
    print("  Auto Company Dashboard - Enhanced Edition")
    print("=" * 60)
    print(f"  URL:     http://{args.host}:{args.port}")
    print(f"  Repo:    {REPO_ROOT}")
    print(f"  Auth:    {auth_status} {token_info if auth_status == 'disabled' else ''}")
    print("=" * 60)
    print("  Endpoints:")
    print("  - Status:      /api/status")
    print("  - Metrics:     /metrics (Prometheus)")
    print("  - Files:       /api/files?dir=docs")
    print("  - Cycles:      /api/cycles")
    print("  - Activities:  /api/activities")
    print("  - Auth Status: /api/auth/status")
    print("=" * 60)
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[dashboard] shutting down...")
    finally:
        server.server_close()
        print("[dashboard] stopped")


if __name__ == "__main__":
    os.chdir(REPO_ROOT)
    main()