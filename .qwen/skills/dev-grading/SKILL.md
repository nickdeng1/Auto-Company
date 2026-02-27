---
name: dev-grading
description: 任务分级评估技能。通过关键词分析+代码扫描，自动评估需求复杂度，推荐L1/L2/L3级别。
---

# 任务分级评估 (Task Grading)

> 智能评估需求复杂度，自动推荐适合的开发流程级别

---

## 分级定义

| 级别 | 名称 | 适用场景 | 阶段数 | 确认点 |
|------|------|----------|--------|--------|
| **L1** | 简单任务 | Bug修复、配置调整、小改动 | 3 | 1 |
| **L2** | 中等任务 | 新字段、新组件、常规功能 | 5 | 2 |
| **L3** | 复杂任务 | 新模块、架构变更、跨领域 | 8 | 8 |

---

## 评估维度 (5维度打分)

| 维度 | L1 (1分) | L2 (2分) | L3 (3分) |
|------|----------|----------|----------|
| **范围** | 单模块 | 2-3模块 | 4+模块/跨服务 |
| **文件数** | 1-3个文件 | 4-10个文件 | 11+个文件 |
| **风险级别** | 低(工具/配置) | 中(业务逻辑) | 高(核心引擎/数据模型) |
| **模式匹配** | 复用现有模式 | 扩展现有模式 | 创建新模式 |
| **外部依赖** | 无外部依赖 | 内部服务调用 | 外部API/第三方 |

**分级规则**:
- L1: 总分 ≤ 6
- L2: 总分 7-11
- L3: 总分 ≥ 12

---

## 执行流程 (增强版)

```
需求描述输入
     ↓
┌─────────────────────────────────────┐
│ 1. 关键词分析                        │
│    - 提取模块相关关键词              │
│    - 识别风险指标词                  │
│    - 检测模式匹配线索                │
│    - 初步评分                        │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ 2. 代码库自动扫描 ★新增★            │
│    - 使用Grep定位相关文件            │
│    - 统计涉及文件数量                │
│    - 分析模块依赖关系                │
│    - 检测核心引擎改动                │
│    - 查找现有测试文件                │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ 3. 综合评分                          │
│    - 关键词分 × 0.3                  │
│    - 代码分析分 × 0.7                │
│    - 计算置信度                      │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ 4. 输出分级结果                      │
│    - 推荐级别                        │
│    - 打分详情                        │
│    - 代码扫描证据                    │
│    - 流程模板                        │
│    - 允许用户覆盖                    │
└─────────────────────────────────────┘
```

---

## 代码扫描规则 ★新增★

### 扫描策略

根据需求描述中的关键词，自动执行代码扫描：

```
关键词 → 搜索模式 → 扫描结果 → 评分
```

### 模块关键词→搜索模式

| 关键词 | 搜索路径 | 搜索模式 |
|--------|----------|----------|
| 表单、字段、form、field | `do1cloud-form/`, `bpms-component/do1cloud-model/form-model/` | `*Field*.java`, `*Form*.java` |
| 流程、审批、task、process | `do1cloud-bpmn/`, `bpms-runtime/workflow/` | `*Task*.java`, `*Process*.java` |
| 业务、页面、按钮、button | `do1cloud-business/`, `bpms-runtime/business/` | `*Button*.java`, `*Page*.java` |
| 同步、WeDoc、智能表格 | `bpms-runtime/form/**/wedoc/` | `*Sync*.java`, `*WeDoc*.java` |
| 定时、调度、scheduler | `bpms-runtime/scheduler/`, `fdn-scheduler/` | `*Scheduler*.java`, `*Trigger*.java` |
| 事件、event、aggregate | `qiqiao-framework-core/**/event/` | `*Event*.java`, `*Handler*.java` |

### 核心文件检测

以下路径的文件被视为核心文件（高风险）：

```
高风险路径:
- */engine/*
- */core/*
- */kernel/*
- */model/*Entity.java
- */service/*Service.java (核心服务)
```

### 扫描结果评分

```
文件数评分:
- 扫描到 1-3 个相关文件: 1分
- 扫描到 4-10 个相关文件: 2分
- 扫描到 11+ 个相关文件: 3分

模块数评分:
- 涉及 1 个模块目录: 1分
- 涉及 2-3 个模块目录: 2分
- 涉及 4+ 个模块目录: 3分

核心文件评分:
- 无核心文件: 1分
- 1-3 个核心文件: 2分
- 4+ 个核心文件: 3分

测试文件评分:
- 有对应测试文件: 1分
- 无测试文件需新建: 2分
- 复杂场景需多个测试: 3分
```

---

## 综合评分算法 ★新增★

```
最终分数 = 关键词分数 × 0.3 + 代码分析分数 × 0.7

置信度 = min(代码扫描命中文件数 / 预期文件数, 100%)

示例:
- 关键词分析: 范围2 + 风险2 + 模式2 + 依赖1 = 7分
- 代码扫描: 文件数2 + 模块数2 + 核心2 + 测试2 = 8分
- 最终分数: 7 × 0.3 + 8 × 0.7 = 2.1 + 5.6 = 7.7 → 取整8分 → L2
- 置信度: 扫描到8个文件 / 预期10个 = 80%
```

---

## 关键词→模块映射

| 关键词 | 模块 | 基础风险分 |
|--------|------|------------|
| config, parameter, setting, 配置 | 配置管理 | 1 |
| utility, helper, tool, 工具 | 工具类 | 1 |
| field, form, Document, 字段, 表单 | 表单引擎 | 2 |
| task, approval, process, 任务, 审批, 流程 | 流程引擎 | 2 |
| button, list, page, 按钮, 列表, 页面 | 业务引擎 | 2 |
| sync, WeDoc, 同步, 智能表格 | 智能表格同步 | 2 |
| scheduler, trigger, 定时, 调度 | 定时任务 | 2 |
| event, aggregate, 事件, 聚合 | 事件系统 | 2 |
| engine, core, kernel, 引擎, 核心 | 核心引擎 | 3 |
| data model, entity, schema, 数据模型 | 数据层 | 3 |
| refactor, redesign, 重构, 重新设计 | 架构变更 | 3 |

---

## 风险指标词

**高风险 (3分)**:
- 重构、重写、迁移、核心、引擎、架构、数据模型
- refactor, rewrite, migrate, core, engine, architecture

**中风险 (2分)**:
- 新增、扩展、集成、联动
- add, extend, integrate, linkage

**低风险 (1分)**:
- 修复、调整、配置、优化
- fix, adjust, config, optimize

---

## 输出格式 (增强版)

```
┌─────────────────────────────────────────────────────────────┐
│  📊 任务分级评估结果                                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  推荐级别: L2 (中等任务)                                     │
│  置信度: 85%                                                 │
│                                                              │
│  ═══ 关键词分析 (权重30%) ═══                               │
│  ├── 模块:       表单引擎, 业务引擎                          │
│  ├── 风险词:     "添加" (中风险)                             │
│  └── 初步分:     7/15                                        │
│                                                              │
│  ═══ 代码扫描 (权重70%) ═══                                 │
│  ├── 扫描文件:   8个相关文件                                 │
│  │   └── form-model/field/*.java (5个)                      │
│  │   └── form-engine/handler/*.java (3个)                   │
│  ├── 涉及模块:   2个 (do1cloud-form, bpms-component)         │
│  ├── 核心文件:   2个 (BaseFormField.java, FieldHandler.java) │
│  ├── 测试文件:   需新建 (无现有测试)                         │
│  └── 扫描分:     8/12                                        │
│                                                              │
│  ═══ 综合评分 ═══                                           │
│  ├── 关键词:     7 × 0.3 = 2.1                               │
│  ├── 代码扫描:   8 × 0.7 = 5.6                               │
│  └── 最终分:     7.7 → 8分 → L2                              │
│                                                              │
│  推荐流程:                                                   │
│  阶段1: 需求分析                                             │
│  阶段2: 技术分析+方案 (合并)           ← 确认点1             │
│  阶段3: 编码计划                                             │
│  阶段4: 编码+测试 (合并)               ← 确认点2             │
│  阶段5: 对齐+文档 (合并)                                     │
│                                                              │
│  [接受L2] [调整为L1] [调整为L3]                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 流程模板对照

### L1 简单流程 (3阶段)
| 阶段 | 名称 | 合并自 | Skill |
|------|------|--------|-------|
| 1 | 快速分析 | 需求分析+技术分析 | `/dev-quick-analysis` |
| 2 | 快速实现 | 编码计划+编码+单测 | `/dev-quick-impl` |
| 3 | 快速收尾 | 对齐+文档 | `/dev-quick-finish` |

### L2 中等流程 (5阶段)
| 阶段 | 名称 | 合并自 | Skill | 确认 |
|------|------|--------|-------|------|
| 1 | 需求分析 | - | `/dev-requirement` | - |
| 2 | 技术分析+方案 | 技术分析+技术方案 | `/dev-tech-combined` | ✓ |
| 3 | 编码计划 | - | `/dev-coding-plan` | - |
| 4 | 编码+测试 | 编码+单测 | `/dev-impl-test` | ✓ |
| 5 | 对齐+文档 | 对齐+文档 | `/dev-finish` | - |

### L3 复杂流程 (8阶段)
保持现有完整流程，每阶段确认。

---

## 进度文件扩展

分级评估完成后，在 `.progress.json` 中添加以下字段：

```json
{
  "taskGrade": {
    "level": "L2",
    "score": 9,
    "breakdown": {
      "scope": 2,
      "fileCount": 2,
      "riskLevel": 2,
      "patternMatch": 2,
      "externalDeps": 1
    },
    "evaluatedAt": "2026-02-09T10:01:00",
    "userOverride": false,
    "overrideReason": null
  },
  "flowTemplate": {
    "type": "L2_MEDIUM",
    "stages": ["requirement", "tech-combined", "coding-plan", "impl-test", "finish"],
    "confirmationPoints": [2, 4],
    "totalStages": 5
  }
}
```

---

## 使用示例 (增强版)

### 示例1: L1简单任务

```
用户: /dev-start 修复日期字段的时区显示问题

AI 执行分级评估:

1. 关键词分析:
   - "修复"(低风险), "日期字段"(表单引擎), "时区"(配置调整)
   - 初步分: 范围1 + 风险1 + 模式1 + 依赖1 = 4分

2. 代码扫描:
   > 执行: Grep "DateTime|DateField|时区|timezone"
   > 结果: 3个文件
   - form-model/field/DateTime.java
   - form-model/field/Date.java
   - form-engine/converter/DateTimeConverter.java

   > 模块分析: 1个模块 (do1cloud-form)
   > 核心文件: 0个
   > 测试文件: DateTimeTest.java 已存在

   扫描分: 文件1 + 模块1 + 核心1 + 测试1 = 4分

3. 综合评分:
   - 关键词: 4 × 0.3 = 1.2
   - 代码扫描: 4 × 0.7 = 2.8
   - 最终分: 4分 → L1
   - 置信度: 100% (扫描到明确文件)

4. 输出: 推荐L1简单流程，3阶段1确认
```

### 示例2: L2中等任务

```
用户: /dev-start 为表单引擎添加AI按钮字段

AI 执行分级评估:

1. 关键词分析:
   - "添加"(中风险), "表单引擎"(表单), "AI按钮"(新字段+AI能力)
   - 初步分: 范围2 + 风险2 + 模式2 + 依赖2 = 8分

2. 代码扫描:
   > 执行: Grep "Button|Field|AIButton" in form-model/, form-engine/
   > 结果: 8个文件
   - form-model/field/Button.java (参考)
   - form-model/field/BaseFormField.java (需扩展)
   - form-engine/handler/ButtonHandler.java (参考)
   - form-engine/handler/BaseFieldHandler.java (需扩展)
   - ...

   > 模块分析: 2个模块 (do1cloud-form, qiqiao-ai-bridge)
   > 核心文件: 2个 (BaseFormField.java, BaseFieldHandler.java)
   > 测试文件: 需新建

   扫描分: 文件2 + 模块2 + 核心2 + 测试2 = 8分

3. 综合评分:
   - 关键词: 8 × 0.3 = 2.4
   - 代码扫描: 8 × 0.7 = 5.6
   - 最终分: 8分 → L2
   - 置信度: 85%

4. 输出: 推荐L2中等流程，5阶段2确认
```

### 示例3: L3复杂任务

```
用户: /dev-start 重构流程引擎的任务调度核心

AI 执行分级评估:

1. 关键词分析:
   - "重构"(高风险), "流程引擎"(核心), "任务调度"(核心), "核心"(高风险)
   - 初步分: 范围3 + 风险3 + 模式3 + 依赖2 = 11分

2. 代码扫描:
   > 执行: Grep "TaskScheduler|TaskDispatch|核心调度"
   > 结果: 23个文件
   - bpmn-engine/kernel/TaskScheduler.java
   - bpmn-engine/kernel/TaskDispatcher.java
   - bpmn-engine/core/TaskExecutor.java
   - bpmn-service/service/BpmnTaskService.java
   - ...

   > 模块分析: 4个模块 (do1cloud-bpmn, bpms-runtime, bpms-component, ...)
   > 核心文件: 8个 (kernel/*, core/*, service/*)
   > 测试文件: 需大量新建

   扫描分: 文件3 + 模块3 + 核心3 + 测试3 = 12分

3. 综合评分:
   - 关键词: 11 × 0.3 = 3.3
   - 代码扫描: 12 × 0.7 = 8.4
   - 最终分: 11.7 → 12分 → L3
   - 置信度: 95%

4. 输出: 推荐L3复杂流程，完整8阶段
```
