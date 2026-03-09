#!/bin/bash
# ============================================================
# Auto Company — Test Claude Engine
# ============================================================
# Quick test script for the Claude engine adapter.
# Run this from terminal (not inside Claude Code).
#
# Usage:
#   ./test-claude-engine.sh
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load configuration
source "$SCRIPT_DIR/lib/config.sh"
ENGINE="claude"
setup_engine_paths

# Load common library
source "$LIB_DIR/common.sh"

# Load Claude engine adapter
source "$LIB_DIR/engine-claude.sh"

echo "=== Claude Engine Test ==="
echo ""

# Initialize engine
engine_init

echo "Resolved Claude binary: $RESOLVED_ENGINE_BIN"
echo ""

# Get version
VERSION=$("$RESOLVED_ENGINE_BIN" --version 2>/dev/null | head -n1 || echo "unknown")
echo "Claude version: $VERSION"
echo ""

# Test configuration
echo "Configuration:"
echo "  CLAUDE_MODEL: ${CLAUDE_MODEL:-<not set>}"
echo "  CLAUDE_TOOLS: ${CLAUDE_TOOLS}"
echo ""

# Create a simple test prompt
TEST_PROMPT="Hello! Please respond with a brief greeting and confirm you can see the project directory structure. List the top-level directories you can see."

echo "Running test prompt..."
echo "---"

# Create temp files
OUTPUT_FILE=$(mktemp)
PROMPT_FILE=$(mktemp)
echo "$TEST_PROMPT" > "$PROMPT_FILE"

# Run Claude (use default model if CLAUDE_MODEL not set)
set +e
cd "$PROJECT_DIR"

CMD=("$RESOLVED_ENGINE_BIN" -p "$PROMPT_FILE" --dangerously-skip-permissions)
if [ -n "${CLAUDE_MODEL:-}" ]; then
    CMD+=(--model "$CLAUDE_MODEL")
fi

"${CMD[@]}" 2>&1 | tee "$OUTPUT_FILE"
EXIT_CODE=$?
set -e

echo ""
echo "---"
echo "Exit code: $EXIT_CODE"

# Cleanup
rm -f "$OUTPUT_FILE" "$PROMPT_FILE"

echo ""
echo "Test complete!"