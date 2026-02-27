#!/bin/bash
# ============================================================
# Auto Company — Codex Loop (Backward-Compatible Wrapper)
# ============================================================
# This is a thin wrapper for backward compatibility.
# Delegates to the unified auto-loop.sh with ENGINE=codex.
#
# Note: The original script has been backed up as auto-loop.sh.bak
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

exec env ENGINE=codex "$SCRIPT_DIR/auto-loop.sh" "$@"