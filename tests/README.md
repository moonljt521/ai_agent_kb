# 测试框架说明

## 测试分层架构

我们采用分层测试策略，将功能拆分为独立的测试单元，便于快速定位问题。

```
tests/
├── unit/                    # 单元测试（不依赖外部服务）
│   ├── test_1_hivision_core.py          # HivisionIDPhotos 核心功能
│   ├── test_2_tool_output.py            # 工具输出格式
│   └── test_3_image_path_extraction.py  # IMAGE_PATH 提取逻辑
├── integration/             # 集成测试（涉及多个组件）
│   ├── test_4_agent_tool_call.py        # Agent 工具调用
│   └── test_5_gradio_display.py         # Gradio 图片显示
└── run_all_tests.sh         # 运行所有测试
```

## 测试层级

### Level 1: 单元测试

#### 测试 1: HivisionIDPhotos 核心功能
- **目的**: 验证图片生成功能
- **不涉及**: Agent, LLM, Gradio
- **测试内容**:
  - HivisionIDPhotos 是否正确初始化
  - 能否生成不同规格的证件照
  - 生成的文件是否存在
  - 文件大小是否合理

```bash
python3 -B tests/unit/test_1_hivision_core.py
```

#### 测试 2: 工具输出格式
- **目的**: 验证工具返回格式
- **不涉及**: Agent, LLM
- **测试内容**:
  - 返回是否包含必要字段（white/blue/red）
  - 是否包含 `[IMAGE_PATH:...]` 标记
  - 是否包含下载链接
  - 图片文件是否真实存在

```bash
python3 -B tests/unit/test_2_tool_output.py
```

#### 测试 3: IMAGE_PATH 提取逻辑
- **目的**: 验证路径提取算法
- **不涉及**: Agent, LLM, 实际文件
- **测试内容**:
  - 正则表达式是否正确
  - 能否处理带空格的路径
  - 能否处理多个标记（取第一个）

```bash
python3 -B tests/unit/test_3_image_path_extraction.py
```

### Level 2: 集成测试

#### 测试 4: Agent 工具调用
- **目的**: 验证 Agent 能否正确调用工具
- **涉及**: Agent, LLM, 工具
- **不涉及**: Gradio 界面
- **测试内容**:
  - Agent 能否理解用户意图
  - 能否正确调用 generate_id_photo 工具
  - 返回是否包含 IMAGE_PATH 标记

```bash
python3 -B tests/integration/test_4_agent_tool_call.py
```

#### 测试 5: Gradio 图片显示
- **目的**: 验证 Gradio 界面处理逻辑
- **不涉及**: Agent, LLM, 实际生成
- **测试内容**:
  - 能否正确提取 IMAGE_PATH
  - 能否转换为 Gradio 图片格式
  - 是否移除了内部标记

```bash
python3 -B tests/integration/test_5_gradio_display.py
```

## 快速开始

### 运行所有测试
```bash
./tests/run_all_tests.sh
```

### 运行单个测试
```bash
# 单元测试
python3 -B tests/unit/test_1_hivision_core.py
python3 -B tests/unit/test_2_tool_output.py
python3 -B tests/unit/test_3_image_path_extraction.py

# 集成测试
python3 -B tests/integration/test_4_agent_tool_call.py
python3 -B tests/integration/test_5_gradio_display.py
```

## 测试策略

### 开发新功能时
1. **先写单元测试** - 验证核心逻辑
2. **再写集成测试** - 验证组件协作
3. **最后手动测试** - 验证用户体验

### 修复 Bug 时
1. **定位问题层级** - 是单元问题还是集成问题？
2. **运行相关测试** - 快速验证修复
3. **运行所有测试** - 确保没有破坏其他功能

### 重构代码时
1. **先运行所有测试** - 确保当前功能正常
2. **进行重构**
3. **再次运行所有测试** - 确保功能未受影响

## 测试原则

### ✅ 好的测试
- **快速**: 单元测试应在 1 秒内完成
- **独立**: 每个测试独立运行，不依赖其他测试
- **可重复**: 多次运行结果一致
- **清晰**: 测试失败时能快速定位问题

### ❌ 避免的做法
- **不要每次都测试全流程** - 太慢，难以定位问题
- **不要在测试中混合多个功能** - 难以判断哪个环节出错
- **不要依赖外部状态** - 如数据库、网络服务（除非必要）

## 测试覆盖

| 功能模块 | 单元测试 | 集成测试 | 手动测试 |
|---------|---------|---------|---------|
| HivisionIDPhotos 核心 | ✅ | - | - |
| 工具输出格式 | ✅ | - | - |
| IMAGE_PATH 提取 | ✅ | - | - |
| Agent 工具调用 | - | ✅ | - |
| Gradio 图片显示 | - | ✅ | ✅ |
| 完整用户流程 | - | - | ✅ |

## 常见问题

### Q: 测试失败了怎么办？
A: 
1. 查看失败的测试层级（单元 or 集成）
2. 单独运行失败的测试，查看详细输出
3. 根据错误信息定位问题
4. 修复后重新运行该测试

### Q: 如何添加新测试？
A:
1. 确定测试层级（单元 or 集成）
2. 在对应目录创建测试文件
3. 遵循现有测试的格式
4. 更新 `run_all_tests.sh`

### Q: 测试太慢怎么办？
A:
1. 优先运行单元测试（最快）
2. 只运行相关的测试
3. 避免在测试中调用 LLM（使用 mock）

## 持续集成

建议在 CI/CD 流程中：
1. **每次提交**: 运行单元测试
2. **每次 PR**: 运行所有测试
3. **每次发布**: 运行所有测试 + 手动测试

## 性能基准

| 测试 | 预期时间 |
|-----|---------|
| test_1_hivision_core | < 3s |
| test_2_tool_output | < 3s |
| test_3_image_path_extraction | < 1s |
| test_4_agent_tool_call | < 10s |
| test_5_gradio_display | < 1s |
| **总计** | **< 20s** |

---

**最后更新**: 2026-02-03  
**维护者**: AI Agent Team
