"""
Tests for structured logging functionality.
"""

import json
import unittest
from pathlib import Path
import tempfile
import os

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.utils import read_structured_logs, get_log_stats


class TestReadStructuredLogs(unittest.TestCase):
    """Test reading structured JSON logs."""

    def test_empty_file(self):
        """Test reading from non-existent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nonexistent.jsonl"
            logs = read_structured_logs(path)
            self.assertEqual(logs, [])

    def test_single_entry(self):
        """Test reading single log entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.jsonl"
            entry = {"ts": "2026-02-27T10:00:00Z", "event": "log", "msg": "test message"}
            path.write_text(json.dumps(entry) + "\n")
            
            logs = read_structured_logs(path)
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]["event"], "log")
            self.assertEqual(logs[0]["msg"], "test message")

    def test_multiple_entries(self):
        """Test reading multiple entries, newest first."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.jsonl"
            entries = [
                {"ts": "2026-02-27T10:00:00Z", "event": "log", "msg": "first"},
                {"ts": "2026-02-27T10:01:00Z", "event": "cycle", "status": "START"},
                {"ts": "2026-02-27T10:02:00Z", "event": "cycle", "status": "OK"},
            ]
            path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
            
            logs = read_structured_logs(path)
            self.assertEqual(len(logs), 3)
            # Newest first
            self.assertEqual(logs[0]["status"], "OK")
            self.assertEqual(logs[2]["msg"], "first")

    def test_limit(self):
        """Test limit parameter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.jsonl"
            entries = [{"ts": f"2026-02-27T10:0{i}:00Z", "event": "log", "n": i} for i in range(10)]
            path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
            
            logs = read_structured_logs(path, limit=5)
            self.assertEqual(len(logs), 5)
            # Should get the last 5 (newest)
            self.assertEqual(logs[0]["n"], 9)

    def test_invalid_json_skipped(self):
        """Test that invalid JSON lines are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.jsonl"
            content = '{"ts": "2026-02-27T10:00:00Z", "event": "log"}\ninvalid json\n{"ts": "2026-02-27T10:01:00Z", "event": "cycle"}\n'
            path.write_text(content)
            
            logs = read_structured_logs(path)
            self.assertEqual(len(logs), 2)


class TestGetLogStats(unittest.TestCase):
    """Test log statistics calculation."""

    def test_empty_logs(self):
        """Test stats with empty logs."""
        stats = get_log_stats([])
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["cycles"], 0)
        self.assertEqual(stats["errors"], 0)

    def test_mixed_events(self):
        """Test stats with mixed events."""
        logs = [
            {"event": "log", "msg": "test"},
            {"event": "cycle", "status": "START"},
            {"event": "cycle", "status": "OK"},
            {"event": "cycle", "status": "FAIL"},
            {"event": "log", "msg": "another"},
        ]
        stats = get_log_stats(logs)
        
        self.assertEqual(stats["total"], 5)
        self.assertEqual(stats["cycles"], 3)
        self.assertEqual(stats["errors"], 1)
        self.assertEqual(stats["by_event"]["log"], 2)
        self.assertEqual(stats["by_event"]["cycle"], 3)
        self.assertEqual(stats["by_status"]["OK"], 1)
        self.assertEqual(stats["by_status"]["FAIL"], 1)

    def test_error_counting(self):
        """Test that error statuses are counted correctly."""
        logs = [
            {"event": "cycle", "status": "FAIL"},
            {"event": "cycle", "status": "BREAKER"},
            {"event": "cycle", "status": "LIMIT"},
            {"event": "cycle", "status": "OK"},
        ]
        stats = get_log_stats(logs)
        
        self.assertEqual(stats["errors"], 3)


if __name__ == "__main__":
    unittest.main()