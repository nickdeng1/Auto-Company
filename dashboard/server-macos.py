#!/usr/bin/env python3
"""
Auto Company Dashboard Server - macOS Edition
==============================================
Web-based monitoring and control panel for Auto Company loop.

Features:
- Real-time status monitoring
- Log tail viewing
- Consensus file preview
- Start/Stop controls
- Process management

Usage:
    python3 dashboard/server-macos.py --port 8787
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import signal
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

# Paths
REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = Path(__file__).resolve().parent

# Qwen Loop files
QWEN_PID_FILE = REPO_ROOT / ".auto-loop-qwen.pid"
QWEN_STATE_FILE = REPO_ROOT / ".auto-loop-qwen-state"
QWEN_LOG_FILE = REPO_ROOT / "logs" / "auto-loop-qwen.log"

# OpenCode Loop files
OPENCODE_PID_FILE = REPO_ROOT / ".auto-loop-opencode.pid"
OPENCODE_STATE_FILE = REPO_ROOT / ".auto-loop-opencode-state"
OPENCODE_LOG_FILE = REPO_ROOT / "logs" / "auto-loop-opencode.log"

# Codex Loop files (fallback)
CODEX_PID_FILE = REPO_ROOT / ".auto-loop.pid"
CODEX_STATE_FILE = REPO_ROOT / ".auto-loop-state"
CODEX_LOG_FILE = REPO_ROOT / "logs" / "auto-loop.log"

# Shared files
CONSENSUS_FILE = REPO_ROOT / "memories" / "consensus.md"
PROMPT_FILE = REPO_ROOT / "PROMPT.md"
STOP_FLAG = REPO_ROOT / ".auto-loop-stop"
PAUSE_FLAG = REPO_ROOT / ".auto-loop-paused"
PROGRESS_FILE = REPO_ROOT / ".progress.json"
ACTIVITIES_FILE = REPO_ROOT / "logs" / "activities.jsonl"

# Scripts
QWEN_SCRIPT = REPO_ROOT / "scripts" / "core" / "auto-loop-qwen.sh"
QWEN_SCRIPT_PY = REPO_ROOT / "scripts" / "core" / "auto-loop-qwen.py"
OPENCODE_SCRIPT = REPO_ROOT / "scripts" / "core" / "auto-loop-opencode.sh"
STOP_SCRIPT = REPO_ROOT / "scripts" / "core" / "stop-loop.sh"
MONITOR_SCRIPT = REPO_ROOT / "scripts" / "core" / "monitor.sh"

# Default engine (can be changed via API)
DEFAULT_ENGINE = "opencode"


def read_text_file(path: Path, fallback: str = "") -> str:
    """Read text file with encoding detection."""
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return fallback
    except Exception as exc:
        return f"(read error: {exc})"

    for enc in ("utf-8", "utf-8-sig", "gb18030", "cp936", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue

    return raw.decode("utf-8", errors="replace")


def read_tail(path: Path, lines: int = 120) -> str:
    """Read last N lines from a file."""
    if lines <= 0:
        return ""
    text = read_text_file(path, "")
    if not text:
        return ""
    rows = text.splitlines()
    return "\n".join(rows[-lines:])


def find_latest_cycle_log(engine: str) -> Path | None:
    """Find the latest cycle log file for the given engine."""
    log_dir = REPO_ROOT / "logs"
    if not log_dir.exists():
        return None

    # Pattern based on engine
    if engine == "opencode":
        pattern = "cycle-opencode-*.log"
    elif engine == "qwen":
        pattern = "cycle-qwen-*.log"
    else:
        pattern = "cycle-*.log"

    # Find all matching files
    matches = list(log_dir.glob(pattern))
    if not matches:
        return None

    # Return the most recent one
    return max(matches, key=lambda p: p.stat().st_mtime)


def read_combined_logs(engine: str, main_lines: int = 50, cycle_lines: int = 500) -> str:
    """Read combined logs: main log + latest cycle log."""
    parts = []

    # Read main log
    if engine == "opencode":
        main_log = OPENCODE_LOG_FILE if OPENCODE_LOG_FILE.exists() else CODEX_LOG_FILE
    elif engine == "qwen":
        main_log = QWEN_LOG_FILE
    else:
        main_log = CODEX_LOG_FILE

    main_content = read_tail(main_log, main_lines)
    if main_content:
        parts.append(f"{'='*60}\n[主日志 - {main_log.name}]\n{'='*60}\n{main_content}")

    # Read latest cycle log
    cycle_log = find_latest_cycle_log(engine)
    if cycle_log:
        cycle_content = read_tail(cycle_log, cycle_lines)
        if cycle_content:
            parts.append(f"\n{'='*60}\n[周期日志 - {cycle_log.name}]\n{'='*60}\n{cycle_content}")

    return "\n".join(parts)


def read_json_file(path: Path, fallback: dict = None) -> dict:
    """Read JSON file."""
    if fallback is None:
        fallback = {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def read_activities(limit: int = 100) -> list[dict]:
    """Read activities from JSONL file, newest first."""
    activities = []
    if not ACTIVITIES_FILE.exists():
        return activities

    try:
        lines = ACTIVITIES_FILE.read_text(encoding="utf-8").strip().split("\n")
        for line in reversed(lines[-limit:]):
            line = line.strip()
            if line:
                try:
                    activities.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return activities


def get_agent_stats(activities: list[dict]) -> dict:
    """Get statistics about agent activities."""
    stats = {}
    for act in activities:
        agent = act.get("agent", "unknown")
        if agent not in stats:
            stats[agent] = {
                "role": act.get("role", ""),
                "count": 0,
                "actions": {},
                "lastActive": ""
            }
        stats[agent]["count"] += 1
        action = act.get("action", "unknown")
        stats[agent]["actions"][action] = stats[agent]["actions"].get(action, 0) + 1
        stats[agent]["lastActive"] = act.get("ts", "")

    return stats


def parse_state_file(path: Path) -> dict[str, str]:
    """Parse KEY=VALUE state file."""
    text = read_text_file(path, "")
    result = {}
    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def is_process_running(pid: int) -> bool:
    """Check if a process is running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError, TypeError):
        return False


def get_process_info(pid: int) -> dict:
    """Get process info by PID."""
    if not pid:
        return {"running": False, "cmd": "", "cpu": "", "mem": ""}
    
    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "pid,pcpu,pmem,comm="],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                return {
                    "running": True,
                    "cmd": parts[3] if len(parts) > 3 else parts[-1] if parts else "",
                    "cpu": parts[1] if len(parts) > 1 else "",
                    "mem": parts[2] if len(parts) > 2 else "",
                }
    except Exception:
        pass
    
    return {"running": False, "cmd": "", "cpu": "", "mem": ""}


def gather_status() -> dict[str, Any]:
    """Gather all status information."""
    now = datetime.now(timezone.utc)

    # Detect which loop is running
    qwen_state = parse_state_file(QWEN_STATE_FILE)
    opencode_state = parse_state_file(OPENCODE_STATE_FILE)
    codex_state = parse_state_file(CODEX_STATE_FILE)

    # Check OpenCode loop
    opencode_pid = None
    opencode_running = False
    if OPENCODE_PID_FILE.exists():
        try:
            opencode_pid = int(OPENCODE_PID_FILE.read_text().strip())
            opencode_running = is_process_running(opencode_pid)
        except (ValueError, OSError):
            pass

    # Check Qwen loop
    qwen_pid = None
    qwen_running = False
    if QWEN_PID_FILE.exists():
        try:
            qwen_pid = int(QWEN_PID_FILE.read_text().strip())
            qwen_running = is_process_running(qwen_pid)
        except (ValueError, OSError):
            pass

    # Check Codex loop
    codex_pid = None
    codex_running = False
    if CODEX_PID_FILE.exists():
        try:
            codex_pid = int(CODEX_PID_FILE.read_text().strip())
            codex_running = is_process_running(codex_pid)
        except (ValueError, OSError):
            pass

    # Determine active engine (priority: opencode > qwen > codex)
    if opencode_running:
        active_engine = "opencode"
        active_pid = opencode_pid
        active_running = True
        active_state = opencode_state
    elif qwen_running:
        active_engine = "qwen"
        active_pid = qwen_pid
        active_running = True
        active_state = qwen_state
    elif codex_running:
        active_engine = "codex"
        active_pid = codex_pid
        active_running = True
        active_state = codex_state
    else:
        # No running loop, check state files for last known engine
        active_engine = (
            opencode_state.get("ENGINE", "") or
            qwen_state.get("ENGINE", "") or
            codex_state.get("ENGINE", "none")
        )
        active_pid = opencode_pid or qwen_pid or codex_pid
        active_running = False
        active_state = opencode_state or qwen_state or codex_state

    # Get process info
    process_info = get_process_info(active_pid) if active_pid else {}

    # Read logs based on active engine
    if active_engine == "opencode":
        # Prefer opencode-specific log, fallback to shared log
        if OPENCODE_LOG_FILE.exists():
            log_file = OPENCODE_LOG_FILE
        else:
            log_file = CODEX_LOG_FILE  # Fallback to shared log
    elif active_engine == "qwen" or QWEN_LOG_FILE.exists():
        log_file = QWEN_LOG_FILE
    else:
        log_file = CODEX_LOG_FILE

    # Read combined logs (main + cycle)
    combined_log = read_combined_logs(active_engine, main_lines=50, cycle_lines=500)

    # Read progress
    progress = read_json_file(PROGRESS_FILE)

    # Read activities
    activities = read_activities(limit=100)
    agent_stats = get_agent_stats(activities)

    # Check stop/pause flags
    stop_requested = STOP_FLAG.exists()
    paused = PAUSE_FLAG.exists()

    return {
        "timestamp": now.isoformat(),
        "engine": {
            "active": active_engine,
            "available": {
                "opencode": OPENCODE_PID_FILE.exists() or OPENCODE_STATE_FILE.exists(),
                "qwen": QWEN_PID_FILE.exists() or QWEN_STATE_FILE.exists(),
                "codex": CODEX_PID_FILE.exists() or CODEX_STATE_FILE.exists(),
            }
        },
        "loop": {
            "state": "running" if active_running else "stopped",
            "pid": active_pid,
            "running": active_running,
            "stopRequested": stop_requested,
            "paused": paused,
            "loopCount": active_state.get("LOOP_COUNT", "0"),
            "errorCount": active_state.get("ERROR_COUNT", "0"),
            "lastRun": active_state.get("LAST_RUN", ""),
            "model": active_state.get("MODEL", "default"),
            "status": active_state.get("STATUS", "unknown"),
        },
        "process": process_info,
        "state": active_state,
        "progress": progress,
        "consensus": read_text_file(CONSENSUS_FILE, "(no consensus file)")[:5000],
        "logTail": combined_log,
        "activities": activities,
        "agentStats": agent_stats,
        "flags": {
            "stop": stop_requested,
            "pause": paused,
        }
    }


def run_script(script_path: Path, args: list = None, timeout: int = 30) -> dict:
    """Run a shell script and return result."""
    if not script_path.exists():
        return {
            "ok": False,
            "error": f"Script not found: {script_path}",
            "exitCode": -1,
            "output": ""
        }
    
    cmd = [str(script_path)]
    if args:
        cmd.extend(args)
    
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO_ROOT)
        )
        elapsed = int((time.time() - start) * 1000)
        return {
            "ok": result.returncode == 0,
            "exitCode": result.returncode,
            "output": result.stdout,
            "error": result.stderr,
            "elapsedMs": elapsed
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": f"Timeout after {timeout}s",
            "exitCode": -1,
            "output": ""
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "exitCode": -1,
            "output": ""
        }


def start_loop(engine: str = None) -> dict:
    """Start a loop with the specified engine."""
    if engine is None:
        engine = DEFAULT_ENGINE

    # Check if already running
    status = gather_status()
    if status["loop"]["running"]:
        return {
            "ok": False,
            "error": f"Loop already running (engine: {status['engine']['active']})",
            "pid": status["loop"]["pid"]
        }

    # Remove stop/pause flags
    STOP_FLAG.unlink(missing_ok=True)
    PAUSE_FLAG.unlink(missing_ok=True)

    # Ensure log directory exists
    log_dir = REPO_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    try:
        if engine == "opencode":
            # Start OpenCode loop (shell script)
            if not OPENCODE_SCRIPT.exists():
                return {"ok": False, "error": f"OpenCode script not found: {OPENCODE_SCRIPT}"}

            subprocess.Popen(
                ["nohup", "bash", str(OPENCODE_SCRIPT)],
                stdout=open(log_dir / "opencode-stdout.log", "a"),
                stderr=open(log_dir / "opencode-stderr.log", "a"),
                stdin=subprocess.DEVNULL,
                cwd=str(REPO_ROOT),
                start_new_session=True
            )
        elif engine == "qwen":
            # Start Qwen loop (shell script preferred, Python fallback)
            script_to_use = QWEN_SCRIPT if QWEN_SCRIPT.exists() else QWEN_SCRIPT_PY
            if not script_to_use.exists():
                return {"ok": False, "error": f"Qwen script not found: {QWEN_SCRIPT} or {QWEN_SCRIPT_PY}"}

            if script_to_use.suffix == ".sh":
                # Shell script
                subprocess.Popen(
                    ["nohup", "bash", str(script_to_use)],
                    stdout=open(log_dir / "qwen-stdout.log", "a"),
                    stderr=open(log_dir / "qwen-stderr.log", "a"),
                    stdin=subprocess.DEVNULL,
                    cwd=str(REPO_ROOT),
                    start_new_session=True
                )
            else:
                # Python script
                subprocess.Popen(
                    ["nohup", sys.executable, str(script_to_use)],
                    stdout=open(log_dir / "qwen-stdout.log", "a"),
                    stderr=open(log_dir / "qwen-stderr.log", "a"),
                    stdin=subprocess.DEVNULL,
                    cwd=str(REPO_ROOT),
                    start_new_session=True
                )
        else:
            return {"ok": False, "error": f"Unknown engine: {engine}"}

        time.sleep(1)

        # Verify it started
        status = gather_status()
        if status["loop"]["running"]:
            return {
                "ok": True,
                "message": f"{engine} loop started",
                "pid": status["loop"]["pid"],
                "engine": engine
            }
        else:
            return {
                "ok": False,
                "error": f"{engine} loop failed to start. Check logs/{engine}-stderr.log"
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def stop_loop() -> dict:
    """Stop the running loop."""
    status = gather_status()
    pid = status["loop"]["pid"]
    engine = status["engine"]["active"]

    if not pid:
        return {"ok": True, "message": "Loop not running"}

    # Create stop flag for graceful shutdown
    STOP_FLAG.touch()

    # Send SIGTERM
    if status["loop"]["running"]:
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)

            # Check if still running
            if is_process_running(pid):
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)
        except ProcessLookupError:
            pass

    # Clean up PID files
    OPENCODE_PID_FILE.unlink(missing_ok=True)
    QWEN_PID_FILE.unlink(missing_ok=True)
    CODEX_PID_FILE.unlink(missing_ok=True)

    return {"ok": True, "message": f"{engine} loop stopped"}


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard."""
    
    def _json(self, data: dict, code: int = 200) -> None:
        """Send JSON response."""
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    
    def _text(self, text: str, code: int = 200, content_type: str = "text/plain; charset=utf-8") -> None:
        """Send text response."""
        body = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    
    def _serve_file(self, path: Path, content_type: str) -> None:
        """Serve a static file."""
        if not path.exists():
            self._text("Not found", code=404)
            return
        self._text(path.read_text(encoding="utf-8"), content_type=content_type)
    
    def do_GET(self) -> None:
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        # Static files
        if path == "/" or path == "/index.html":
            # Serve macOS-specific dashboard
            dashboard_file = DASHBOARD_DIR / "index-macos.html"
            if dashboard_file.exists():
                self._serve_file(dashboard_file, "text/html; charset=utf-8")
            else:
                self._serve_file(DASHBOARD_DIR / "index.html", "text/html; charset=utf-8")
            return
        
        if path == "/app.js":
            js_file = DASHBOARD_DIR / "app-macos.js"
            if js_file.exists():
                self._serve_file(js_file, "application/javascript; charset=utf-8")
            else:
                self._serve_file(DASHBOARD_DIR / "app.js", "application/javascript; charset=utf-8")
            return
        
        if path == "/styles.css":
            self._serve_file(DASHBOARD_DIR / "styles.css", "text/css; charset=utf-8")
            return
        
        if path == "/favicon.svg":
            self._serve_file(DASHBOARD_DIR / "favicon.svg", "image/svg+xml")
            return
        
        # API endpoints
        if path == "/api/status":
            self._json(gather_status())
            return
        
        if path == "/api/log-tail":
            qs = parse_qs(parsed.query)
            lines = int(qs.get("lines", ["200"])[0])
            status = gather_status()
            log_file = QWEN_LOG_FILE if status["engine"]["active"] == "qwen" else CODEX_LOG_FILE
            self._json({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "lines": lines,
                "logTail": read_tail(log_file, lines)
            })
            return
        
        if path == "/api/consensus":
            self._json({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "content": read_text_file(CONSENSUS_FILE, "")
            })
            return
        
        if path == "/api/progress":
            self._json({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "progress": read_json_file(PROGRESS_FILE)
            })
            return

        if path == "/api/activities":
            qs = parse_qs(parsed.query)
            limit = int(qs.get("limit", ["100"])[0])
            activities = read_activities(limit)
            agent_stats = get_agent_stats(activities)
            self._json({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "activities": activities,
                "agentStats": agent_stats
            })
            return
        
        self._text("Not found", code=404)
    
    def do_POST(self) -> None:
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == "/api/action/start":
            # Parse optional engine parameter
            qs = parse_qs(parsed.query)
            engine = qs.get("engine", [None])[0]
            result = start_loop(engine)
            self._json({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "start",
                **result
            })
            return
        
        if path == "/api/action/stop":
            result = stop_loop()
            self._json({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "stop",
                **result
            })
            return
        
        if path == "/api/action/refresh":
            self._json({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "refresh",
                "ok": True,
                "status": gather_status()
            })
            return
        
        self._text("Not found", code=404)
    
    def log_message(self, fmt: str, *args) -> None:
        """Suppress default logging."""
        pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Auto Company Dashboard Server (macOS Edition)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 dashboard/server-macos.py
    python3 dashboard/server-macos.py --port 8080
    python3 dashboard/server-macos.py --host 0.0.0.0
        """
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8787, help="Port to bind (default: 8787)")
    args = parser.parse_args()
    
    # Ensure log directory exists
    (REPO_ROOT / "logs").mkdir(parents=True, exist_ok=True)
    
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    
    print("=" * 60)
    print("  Auto Company Dashboard - macOS Edition")
    print("=" * 60)
    print(f"  URL:     http://{args.host}:{args.port}")
    print(f"  Repo:    {REPO_ROOT}")
    print(f"  Logs:    {REPO_ROOT / 'logs'}")
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