---
name: dev-coding
description: 编码技能。按编码计划逐个执行任务，生成符合规范的代码。开发流程第 5 阶段。
---

# 编码 (Coding)

> 开发流程第 5 阶段：按计划编码 → 遵循规范 → 增量提交

---

## 前置条件

- 已完成编码计划（`/dev-coding-plan`）
- 编码计划已确认

---

## 执行流程

```
编码计划任务列表
     ↓
┌─────────────────────────────────────┐
│ 1. 任务选择                          │
│    - 选择下一个可执行任务              │
│    - 检查依赖是否满足                 │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ 2. 代码生成                          │
│    - 参考模块知识                    │
│    - 参考现有实现                    │
│    - 遵循编码规范                    │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ 3. 自检                              │
│    - 代码风格检查                    │
│    - 编译检查                        │
│    - 基本逻辑验证                    │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ 4. 标记完成                          │
│    - 更新任务状态                    │
│    - 记录关键决策                    │
└─────────────────────────────────────┘
     ↓
下一个任务 / 进入单测阶段
```

---

## 编码规范

### 通用规范

```java
// 1. 类注释
/**
 * [类说明]
 *
 * @author AI辅助开发系统
 * @since [版本号]
 */

// 2. 方法注释
/**
 * [方法说明]
 *
 * @param param1 [参数说明]
 * @return [返回值说明]
 */

// 3. 命名规范
// - 类名：大驼峰 PascalCase
// - 方法名：小驼峰 camelCase
// - 常量：全大写下划线 UPPER_SNAKE_CASE
// - 包名：全小写 lowercase

// 4. 代码组织
// - 字段 → 构造器 → 公共方法 → 私有方法
// - 相关方法放在一起
// - 每个方法不超过 50 行
```

### 模块特定规范

#### 表单字段

```java
@Widget(name = "newField", description = "新字段描述")
public class NewField extends BaseFormField {

    // 1. 字段属性
    private String customProperty;

    // 2. 必须实现的方法
    @Override
    public Object getValue() { ... }

    @Override
    public void setValue(Object value) { ... }

    // 3. 可选：联动刷新
    @Override
    public List<String> getTriggerRefreshElementIds() { ... }
}
```

#### 流程节点行为

```java
public class NewNodeBehavior implements Behavior {

    @Override
    public void execute(DelegateExecution execution) {
        // 1. 获取上下文
        // 2. 执行业务逻辑
        // 3. 设置变量
        // 4. 完成节点
    }
}
```

#### 按钮行为

```java
public class NewButtonBehavior extends AbstractBusinessButtonBehavior {

    @Override
    public Object execute(ButtonClickContext context) {
        // 1. 参数校验
        // 2. 业务处理
        // 3. 返回结果
    }
}
```

---

## 代码模板

### 服务类模板

```java
package cn.com.do1.[module].service.impl;

import org.springframework.stereotype.Service;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
@RequiredArgsConstructor
public class [Name]ServiceImpl implements [Name]Service {

    private final [Dependency1] dependency1;
    private final [Dependency2] dependency2;

    @Override
    public [ReturnType] [methodName]([Params]) {
        log.info("[方法说明] - 参数: {}", params);

        // 业务逻辑

        return result;
    }
}
```

### Controller 模板

```java
package cn.com.do1.[module].controller;

import org.springframework.web.bind.annotation.*;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/v1/[resource]")
@RequiredArgsConstructor
public class [Name]Controller {

    private final [Name]Service service;

    @PostMapping
    public ResponseEntity<[Response]> create(@Valid @RequestBody [Request] request) {
        return ResponseEntity.ok(service.create(request));
    }

    @GetMapping("/{id}")
    public ResponseEntity<[Response]> get(@PathVariable String id) {
        return ResponseEntity.ok(service.get(id));
    }
}
```

---

## 增量提交

每完成一个任务后：

```bash
# 1. 检查改动
git status
git diff

# 2. 提交（小步提交）
git add [相关文件]
git commit -m "[任务编号] [任务描述]"

# 示例
git commit -m "task-1.1: 创建 AIButtonField 字段类"
```

---

## 下一步

完成所有编码任务后，进入单元测试阶段，使用 `/dev-unit-test`
