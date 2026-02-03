# Ollama 快速参考

## 🚀 快速开始

```bash
# 1. 确认 Ollama 运行
curl http://127.0.0.1:11434/
# 应返回: Ollama is running

# 2. 确认模型已下载
ollama list
# 应看到: qwen3:8b

# 3. 确认配置
cat .env | grep -E "(MODEL_PROVIDER|OLLAMA)"
# 应看到:
# MODEL_PROVIDER=ollama
# OLLAMA_BASE_URL=http://127.0.0.1:11434
# OLLAMA_LLM_MODEL=qwen3:8b

# 4. 启动服务
./start_web.sh

# 5. 访问
open http://localhost:8000
```

## 🔧 常用命令

### Ollama 服务管理
```bash
# 启动
ollama serve

# 检查状态
curl http://127.0.0.1:11434/

# 停止（macOS）
killall ollama
```

### 模型管理
```bash
# 列出已安装模型
ollama list

# 下载模型
ollama pull qwen3:8b

# 删除模型
ollama rm qwen3:8b

# 测试模型
ollama run qwen3:8b "你好"
```

### 切换提供商
```bash
# 使用脚本切换
./switch_provider.sh

# 或手动修改 .env
# MODEL_PROVIDER=ollama  # 本地 Ollama
# MODEL_PROVIDER=aliyun  # 阿里云
# MODEL_PROVIDER=groq    # Groq
```

## 📊 推荐模型

| 模型 | 大小 | 内存需求 | 速度 | 质量 | 适用场景 |
|------|------|----------|------|------|----------|
| qwen3:4b | 2.3GB | 8GB | 快 | 中 | 快速测试 |
| qwen3:8b | 4.9GB | 16GB | 中 | 高 | 推荐使用 ⭐ |
| qwen2.5:14b | 8.7GB | 24GB | 慢 | 很高 | 高质量需求 |
| llama3:8b | 4.7GB | 16GB | 中 | 高 | 英文优先 |

## ⚠️ 常见问题

### 问题：Ollama 服务未响应
**症状：** 页面显示 "Ollama 服务未响应" 错误

**解决：**
```bash
# 1. 检查服务
curl http://127.0.0.1:11434/

# 2. 如果未运行，启动服务
ollama serve

# 3. 验证
curl http://127.0.0.1:11434/
```

### 问题：模型未找到
**症状：** 错误提示模型不存在

**解决：**
```bash
# 1. 检查已安装模型
ollama list

# 2. 下载模型
ollama pull qwen3:8b

# 3. 验证
ollama list | grep qwen3:8b
```

### 问题：响应很慢
**原因：** 内存不足或 CPU 性能限制

**解决：**
```bash
# 1. 使用更小的模型
# 修改 .env
OLLAMA_LLM_MODEL=qwen3:4b

# 2. 检查内存使用
top -o MEM

# 3. 考虑使用 GPU（如果有）
# Ollama 会自动检测并使用 GPU
```

### 问题：配置未生效
**症状：** 修改 .env 后仍使用旧配置

**解决：**
```bash
# 重启 Web 服务
# 1. 停止当前服务（Ctrl+C）
# 2. 重新启动
./start_web.sh
```

## 💡 性能优化

### 1. 使用合适的模型
- 开发测试：qwen3:4b
- 日常使用：qwen3:8b ⭐
- 高质量需求：qwen2.5:14b

### 2. 硬件优化
- 最低：8GB 内存 + 4 核 CPU
- 推荐：16GB 内存 + 8 核 CPU
- 最佳：32GB 内存 + GPU

### 3. 系统优化
```bash
# macOS: 关闭不必要的应用
# Linux: 调整 swap
sudo sysctl vm.swappiness=10
```

## 🔄 与其他提供商对比

| 特性 | Ollama | 阿里云 | Groq |
|------|--------|--------|------|
| 成本 | 免费 | 按量付费 | 免费 |
| 速度 | 取决于硬件 | 快 | 非常快 |
| 隐私 | 完全本地 | 云端 | 云端 |
| 稳定性 | 取决于硬件 | 高 | 高 |
| 网络要求 | 无 | 需要 | 需要 |
| 设置难度 | 中 | 简单 | 简单 |

## 📚 相关资源

- [Ollama 官方文档](https://ollama.ai/docs)
- [模型库](https://ollama.ai/library)
- [完整配置指南](OLLAMA_SETUP.md)
- [项目 README](README.md)

## 🆘 获取帮助

1. 运行诊断脚本：`./quick_test_ollama.sh`
2. 查看日志：检查终端输出
3. 测试错误处理：`./test_error_handling.sh`
4. 查看完整文档：`OLLAMA_SETUP.md`
