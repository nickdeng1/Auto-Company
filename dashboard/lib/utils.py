"""
Dashboard utility functions.
File reading, encoding detection, and helper functions.
"""

import json
from pathlib import Path
from typing import Any


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


def read_json_file(path: Path, fallback: dict = None) -> dict:
    """Read JSON file."""
    if fallback is None:
        fallback = {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def read_activities(activities_file: Path, limit: int = 100) -> list[dict]:
    """Read activities from JSONL file, newest first."""
    activities = []
    if not activities_file.exists():
        return activities

    try:
        lines = activities_file.read_text(encoding="utf-8").strip().split("\n")
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


def read_structured_logs(jsonl_file: Path, limit: int = 500) -> list[dict]:
    """Read structured JSON logs from .jsonl file, newest first."""
    logs = []
    if not jsonl_file.exists():
        return logs

    try:
        lines = jsonl_file.read_text(encoding="utf-8").strip().split("\n")
        for line in reversed(lines[-limit:]):
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    logs.append(entry)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return logs


def get_log_stats(logs: list[dict]) -> dict:
    """Get statistics from structured logs."""
    stats = {
        "total": len(logs),
        "by_event": {},
        "by_status": {},
        "errors": 0,
        "cycles": 0,
    }

    for entry in logs:
        event = entry.get("event", "unknown")
        stats["by_event"][event] = stats["by_event"].get(event, 0) + 1

        if event == "cycle":
            stats["cycles"] += 1
            status = entry.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            if status in ("FAIL", "BREAKER", "LIMIT"):
                stats["errors"] += 1

    return stats


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
    import os
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError, TypeError):
        return False


def get_process_info(pid: int) -> dict:
    """Get process info by PID."""
    import subprocess

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