#!/bin/bash
# ============================================================
# Auto Company — Unified Auto Loop
# ============================================================
# Unified entry point for all AI engines (codex, qwen, opencode).
# Uses engine adapters for engine-specific behavior.
#
# Usage:
#   ./auto-loop.sh                    # Run with default engine (qwen)
#   ENGINE=codex ./auto-loop.sh       # Run with Codex
#   ENGINE=qwen ./auto-loop.sh        # Run with Qwen
#   ENGINE=opencode ./auto-loop.sh    # Run with OpenCode
#
# Stop:
#   ./stop-loop.sh                    # Graceful stop
#   kill $(cat .auto-loop-<engine>.pid)  # Force stop
#
# Config (env vars, see lib/config.sh):
#   ENGINE=...                        # AI engine (codex/qwen/opencode, default: qwen)
#   MODEL=...                         # Model override
#   LOOP_INTERVAL=30                  # Seconds between cycles
#   CYCLE_TIMEOUT_SECONDS=1800        # Max seconds per cycle
#   MAX_CONSECUTIVE_ERRORS=5          # Circuit breaker threshold
#   COOLDOWN_SECONDS=300              # Cooldown after circuit break
#   LIMIT_WAIT_SECONDS=3600           # Wait on usage limit
#   MAX_LOGS=200                      # Max cycle logs to keep
# ============================================================

set -euo pipefail

# === Load Configuration ===
# All paths and settings are centralized in config.sh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib/config.sh
source "$SCRIPT_DIR/lib/config.sh"

# === Setup Engine-specific Paths ===
setup_engine_paths

# === Load Common Library ===
# shellcheck source=lib/common.sh
source "$LIB_DIR/common.sh"

# === Load Engine Adapter ===
# shellcheck source=lib/engine-<engine>.sh
source "$LIB_DIR/engine-${ENGINE}.sh"

# === Dependency Checks ===

if [ ! -f "$PROMPT_FILE" ]; then
    echo "Error: PROMPT.md not found at $PROMPT_FILE"
    exit 1
fi

# === Initialization ===

setup_project
check_existing_instance
engine_init
write_pid_file
setup_traps
init_counters

# Log startup information
engine_log_startup

# === Main Loop ===

while true; do
    # Check for stop request
    if check_stop_requested; then
        log "Stop requested. Shutting down gracefully."
        cleanup
    fi

    loop_count=$((loop_count + 1))
    cycle_log="$LOG_DIR/cycle-${ENGINE}-$(printf '%04d' "$loop_count")-$(date '+%Y%m%d-%H%M%S').log"

    log_cycle "$loop_count" "START" "Beginning work cycle"
    save_state "running"

    # Log rotation
    rotate_logs

    # Backup consensus before cycle
    backup_consensus

    # Build prompt with consensus pre-injected
    FULL_PROMPT=$(build_full_prompt "$loop_count")

    # Run engine cycle
    run_engine_cycle "$FULL_PROMPT"

    # Extract metadata for logging
    extract_cycle_metadata

    # Process result
    process_cycle_result "$loop_count" "$cycle_log" "$RESULT_TEXT"

    # Commit consensus if cycle succeeded
    git_commit_consensus "$loop_count" 2>/dev/null || true

    save_state "idle"
    log_cycle "$loop_count" "WAIT" "Sleeping ${LOOP_INTERVAL}s before next cycle..."
    sleep "${LOOP_INTERVAL}"
done