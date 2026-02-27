#!/bin/bash
# ============================================================
# Auto Company — OpenCode Loop (Backward-Compatible Wrapper)
# ============================================================
# This is a thin wrapper for backward compatibility.
# Delegates to the unified auto-loop.sh with ENGINE=opencode.
#
# Note: The original script has been backed up as auto-loop-opencode.sh.bak
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

exec env ENGINE=opencode "$SCRIPT_DIR/auto-loop.sh" "$@"