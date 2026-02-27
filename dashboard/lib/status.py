"""
Dashboard status gathering functions.
Collects loop state, process info, and system status.
"""

import os
import re
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .utils import (
    read_text_file,
    read_json_file,
    read_activities,
    read_structured_logs,
    get_log_stats,
    get_agent_stats,
    parse_state_file,
    is_process_running,
    get_process_info,
)

# Default paths (can be overridden)
REPO_ROOT = Path(__file__).resolve().parents[2]

# Loop files
QWEN_PID_FILE = REPO_ROOT / ".auto-loop-qwen.pid"
QWEN_STATE_FILE = REPO_ROOT / ".auto-loop-qwen-state"
QWEN_LOG_FILE = REPO_ROOT / "logs" / "auto-loop-qwen.log"
QWEN_JSONL_FILE = REPO_ROOT / "logs" / "auto-loop-qwen.jsonl"

OPENCODE_PID_FILE = REPO_ROOT / ".auto-loop-opencode.pid"
OPENCODE_STATE_FILE = REPO_ROOT / ".auto-loop-opencode-state"
OPENCODE_LOG_FILE = REPO_ROOT / "logs" / "auto-loop-opencode.log"
OPENCODE_JSONL_FILE = REPO_ROOT / "logs" / "auto-loop-opencode.jsonl"

CODEX_PID_FILE = REPO_ROOT / ".auto-loop.pid"
CODEX_STATE_FILE = REPO_ROOT / ".auto-loop-state"
CODEX_LOG_FILE = REPO_ROOT / "logs" / "auto-loop.log"
CODEX_JSONL_FILE = REPO_ROOT / "logs" / "auto-loop.jsonl"

# Shared files
CONSENSUS_FILE = REPO_ROOT / "memories" / "consensus.md"
PROMPT_FILE = REPO_ROOT / "PROMPT.md"
STOP_FLAG = REPO_ROOT / ".auto-loop-stop"
PAUSE_FLAG = REPO_ROOT / ".auto-loop-paused"
PROGRESS_FILE = REPO_ROOT / ".progress.json"
ACTIVITIES_FILE = REPO_ROOT / "logs" / "activities.jsonl"

# Scripts
QWEN_SCRIPT = REPO_ROOT / "scripts" / "core" / "auto-loop-qwen.sh"
OPENCODE_SCRIPT = REPO_ROOT / "scripts" / "core" / "auto-loop-opencode.sh"
STOP_SCRIPT = REPO_ROOT / "scripts" / "core" / "stop-loop.sh"

DEFAULT_ENGINE = "qwen"
BROWSE_DIRS = ["docs", "projects", "logs"]


def gather_status() -> dict[str, Any]:
    """Gather all status information."""
    now = datetime.now(timezone.utc)

    qwen_state = parse_state_file(QWEN_STATE_FILE)
    opencode_state = parse_state_file(OPENCODE_STATE_FILE)
    codex_state = parse_state_file(CODEX_STATE_FILE)

    qwen_pid = None
    qwen_running = False
    if QWEN_PID_FILE.exists():
        try:
            qwen_pid = int(QWEN_PID_FILE.read_text().strip())
            qwen_running = is_process_running(qwen_pid)
        except (ValueError, OSError):
            pass

    opencode_pid = None
    opencode_running = False
    if OPENCODE_PID_FILE.exists():
        try:
            opencode_pid = int(OPENCODE_PID_FILE.read_text().strip())
            opencode_running = is_process_running(opencode_pid)
        except (ValueError, OSError):
            pass

    codex_pid = None
    codex_running = False
    if CODEX_PID_FILE.exists():
        try:
            codex_pid = int(CODEX_PID_FILE.read_text().strip())
            codex_running = is_process_running(codex_pid)
        except (ValueError, OSError):
            pass

    if qwen_running:
        active_engine = "qwen"
        active_pid = qwen_pid
        active_running = True
        active_state = qwen_state
    elif opencode_running:
        active_engine = "opencode"
        active_pid = opencode_pid
        active_running = True
        active_state = opencode_state
    elif codex_running:
        active_engine = "codex"
        active_pid = codex_pid
        active_running = True
        active_state = codex_state
    else:
        active_engine = qwen_state.get("ENGINE", "") or opencode_state.get("ENGINE", "") or "qwen"
        active_pid = qwen_pid or opencode_pid or codex_pid
        active_running = False
        active_state = qwen_state or opencode_state or codex_state

    process_info = get_process_info(active_pid) if active_pid else {}

    if active_engine == "qwen":
        main_log = QWEN_LOG_FILE
        jsonl_log = QWEN_JSONL_FILE
    elif active_engine == "opencode":
        main_log = OPENCODE_LOG_FILE if OPENCODE_LOG_FILE.exists() else CODEX_LOG_FILE
        jsonl_log = OPENCODE_JSONL_FILE if OPENCODE_JSONL_FILE.exists() else CODEX_JSONL_FILE
    else:
        main_log = CODEX_LOG_FILE
        jsonl_log = CODEX_JSONL_FILE

    progress = read_json_file(PROGRESS_FILE)
    activities = read_activities(ACTIVITIES_FILE, limit=100)
    agent_stats = get_agent_stats(activities)
    stop_requested = STOP_FLAG.exists()
    paused = PAUSE_FLAG.exists()

    # Read structured logs for statistics
    structured_logs = read_structured_logs(jsonl_log, limit=500)
    log_stats = get_log_stats(structured_logs)

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
        "activities": activities,
        "agentStats": agent_stats,
        "logStats": log_stats,
        "flags": {"stop": stop_requested, "pause": paused},
    }


def find_cycle_logs(engine: str = None) -> list[dict]:
    """Find all cycle log files with metadata."""
    log_dir = REPO_ROOT / "logs"
    if not log_dir.exists():
        return []

    patterns = []
    if engine == "qwen":
        patterns = ["cycle-qwen-*.log"]
    elif engine == "opencode":
        patterns = ["cycle-opencode-*.log"]
    elif engine == "codex":
        patterns = ["cycle-*.log"]
    else:
        patterns = ["cycle-qwen-*.log", "cycle-opencode-*.log", "cycle-*.log"]

    cycles = []
    seen = set()

    for pattern in patterns:
        for path in log_dir.glob(pattern):
            if path.name in seen:
                continue
            seen.add(path.name)

            try:
                stat = path.stat()
                # Parse cycle number from filename
                match = re.search(r"cycle-\w*-(\d+)-", path.name)
                cycle_num = int(match.group(1)) if match else 0

                # Detect engine from filename
                if "qwen" in path.name:
                    eng = "qwen"
                elif "opencode" in path.name:
                    eng = "opencode"
                else:
                    eng = "codex"

                cycles.append({
                    "filename": path.name,
                    "path": str(path.relative_to(REPO_ROOT)),
                    "cycle": cycle_num,
                    "engine": eng,
                    "size": stat.st_size,
                    "mtime": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                })
            except Exception:
                continue

    # Sort by mtime descending
    cycles.sort(key=lambda x: x["mtime"], reverse=True)
    return cycles


def browse_directory(dir_path: Path, base_path: Path) -> dict:
    """Browse a directory and return file listing."""
    if not dir_path.exists() or not dir_path.is_dir():
        return {"error": f"Directory not found: {dir_path}", "files": [], "dirs": []}

    files = []
    dirs = []

    try:
        for item in sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            rel_path = str(item.relative_to(base_path))
            if item.is_dir():
                dirs.append({
                    "name": item.name,
                    "path": rel_path,
                    "type": "dir"
                })
            else:
                stat = item.stat()
                # Detect file type
                ext = item.suffix.lower()
                file_type = "file"
                if ext in [".md", ".markdown"]:
                    file_type = "markdown"
                elif ext in [".json", ".jsonl"]:
                    file_type = "json"
                elif ext in [".py", ".js", ".ts", ".sh"]:
                    file_type = "code"
                elif ext in [".log"]:
                    file_type = "log"

                files.append({
                    "name": item.name,
                    "path": rel_path,
                    "type": file_type,
                    "ext": ext,
                    "size": stat.st_size,
                    "mtime": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                })
    except Exception as e:
        return {"error": str(e), "files": [], "dirs": []}

    return {
        "path": str(dir_path.relative_to(base_path)),
        "files": files,
        "dirs": dirs
    }


def run_script(script_path: Path, args: list = None, timeout: int = 30) -> dict:
    """Run a shell script and return result."""
    if not script_path.exists():
        return {"ok": False, "error": f"Script not found: {script_path}", "exitCode": -1, "output": ""}

    cmd = [str(script_path)]
    if args:
        cmd.extend(args)

    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(REPO_ROOT))
        elapsed = int((time.time() - start) * 1000)
        return {"ok": result.returncode == 0, "exitCode": result.returncode, "output": result.stdout, "error": result.stderr, "elapsedMs": elapsed}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"Timeout after {timeout}s", "exitCode": -1, "output": ""}
    except Exception as e:
        return {"ok": False, "error": str(e), "exitCode": -1, "output": ""}


def start_loop(engine: str = None) -> dict:
    """Start a loop with the specified engine."""
    if engine is None:
        engine = DEFAULT_ENGINE

    status = gather_status()
    if status["loop"]["running"]:
        return {"ok": False, "error": f"Loop already running (engine: {status['engine']['active']})", "pid": status["loop"]["pid"]}

    STOP_FLAG.unlink(missing_ok=True)
    PAUSE_FLAG.unlink(missing_ok=True)

    log_dir = REPO_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    try:
        if engine == "qwen":
            script = QWEN_SCRIPT
            if not script.exists():
                return {"ok": False, "error": f"Qwen script not found: {script}"}
            subprocess.Popen(
                ["nohup", "bash", str(script)],
                stdout=open(log_dir / "qwen-stdout.log", "a"),
                stderr=open(log_dir / "qwen-stderr.log", "a"),
                stdin=subprocess.DEVNULL,
                cwd=str(REPO_ROOT),
                start_new_session=True
            )
        elif engine == "opencode":
            script = OPENCODE_SCRIPT
            if not script.exists():
                return {"ok": False, "error": f"OpenCode script not found: {script}"}
            subprocess.Popen(
                ["nohup", "bash", str(script)],
                stdout=open(log_dir / "opencode-stdout.log", "a"),
                stderr=open(log_dir / "opencode-stderr.log", "a"),
                stdin=subprocess.DEVNULL,
                cwd=str(REPO_ROOT),
                start_new_session=True
            )
        else:
            return {"ok": False, "error": f"Unknown engine: {engine}"}

        time.sleep(1)
        status = gather_status()
        if status["loop"]["running"]:
            return {"ok": True, "message": f"{engine} loop started", "pid": status["loop"]["pid"], "engine": engine}
        else:
            return {"ok": False, "error": f"{engine} loop failed to start. Check logs/{engine}-stderr.log"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def stop_loop() -> dict:
    """Stop the running loop."""
    status = gather_status()
    pid = status["loop"]["pid"]
    engine = status["engine"]["active"]

    if not pid:
        return {"ok": True, "message": "Loop not running"}

    STOP_FLAG.touch()

    if status["loop"]["running"]:
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)
            if is_process_running(pid):
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)
        except ProcessLookupError:
            pass

    OPENCODE_PID_FILE.unlink(missing_ok=True)
    QWEN_PID_FILE.unlink(missing_ok=True)
    CODEX_PID_FILE.unlink(missing_ok=True)

    return {"ok": True, "message": f"{engine} loop stopped"}