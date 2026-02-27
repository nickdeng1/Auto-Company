# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This directory contains the core orchestration shell scripts for the Auto Company autonomous loop system. These scripts continuously drive an AI team by running an AI CLI (Codex, Qwen, or OpenCode) in a headless cycle, using `memories/consensus.md` as the "relay baton" between cycles.

## Script Inventory

| Script | Engine | PID File |
|--------|--------|----------|
| `auto-loop.sh` | Codex CLI (`codex exec`) | `.auto-loop.pid` |
| `auto-loop-qwen.sh` | Qwen Code CLI (`qwen --yolo`) | `.auto-loop-qwen.pid` |
| `auto-loop-opencode.sh` | OpenCode CLI (`opencode run`) | `.auto-loop-opencode.pid` |
| `monitor.sh` | — | reads `.auto-loop-state` |
| `stop-loop.sh` | — | reads `.auto-loop.pid` |

## Running the Loop

All commands are run from the **project root** (`Auto-Company/`), not from this directory:

```bash
make start              # Start Codex loop (foreground)
make start-awake        # Start + prevent macOS sleep
make stop               # Graceful stop
make status             # Status + latest consensus
make monitor            # Tail live logs
make last               # Show last cycle's full output
make cycles             # Cycle history summary
make pause              # Pause daemon (no auto-restart)
make resume             # Resume paused daemon
make install            # Install as launchd (macOS) or systemd (Linux)
make clean-logs         # Remove cycle logs
make reset-consensus    # Reset consensus.md to initial state (destructive)
```

Alternative: run scripts directly from project root:
```bash
./scripts/core/auto-loop-qwen.sh        # Qwen engine
./scripts/core/auto-loop-opencode.sh    # OpenCode engine
./scripts/core/stop-loop.sh             # Stop any loop
```

## Key Architecture

### The Cycle Loop

Each script follows the same pattern:
1. Reads `PROMPT.md` + `memories/consensus.md`
2. Injects consensus as runtime context into the full prompt
3. Runs the AI CLI headlessly with a per-cycle timeout watchdog
4. Validates `memories/consensus.md` was updated (must contain `# Auto Company Consensus`, `## Next Action`, `## Company State` headers)
5. On hard failure: restores consensus from `.bak`, increments error counter
6. Circuit breaker trips at `MAX_CONSECUTIVE_ERRORS` (default: 5), then cools down `COOLDOWN_SECONDS` (default: 300s)
7. On API usage limit detection: waits `LIMIT_WAIT_SECONDS` (default: 3600s)
8. Sleeps `LOOP_INTERVAL` (default: 30s) between cycles

### Stop Mechanism

Two parallel stop signals are used:
- **Signal file**: creates `.auto-loop-stop` (checked at cycle start for graceful stop)
- **SIGTERM**: sent directly to the loop PID for immediate termination

### Consensus Validation

A cycle is considered successful only if `memories/consensus.md`:
- Is non-empty
- Contains `^# Auto Company Consensus`
- Contains `^## Next Action`
- Contains `^## Company State`

A timed-out cycle is treated as a soft-success if consensus was updated.

## Environment Variables

All loops respect these overrides (set before running):

```bash
LOOP_INTERVAL=30            # Seconds between cycles
CYCLE_TIMEOUT_SECONDS=1800  # Max seconds per cycle
MAX_CONSECUTIVE_ERRORS=5    # Circuit breaker threshold
COOLDOWN_SECONDS=300        # Cooldown after circuit break
LIMIT_WAIT_SECONDS=3600     # Wait on API usage limit
MAX_LOGS=200                # Max cycle log files to retain
MODEL=...                   # Override model (engine-specific)
CODEX_BIN=...               # Override Codex binary path
QWEN_BIN=...                # Override Qwen binary path
CODEX_SANDBOX_MODE=danger-full-access  # Codex sandbox mode
```

## Log Files (relative to project root)

- `logs/auto-loop.log` — main Codex loop log
- `logs/auto-loop-qwen.log` — Qwen loop log
- `logs/auto-loop-opencode.log` — OpenCode loop log
- `logs/cycle-NNNN-TIMESTAMP.log` — per-cycle full output (Codex)
- `logs/cycle-qwen-NNNN-TIMESTAMP.log` — per-cycle output (Qwen)
- `logs/cycle-opencode-NNNN-TIMESTAMP.log` — per-cycle output (OpenCode)

Logs rotate at 10MB; cycle logs are trimmed to `MAX_LOGS` most recent.
