# Auto Company — Fully Autonomous AI Company

## Project Overview

**Auto Company** is an experimental autonomous AI company that runs 24/7 without human intervention. It consists of 14 AI agents, each modeled after world-class experts in their domain (Jeff Bezos, DHH, Charlie Munger, etc.). The agents ideate products, make decisions, write code, deploy, and market — all autonomously.

### Core Architecture

```
daemon (launchd / systemd --user, auto-restart on crash)
  └── scripts/core/auto-loop.sh (continuous loop)
        ├── reads PROMPT.md + consensus.md
        ├── LLM CLI call (Codex CLI / Claude Code / Qwen)
        │   ├── reads CLAUDE.md (charter + guardrails)
        │   ├── reads .claude/skills/team/SKILL.md (teaming method)
        │   ├── forms an Agent Team (3-5 agents)
        │   ├── executes: research, coding, deploy, marketing
        │   └── updates memories/consensus.md (handoff baton)
        ├── failure handling: rate-limit wait / circuit breaker / consensus rollback
        └── sleep -> next cycle
```

Each cycle is an independent CLI call. `memories/consensus.md` is the only cross-cycle state.

### Supported Platforms

| Platform | Daemon System | Entry Point |
|----------|---------------|-------------|
| macOS | launchd | `make start` / `make install` |
| Windows + WSL2 | systemd --user | `.\scripts\windows\start-win.ps1` |
| Linux | systemd --user | `make start` / `make install` |

### Available Engines

| Engine | Script | CLI Required |
|--------|--------|--------------|
| Codex | `auto-loop.sh` | `codex` (OpenAI) |
| OpenCode | `auto-loop-opencode.sh` | `opencode` |
| Qwen | `auto-loop-qwen.sh` | Qwen API |

---

## Project Structure

```
auto-company/
├── CLAUDE.md              # Company charter (mission + guardrails + team + workflows)
├── PROMPT.md              # Per-cycle execution prompt (convergence rules)
├── INDEX.md               # Script index + responsibility table
├── Makefile               # Common command entry
├── QWEN.md                # This file - development context
├── scripts/
│   ├── core/              # Core loop and control scripts
│   │   ├── auto-loop.sh           # Codex CLI loop
│   │   ├── auto-loop-opencode.sh  # OpenCode CLI loop
│   │   ├── auto-loop-qwen.sh      # Qwen CLI loop
│   │   ├── monitor.sh             # Status monitor
│   │   └── stop-loop.sh           # Stop control
│   ├── windows/           # Windows entry/guardian/autostart scripts
│   ├── wsl/               # WSL systemd --user daemon scripts
│   └── macos/             # macOS launchd daemon scripts
├── memories/
│   └── consensus.md       # Shared handoff memory across cycles
├── docs/                  # Agent outputs (14 role folders + windows-setup.md)
├── projects/              # Workspace for generated projects
├── logs/                  # Loop execution logs
├── dashboard/             # Local web status dashboard
│   ├── server.py          # Linux/WSL dashboard server
│   ├── server-macos.py    # macOS dashboard server
│   └── ...
└── .claude/
    ├── agents/            # 14 agent definitions (expert personas)
    ├── skills/            # 30+ reusable skills
    └── settings.json      # Permissions + Agent Teams switch
```

---

## 14 AI Agent Team

### Strategy Layer

| Agent | Expert Persona | When to Use |
|-------|----------------|-------------|
| `ceo-bezos` | Jeff Bezos | Strategic decisions, PR/FAQ, flywheel thinking, Day 1 mindset |
| `cto-vogels` | Werner Vogels | Architecture design, technical selection, reliability decisions |
| `critic-munger` | Charlie Munger | Pre-mortem, inversion, challenge feasibility, prevent group delusion |

### Product Layer

| Agent | Expert Persona | When to Use |
|-------|----------------|-------------|
| `product-norman` | Don Norman | Product features, usability, human-centered design |
| `ui-duarte` | Matias Duarte | Visual design, Material Design, typography |
| `interaction-cooper` | Alan Cooper | User flows, persona-driven design, interaction patterns |

### Engineering Layer

| Agent | Expert Persona | When to Use |
|-------|----------------|-------------|
| `fullstack-dhh` | DHH | Code implementation, convention over configuration |
| `qa-bach` | James Bach | Test strategy, exploratory testing, quality risk assessment |
| `devops-hightower` | Kelsey Hightower | Deployment, CI/CD, infrastructure, observability |

### Business Layer

| Agent | Expert Persona | When to Use |
|-------|----------------|-------------|
| `marketing-godin` | Seth Godin | Positioning, purple cow, permission marketing |
| `operations-pg` | Paul Graham | Zero-to-one growth, "do things that don't scale" |
| `sales-ross` | Aaron Ross | Predictable revenue, funnel systems, conversion |
| `cfo-campbell` | Patrick Campbell | Pricing strategy, unit economics, financial modeling |

### Intelligence Layer

| Agent | Expert Persona | When to Use |
|-------|----------------|-------------|
| `research-thompson` | Ben Thompson | Market research, competitor analysis, aggregation theory |

Agent definitions are in `.claude/agents/<role>-<expert>.md`.

---

## Skills Arsenal (30+)

All skills are under `.claude/skills/`. Key categories:

### Research & Intelligence
- `deep-research`, `web-scraping`, `websh`, `deep-reading-analyst`, `competitive-intelligence-analyst`, `github-explorer`

### Strategy & Business
- `product-strategist`, `market-sizing-analysis`, `startup-business-models`, `micro-saas-launcher`

### Finance & Pricing
- `startup-financial-modeling`, `financial-unit-economics`, `pricing-strategy`

### Critical Thinking & Risk
- `premortem`, `scientific-critical-thinking`, `deep-analysis`

### Engineering & Security
- `code-review-security`, `security-audit`, `devops`, `tailwind-v4-shadcn`

### UX & Experience
- `ux-audit-rethink`, `user-persona-creation`, `user-research-synthesis`

### Marketing & Growth
- `seo-content-strategist`, `content-strategy`, `seo-audit`, `email-sequence`, `ph-community-outreach`, `community-led-growth`, `cold-email-sequence-generator`

### Quality
- `senior-qa`

### Internal Utilities
- `team`, `find-skills`, `skill-creator`, `agent-browser`

---

## Commands

### Quick Reference

```bash
# Show all commands
make help

# Start/Stop
make start           # Foreground start
make stop            # Stop loop

# Daemon mode (macOS/Linux)
make install         # Install as daemon (auto-start + auto-restart)
make uninstall       # Remove daemon
make pause           # Pause daemon
make resume          # Resume daemon

# Monitoring
make status          # Show status + latest consensus
make monitor         # Live log tail (Ctrl+C to exit)
make last            # Show last cycle output
make cycles          # Show cycle history summary

# Maintenance
make clean-logs      # Remove all cycle logs
make reset-consensus # Reset consensus to initial state (CAUTION!)

# Interactive
make team            # Start interactive CLI session
```

### Configuration (Environment Variables)

```bash
MODEL=gpt-5.3-codex make start             # Model override
LOOP_INTERVAL=60 make start                # 60s interval (default 30)
CYCLE_TIMEOUT_SECONDS=3600 make start      # 1h cycle timeout (default 1800)
MAX_CONSECUTIVE_ERRORS=3 make start        # Circuit-breaker threshold (default 5)
```

### Web Dashboard (Enhanced Edition)

```bash
# Enhanced Dashboard (推荐)
python3 dashboard/server-enhanced.py --host 0.0.0.0 --port 8787

# macOS Basic
python3 dashboard/server-macos.py --port 8787
```

Then open http://服务器IP:8787 in browser.

**Dashboard 功能:**

| Tab | 功能 |
|-----|------|
| **📊 概览** | 共识文件、运行状态、Agent 活动时间线 |
| **📁 产出物** | 文件树导航 + Markdown/代码预览 + 下载 |
| **📜 日志** | 主日志/周期日志切换 + 搜索过滤 |
| **🔄 周期历史** | 所有周期日志列表，点击查看详情 |

**API 端点:**

| API | 说明 |
|-----|------|
| `/api/status` | 完整状态信息 |
| `/api/files?dir=docs` | 文件列表 (docs/projects/logs) |
| `/api/file/<path>` | 文件内容预览 |
| `/api/download/<path>` | 文件下载 |
| `/api/cycles` | 周期日志列表 |
| `/api/cycle/<filename>` | 单个周期日志内容 |
| `/api/activities` | Agent 活动记录 |

---

## Operating Model

### Decision Principles

1. **Ship > Plan > Discuss** — if you can ship, do not over-discuss
2. **Act at 70% information** — waiting for 90% is usually too slow
3. **Customer-first** — build for real demand, not internal hype
4. **Prefer simplicity** — do not split what one person can finish
5. **Ramen profitability first** — revenue before vanity growth
6. **Boring technology first** — use proven tech unless new tech gives clear 10x upside
7. **Monolith first** — get it running first, split only when needed

### Convergence Rules (Mandatory)

| Cycle | Action |
|-------|--------|
| Cycle 1 | Brainstorm — each agent proposes ideas, rank top 3 |
| Cycle 2 | Validate #1 — Munger pre-mortem + Thompson market check + Campbell economics → **GO / NO-GO** |
| Cycle 3+ | GO → create repo, build, deploy. NO-GO → try next idea. **Discussion-only loops forbidden** |
| Cycle 2+ | **Must produce tangible output** (file, repo, deployment). Pure discussion prohibited |

### Six Standard Workflows

| # | Workflow | Collaboration Chain |
|---|----------|---------------------|
| 1 | New Product Evaluation | Research → CEO → Munger → Product → CTO → CFO |
| 2 | Feature Development | Interaction → UI → Full-stack → QA → DevOps |
| 3 | Product Launch | QA → DevOps → Marketing → Sales → Ops → CEO |
| 4 | Pricing and Monetization | Research → CFO → Sales → Munger → CEO |
| 5 | Weekly Review | Ops → Sales → CFO → QA → CEO |
| 6 | Opportunity Discovery | Research → CEO → Munger → CFO |

---

## Safety Guardrails (Non-Negotiable)

| Forbidden | Details |
|-----------|---------|
| Delete GitHub repositories | No `gh repo delete` or equivalent destructive repo actions |
| Delete Cloudflare projects | No `wrangler delete` for Workers/Pages/KV/D1/R2 |
| Delete system files | No `rm -rf /`; never touch `~/.ssh/`, `~/.config/`, `~/.claude/` |
| Illegal activity | No fraud, infringement, data theft, or unauthorized access |
| Leak credentials | Never commit keys/tokens/passwords to public repos/logs |
| Force-push protected branches | No `git push --force` to main/master |
| Destructive git reset on shared branches | `git reset --hard` only on disposable temporary branches |

**Allowed:** create repos, deploy projects, create branches, commit code, install dependencies.

**Workspace rule:** all new projects must be created under `projects/`.

---

## Documentation Map

Each agent stores outputs under `docs/<role>/`:

| Agent | Directory | Typical Outputs |
|-------|-----------|-----------------|
| `ceo-bezos` | `docs/ceo/` | PR/FAQ, strategic memos, decision records |
| `cto-vogels` | `docs/cto/` | ADRs, system design, technical selection notes |
| `critic-munger` | `docs/critic/` | Inversion reports, pre-mortems, veto logs |
| `product-norman` | `docs/product/` | Product specs, personas, usability analysis |
| `ui-duarte` | `docs/ui/` | Design systems, visual guidelines, color systems |
| `interaction-cooper` | `docs/interaction/` | Interaction flows, personas, navigation structures |
| `fullstack-dhh` | `docs/fullstack/` | Implementation notes, code docs, refactor logs |
| `qa-bach` | `docs/qa/` | Test strategies, bug reports, quality assessments |
| `devops-hightower` | `docs/devops/` | Deployment configs, runbooks, monitoring design |
| `marketing-godin` | `docs/marketing/` | Positioning, content strategy, campaign plans |
| `operations-pg` | `docs/operations/` | Growth experiments, retention analysis, ops metrics |
| `sales-ross` | `docs/sales/` | Funnel analysis, conversion plans, pricing playbooks |
| `cfo-campbell` | `docs/cfo/` | Financial models, pricing analyses, unit economics |
| `research-thompson` | `docs/research/` | Market/competitor/trend intelligence |

---

## Consensus Memory

`memories/consensus.md` is the cross-cycle baton. It must be updated before each cycle ends.

Required sections:
- Last Updated
- Current Phase (Day 0 / Exploring / Building / Launching / Growing)
- What We Did This Cycle
- Key Decisions Made
- Agent Activities This Cycle
- Active Projects
- Next Action
- Company State
- Open Questions

---

## Communication Norms

- Keep communication concise and actionable
- Resolve disagreements with evidence; CEO makes final calls
- Every discussion ends with a concrete Next Action
- Use Chinese for communication, keep technical terms in English

---

## Dependencies

| Dependency | Notes |
|------------|-------|
| Codex CLI / Claude Code / Qwen | Supported CLI engines |
| macOS or Linux/WSL2 | macOS uses launchd; Linux/WSL uses systemd --user |
| `make` | Start/stop/monitor command entry |
| `jq` | Recommended for log processing |
| `gh` | Optional, GitHub CLI |
| `wrangler` | Optional, Cloudflare CLI |

---

## Current Project State

According to `memories/consensus.md`:

- **Current Phase**: Self-Improvement
- **Active Projects**: 
  - Auto Company optimization (P0)
  - EmailGuard v0.1.0 (Released)
  - DevPulse (Phase 0 validation)
- **Tech Stack**: Python 3.11+ + FastAPI + Docker
- **Revenue**: $0
- **Users**: 0
- **GitHub**: https://github.com/nickdeng1/Auto-Company

---

## Disclaimer

This is an **experimental project**:

- Daemon mode works on macOS (launchd) and Linux/WSL (systemd --user)
- Windows entry requires WSL — PowerShell is only the control layer
- Still under test — runs, but stability is not guaranteed
- Each cycle consumes model quota
- Fully autonomous — agents act without approval prompts
- No warranty — review `docs/` and `projects/` regularly

Suggested rollout: start with foreground mode (`make start`), then move to daemon mode (`make install`).