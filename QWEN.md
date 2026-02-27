# Auto Company — AI 自主公司项目

## 项目概述

**Auto Company** 是一个全自主运行的 AI 公司实验项目，由 14 个 AI Agent 组成，模拟真实公司的完整运营流程。项目基于 Claude Code 的 Agent Teams 功能驱动，实现 24/7 不间断的自主决策、产品开发、部署上线和营销推广。

### 核心特点

- **完全自主**: AI 团队自主决策，无需人类参与日常运营
- **专家人格**: 14 个 Agent 分别模拟各领域顶尖专家的思维模式（Bezos、DHH、Kelsey Hightower 等）
- **永续循环**: 通过共识记忆机制 (`memories/consensus.md`) 实现跨周期任务接力
- **安全红线**: 内置严格的安全限制，防止破坏性操作

### 架构概览

```
launchd (崩溃自重启)
  └── auto-loop.sh (永续循环)
        ├── 读 PROMPT.md + consensus.md
        ├── claude -p (驱动一个工作周期)
        │   ├── 读 CLAUDE.md (公司章程 + 安全红线)
        │   ├── 读 .claude/skills/team/SKILL.md (组队方法)
        │   ├── 组建 Agent Team (3-5 人)
        │   ├── 执行：调研、写码、部署、营销
        │   └── 更新 memories/consensus.md (传递接力棒)
        ├── 失败处理：限额等待 / 熔断保护 / consensus 回滚
        └── sleep → 下一轮
```

---

## 项目结构

```
auto-company/
├── CLAUDE.md              # 公司章程（使命 + 安全红线 + 团队定义）
├── PROMPT.md              # 每轮工作指令（收敛规则 + 验证机制）
├── AGENTS.md              # 项目说明文档
├── QWEN.md                # 本文件 - 开发上下文指南
├── Makefile               # 常用命令快捷方式
├── auto-loop.sh           # 主循环脚本（Bash 版本）
├── auto-loop.py           # 主循环脚本（Python 版本，使用 NVIDIA API）
├── stop-loop.sh           # 停止/暂停/恢复循环
├── monitor.sh             # 实时监控工具
├── install-daemon.sh      # launchd 守护进程安装器
├── memories/
│   └── consensus.md       # 共识记忆（跨周期接力棒）
├── docs/                  # Agent 工作产出（14 个子目录）
│   ├── ceo/               # CEO 战略决策文档
│   ├── cfo/               # 财务分析和定价文档
│   ├── cto/               # 技术架构和选型文档
│   ├── critic/            # 逆向分析和风险评估
│   ├── devops/            # 部署和运维文档
│   ├── fullstack/         # 开发技术方案文档
│   ├── interaction/       # 交互设计文档
│   ├── marketing/         # 营销策略文档
│   ├── operations/        # 运营增长文档
│   ├── product/           # 产品需求文档
│   ├── qa/                # 测试策略文档
│   ├── research/          # 市场调研文档
│   ├── sales/             # 销售策略文档
│   └── ui/                # UI 设计规范文档
├── projects/              # 所有新建项目的工作空间
├── data/
│   ├── inputs/            # 输入数据
│   └── outputs/           # 输出数据
├── logs/                  # 循环执行日志
├── agents/                # 功能验证器和影子测试器
└── .claude/
    ├── agents/            # 14 个 Agent 定义文件（.md）
    ├── skills/            # 30+ 技能模块
    └── settings.json      # Claude Code 配置
```

---

## 14 个 AI Agent 团队

### 战略层

| Agent | 专家 | 职责 |
|-------|------|------|
| `ceo-bezos` | Jeff Bezos | 战略决策、PR/FAQ、飞轮效应、Day 1 心态 |
| `cto-vogels` | Werner Vogels | 技术架构、API First、为失败而设计 |
| `critic-munger` | Charlie Munger | 逆向思维、Pre-Mortem、识别认知偏见 |

### 产品层

| Agent | 专家 | 职责 |
|-------|------|------|
| `product-norman` | Don Norman | 产品功能定义、可用性评估、以人为本设计 |
| `ui-duarte` | Matías Duarte | 视觉设计、Material 设计系统、Typography |
| `interaction-cooper` | Alan Cooper | 交互流程、Persona 驱动、目标导向设计 |

### 工程层

| Agent | 专家 | 职责 |
|-------|------|------|
| `fullstack-dhh` | DHH | 全栈开发、约定优于配置、Majestic Monolith |
| `qa-bach` | James Bach | 探索性测试、质量风险评估 |
| `devops-hightower` | Kelsey Hightower | DevOps、Serverless、自动化运维 |

### 商业层

| Agent | 专家 | 职责 |
|-------|------|------|
| `marketing-godin` | Seth Godin | 紫牛理论、许可营销、品牌建设 |
| `operations-pg` | Paul Graham | 冷启动、Do Things That Don't Scale |
| `sales-ross` | Aaron Ross | 可预测收入、销售漏斗、转化率优化 |
| `cfo-campbell` | Patrick Campbell | 定价策略、单位经济学、财务建模 |

### 情报层

| Agent | 专家 | 职责 |
|-------|------|------|
| `research-thompson` | Ben Thompson | 市场调研、竞品分析、聚合理论 |

---

## 构建和运行

### 环境要求

- **macOS** — 使用 `launchd` 管理守护进程（Linux/systemd 尚未支持）
- **Claude Code CLI** — 必须安装并登录
- **Claude 订阅** — 推荐 Max 或 Pro（24/7 运行需要持续额度）
- **可选工具**: `jq`（解析 JSON）、`gh`（GitHub CLI）、`wrangler`（Cloudflare CLI）

### 常用命令

```bash
# 查看所有命令
make help

# 启动和停止
make start           # 前台启动循环
make start-awake     # 前台启动 + 防止 macOS 睡眠
make stop            # 停止循环
make install         # 安装为守护进程（开机自启 + 崩溃自重启）
make uninstall       # 卸载守护进程

# 监控和日志
make status          # 查看状态 + 最新共识
make monitor         # 实时跟踪日志（Ctrl+C 退出）
make last            # 查看上一轮完整输出
make cycles          # 查看历史周期摘要

# 控制
make pause           # 暂停（不自动拉起）
make resume          # 恢复
make awake           # 为当前运行 PID 挂防睡眠
make team            # 启动交互式 Claude 会话（带 /team 技能）

# 维护
make clean-logs      # 清理所有周期日志
make reset-consensus # 重置共识到初始状态（谨慎使用！）
```

### 配置（环境变量）

```bash
MODEL=sonnet make start                    # 切换模型（默认 opus）
LOOP_INTERVAL=60 make start                # 60 秒间隔（默认 30）
CYCLE_TIMEOUT_SECONDS=3600 make start      # 单轮超时 1 小时（默认 1800）
MAX_CONSECUTIVE_ERRORS=3 make start        # 熔断阈值（默认 5）
```

---

## 开发指南

### 工作周期流程

1. **读取共识**: 从 `memories/consensus.md` 加载当前状态
2. **决策**: 根据共识决定下一步行动
3. **组队执行**: 选择 3-5 个最相关的 Agent 组建团队
4. **更新共识**: 将本轮成果写入共识文件

### 收敛规则（防止无限讨论）

| 周期 | 动作 |
|------|------|
| Cycle 1 | 头脑风暴——每个 Agent 提一个想法，排出 top 3 |
| Cycle 2 | 验证 #1——Munger 做 Pre-Mortem，Thompson 验证市场，Campbell 算账 → **GO / NO-GO** |
| Cycle 3+ | GO → 建 repo 写代码部署。NO-GO → 试下一个。**纯讨论禁止** |

### 六大标准流程

| # | 流程 | 协作链 |
|---|------|--------|
| 1 | **新产品评估** | 调研 → CEO → Munger → 产品 → CTO → CFO |
| 2 | **功能开发** | 交互 → UI → 全栈 → QA → DevOps |
| 3 | **产品发布** | QA → DevOps → 营销 → 销售 → 运营 → CEO |
| 4 | **定价变现** | 调研 → CFO → 销售 → Munger → CEO |
| 5 | **每周复盘** | 运营 → 销售 → CFO → QA → CEO |
| 6 | **机会发现** | 调研 → CEO → Munger → CFO |

### 添加新 Agent

1. 在 `.claude/agents/` 创建 `<role>-<expert>.md` 文件
2. 定义 Agent 的人格、触发场景和职责
3. 在 `CLAUDE.md` 的"团队架构"章节添加说明
4. 在 `docs/` 下创建对应的子目录

### 添加新技能

1. 在 `.claude/skills/` 创建新目录
2. 添加 `SKILL.md` 描述技能的使用方法
3. 可选：添加示例文件或模板

### 技能武器库（30+）

位于 `.claude/skills/`，包括：

- **调研情报**: `deep-research`, `web-scraping`, `competitive-intelligence-analyst`, `github-explorer`
- **战略商业**: `product-strategist`, `market-sizing-analysis`, `startup-business-models`
- **财务定价**: `startup-financial-modeling`, `financial-unit-economics`, `pricing-strategy`
- **批判风控**: `premortem`, `scientific-critical-thinking`, `deep-analysis`
- **工程安全**: `code-review-security`, `security-audit`, `devops`
- **设计体验**: `ux-audit-rethink`, `user-persona-creation`, `user-research-synthesis`
- **营销增长**: `seo-content-strategist`, `content-strategy`, `ph-community-outreach`, `community-led-growth`
- **质量保障**: `senior-qa`

---

## 安全红线

绝对禁止的操作：

| 禁止 | 具体 |
|------|------|
| 删除 GitHub 仓库 | `gh repo delete` 及一切删库操作 |
| 删除 Cloudflare 项目 | `wrangler delete`，不删 Workers/Pages/KV/D1/R2 |
| 删除系统文件 | `rm -rf /`，不碰 `~/.ssh/`、`~/.config/`、`~/.claude/` |
| 非法活动 | 欺诈、侵权、数据窃取、未授权访问 |
| 泄露凭证 | API keys/tokens/passwords 不进公开仓库或日志 |
| Force push 主分支 | `git push --force` 到 main/master |
| 破坏性 git 操作 | `git reset --hard` 仅限临时分支 |

**允许的操作**: 创建仓库 ✅ 部署项目 ✅ 创建分支 ✅ 提交代码 ✅ 安装依赖 ✅

**工作空间**: 所有新项目必须在 `projects/` 目录下创建。

---

## 测试实践

### 功能验证机制

项目实现了三层验收流程：

1. **功能验证** — 检测代码真实性（禁止模拟代码）
2. **自动修复** — 检测并修复模拟代码
3. **用户场景测试** — 确保真实使用体验

### 禁止虚假完成

```
❌ 禁止的行为:
├─ shutil.copy2() 复制文件模拟处理
├─ 只返回固定值 (True/False)
├─ "Coming Soon", "TODO", "PLACEHOLDER"
├─ "Lorem ipsum", "mock_data", "stub_data"
└─ 模拟代码模式
```

### 验证命令

```validate
target: <验证对象描述>
type: video_generation|api_endpoint|web_flask|general
```

---

## 协作规范

- **沟通语言**: 中文沟通，技术术语保留英文
- **决策原则**: Ship > Plan > Discuss
- **分歧处理**: 摆论据，CEO 拍板
- **输出要求**: 每次讨论必有 Next Action

### 文档管理

每个 Agent 产出存放在 `docs/<role>/`：

| Agent | 目录 | 产出内容 |
|-------|------|----------|
| `ceo-bezos` | `docs/ceo/` | PR/FAQ、战略备忘录、决策记录 |
| `cto-vogels` | `docs/cto/` | ADR、系统设计、技术选型 |
| `critic-munger` | `docs/critic/` | 逆向分析报告、Pre-Mortem、否决记录 |
| `product-norman` | `docs/product/` | 产品 Spec、用户画像、可用性分析 |
| `ui-duarte` | `docs/ui/` | 设计系统、视觉规范、配色方案 |
| `interaction-cooper` | `docs/interaction/` | 交互流程、Persona、导航结构 |
| `fullstack-dhh` | `docs/fullstack/` | 技术方案、代码文档、重构记录 |
| `qa-bach` | `docs/qa/` | 测试策略、Bug 报告、质量评估 |
| `devops-hightower` | `docs/devops/` | 部署配置、Runbook、监控方案 |
| `marketing-godin` | `docs/marketing/` | 产品定位、内容策略、传播计划 |
| `operations-pg` | `docs/operations/` | 增长实验、留存分析、运营指标 |
| `sales-ross` | `docs/sales/` | 销售漏斗、转化分析、定价方案 |
| `cfo-campbell` | `docs/cfo/` | 财务模型、定价分析、单位经济学 |
| `research-thompson` | `docs/research/` | 市场调研、竞品分析、行业趋势 |

---

## 相关文档

| 文件 | 说明 |
|------|------|
| `README.md` | 项目介绍和快速开始 |
| `CLAUDE.md` | 公司章程（使命、安全红线、团队、流程） |
| `PROMPT.md` | 每轮工作指令和收敛规则 |
| `AGENTS.md` | 项目详细说明文档 |
| `IMPLEMENTATION_PLAN.md` | 根本性改进方案 |
| `WEB_UI_GUIDE.md` | Web UI 使用指南 |
| `TASK_CHECKLIST.md` | 任务检查清单 |

---

## 注意事项

⚠️ **实验项目警告**:

- 仅支持 macOS（Linux/systemd 尚未实现）
- 还在测试中，能跑但不保证稳定
- 每个周期消耗 Claude API 额度或订阅配额
- AI 团队自主决策，不会询问人类
- 建议先用 `make start` 前台观察，确认无误后再 `make install`

---

## 当前项目状态

根据最新共识 (`memories/consensus.md`)：

- **当前阶段**: Testing Complete
- **活跃项目**: AI 数字口播主播 (ai-digital-anchor)
- **技术栈**: Flask + Python 3.6 + TTS
- **服务地址**: http://192.168.23.146:5000
- **产品版本**: v1.1.0
- **收入**: $0
- **用户**: 0
