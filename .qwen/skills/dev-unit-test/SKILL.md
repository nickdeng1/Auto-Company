---
name: dev-unit-test
description: 单元测试技能。为实现的代码编写单元测试，确保覆盖核心逻辑。开发流程第 6 阶段。
---

# 单元测试 (Unit Test)

> 开发流程第 6 阶段：编写测试 → 执行验证 → 确保覆盖

---

## 前置条件

- 已完成编码（`/dev-coding`）
- 所有编码任务已完成

---

## 执行流程

```
编码完成的类
     ↓
┌─────────────────────────────────────┐
│ 1. 测试范围确定                      │
│    - 识别需要测试的类                │
│    - 确定测试优先级                  │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ 2. 测试用例设计                      │
│    - 正常流程                        │
│    - 边界条件                        │
│    - 异常场景                        │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ 3. 测试代码编写                      │
│    - 使用 JUnit 5                    │
│    - 使用 Mockito                    │
│    - 遵循 AAA 模式                   │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ 4. 执行测试                          │
│    - 运行单元测试                    │
│    - 检查覆盖率                      │
│    - 修复失败用例                    │
└─────────────────────────────────────┘
     ↓
测试通过 → 进入方案对齐阶段
```

---

## 测试规范

### 命名规范

```java
// 测试类命名：[被测类名]Test
public class AIButtonFieldTest {

    // 测试方法命名：should[预期行为]_when[条件]
    @Test
    void shouldReturnValue_whenValueIsSet() { ... }

    @Test
    void shouldThrowException_whenValueIsNull() { ... }
}
```

### AAA 模式

```java
@Test
void shouldCalculateTotal_whenItemsProvided() {
    // Arrange - 准备
    Order order = new Order();
    order.addItem(new Item("A", 100));
    order.addItem(new Item("B", 200));

    // Act - 执行
    int total = order.calculateTotal();

    // Assert - 断言
    assertThat(total).isEqualTo(300);
}
```

---

## 测试模板

### 服务类测试

```java
package cn.com.do1.[module].service.impl;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class [Name]ServiceImplTest {

    @Mock
    private [Dependency] dependency;

    @InjectMocks
    private [Name]ServiceImpl service;

    @BeforeEach
    void setUp() {
        // 初始化
    }

    @Test
    void shouldDoSomething_whenCondition() {
        // Arrange
        when(dependency.method()).thenReturn(expectedValue);

        // Act
        var result = service.method();

        // Assert
        assertThat(result).isNotNull();
        verify(dependency).method();
    }

    @Test
    void shouldThrowException_whenInvalidInput() {
        // Arrange
        var invalidInput = null;

        // Act & Assert
        assertThatThrownBy(() -> service.method(invalidInput))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessage("Input cannot be null");
    }
}
```

### 表单字段测试

```java
@ExtendWith(MockitoExtension.class)
class NewFieldTest {

    private NewField field;

    @BeforeEach
    void setUp() {
        field = new NewField();
    }

    @Test
    void shouldReturnWidgetName() {
        assertThat(field.getWidgetName()).isEqualTo("newField");
    }

    @Test
    void shouldSetAndGetValue() {
        // Arrange
        String value = "testValue";

        // Act
        field.setValue(value);

        // Assert
        assertThat(field.getValue()).isEqualTo(value);
    }

    @Test
    void shouldTriggerRefresh_whenValueChanged() {
        // Arrange
        field.setTriggerRefreshElementIds(List.of("field2", "field3"));

        // Act
        var refreshIds = field.getTriggerRefreshElementIds();

        // Assert
        assertThat(refreshIds).containsExactly("field2", "field3");
    }
}
```

---

## 测试覆盖要求

| 类型 | 最低覆盖率 | 重点覆盖 |
|------|-----------|----------|
| 核心业务逻辑 | 80% | 必须 |
| 工具类 | 90% | 必须 |
| Controller | 60% | 主要接口 |
| 配置类 | 可选 | 复杂配置 |

---

## 运行测试

```bash
# 运行单个测试类
mvn test -Dtest=[TestClassName]

# 运行所有测试
mvn test

# 生成覆盖率报告
mvn test jacoco:report

# 查看覆盖率报告
open target/site/jacoco/index.html
```

---

## 下一步

测试通过后，进入方案对齐阶段，使用 `/dev-alignment`
