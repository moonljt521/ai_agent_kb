# 开发流程规范

## 问题分析

之前的开发流程存在以下问题：
1. **每次都测试全流程** - 耗时长，难以定位问题
2. **没有分层测试** - 无法快速判断哪个环节出错
3. **缺少单元测试** - 修改代码后需要重新测试整个系统

## 新的开发流程

### 1. 分层测试架构

```
┌─────────────────────────────────────┐
│  Level 5: 手动测试（用户体验）        │
├─────────────────────────────────────┤
│  Level 4: 集成测试（Agent + Gradio）  │
├─────────────────────────────────────┤
│  Level 3: 工具测试（Tool 输出）       │
├─────────────────────────────────────┤
│  Level 2: 核心功能测试（HivisionIDPhotos）│
├─────────────────────────────────────┤
│  Level 1: 单元测试（算法逻辑）        │
└─────────────────────────────────────┘
```

### 2. 开发新功能

#### Step 1: 编写单元测试
```bash
# 创建测试文件
vim tests/unit/test_new_feature.py

# 运行测试（应该失败）
python3 -B tests/unit/test_new_feature.py
```

#### Step 2: 实现核心功能
```bash
# 实现功能
vim app/core/new_feature.py

# 运行测试（应该通过）
python3 -B tests/unit/test_new_feature.py
```

#### Step 3: 集成到工具
```bash
# 更新工具
vim app/core/tools.py

# 测试工具输出
python3 -B tests/unit/test_2_tool_output.py
```

#### Step 4: 集成到 Agent
```bash
# 测试 Agent 调用
python3 -B tests/integration/test_4_agent_tool_call.py
```

#### Step 5: 手动测试
```bash
# 启动服务
./start_hivision.sh

# 在浏览器中测试
```

### 3. 修复 Bug

#### Step 1: 定位问题层级
```bash
# 运行所有测试，找出失败的层级
./tests/run_all_tests.sh
```

#### Step 2: 单独运行失败的测试
```bash
# 例如：工具输出格式有问题
python3 -B tests/unit/test_2_tool_output.py
```

#### Step 3: 修复代码
```bash
# 修改相关代码
vim app/core/tools.py
```

#### Step 4: 验证修复
```bash
# 重新运行失败的测试
python3 -B tests/unit/test_2_tool_output.py

# 运行所有测试，确保没有破坏其他功能
./tests/run_all_tests.sh
```

### 4. 重构代码

#### Step 1: 运行所有测试（确保当前功能正常）
```bash
./tests/run_all_tests.sh
```

#### Step 2: 进行重构
```bash
vim app/core/some_module.py
```

#### Step 3: 再次运行所有测试
```bash
./tests/run_all_tests.sh
```

## 测试策略

### 快速反馈循环

```
修改代码 → 运行单元测试（< 3s）→ 通过 → 运行集成测试（< 10s）→ 通过 → 提交
         ↓ 失败                    ↓ 失败
         修复                      修复
```

### 测试优先级

1. **单元测试** - 最快，最先运行
2. **工具测试** - 验证输出格式
3. **集成测试** - 验证组件协作
4. **手动测试** - 验证用户体验

### 何时运行哪些测试

| 场景 | 运行测试 | 预期时间 |
|-----|---------|---------|
| 修改核心功能 | 单元测试 | < 3s |
| 修改工具 | 单元测试 + 工具测试 | < 5s |
| 修改 Agent | 所有测试 | < 20s |
| 提交代码前 | 所有测试 | < 20s |
| 发布前 | 所有测试 + 手动测试 | < 5min |

## 测试命令速查

### 单元测试
```bash
# HivisionIDPhotos 核心功能
python3 -B tests/unit/test_1_hivision_core.py

# 工具输出格式
python3 -B tests/unit/test_2_tool_output.py

# IMAGE_PATH 提取逻辑
python3 -B tests/unit/test_3_image_path_extraction.py
```

### 集成测试
```bash
# Agent 工具调用
python3 -B tests/integration/test_4_agent_tool_call.py

# Gradio 图片显示
python3 -B tests/integration/test_5_gradio_display.py
```

### 运行所有测试
```bash
./tests/run_all_tests.sh
```

## 当前测试状态

| 测试 | 状态 | 说明 |
|-----|------|------|
| 1. HivisionIDPhotos 核心 | ✅ 通过 | 图片生成正常 |
| 2. 工具输出格式 | ✅ 通过 | 格式正确 |
| 3. IMAGE_PATH 提取 | ✅ 通过 | 提取逻辑正确 |
| 4. Agent 工具调用 | ❌ 失败 | IMAGE_PATH 未传递到响应 |
| 5. Gradio 图片显示 | ✅ 通过 | 显示逻辑正确 |

## 已知问题

### 问题 1: IMAGE_PATH 未传递到 Agent 响应
- **层级**: 集成测试（test_4）
- **原因**: Agent 的 intermediate_steps 提取逻辑未生效
- **影响**: 图片无法在 Gradio 中显示
- **解决方案**: 需要调试 agent.py 中的提取逻辑

### 问题 2: Python 缓存问题
- **现象**: 代码更新后不生效
- **解决方案**: 使用 `python3 -B` 或清除缓存
  ```bash
  find . -name "*.pyc" -delete
  find . -name "__pycache__" -type d -exec rm -rf {} +
  ```

## 最佳实践

### ✅ 推荐做法
1. **先写测试，再写代码** - TDD（测试驱动开发）
2. **每次只修改一个功能** - 便于定位问题
3. **提交前运行所有测试** - 确保没有破坏现有功能
4. **测试失败时不要提交** - 保持主分支稳定

### ❌ 避免做法
1. **不要跳过测试直接手动测试** - 浪费时间
2. **不要在测试中混合多个功能** - 难以定位问题
3. **不要依赖外部状态** - 测试应该独立可重复
4. **不要每次都测试全流程** - 使用分层测试

## 工具推荐

### 快速运行测试
```bash
# 创建别名
alias test1='python3 -B tests/unit/test_1_hivision_core.py'
alias test2='python3 -B tests/unit/test_2_tool_output.py'
alias test3='python3 -B tests/unit/test_3_image_path_extraction.py'
alias test4='python3 -B tests/integration/test_4_agent_tool_call.py'
alias test5='python3 -B tests/integration/test_5_gradio_display.py'
alias testall='./tests/run_all_tests.sh'
```

### 监控文件变化自动运行测试
```bash
# 安装 entr
brew install entr  # macOS
apt-get install entr  # Linux

# 监控文件变化
ls app/core/*.py | entr -c python3 -B tests/unit/test_2_tool_output.py
```

## 持续改进

### 下一步计划
1. ✅ 建立分层测试框架
2. ⏳ 修复 IMAGE_PATH 传递问题
3. ⏳ 添加更多边界情况测试
4. ⏳ 集成到 CI/CD 流程
5. ⏳ 添加性能测试

### 测试覆盖率目标
- 单元测试覆盖率: > 80%
- 集成测试覆盖率: > 60%
- 关键路径覆盖率: 100%

---

**最后更新**: 2026-02-03  
**维护者**: AI Agent Team  
**版本**: 1.0.0
