# 快速参考指南

## 🚀 启动服务

```bash
# 启动所有服务（推荐）
./start_all_services.sh

# 或手动启动
python3 -B file_server.py &      # 文件服务器 (端口 8000)
python3 -B app_gradio.py &       # Gradio 界面 (端口 7860)
```

## 🌐 访问地址

- **Gradio 界面**: http://localhost:7860
- **文件服务器**: http://localhost:8000
- **健康检查**: http://localhost:8000/health

## 📸 证件照生成

### 支持的尺寸
- 1寸 (295x413)
- 小1寸 (260x378)
- 2寸 (413x579)
- 小2寸 (413x531)
- 大1寸 (390x567)
- 护照 (354x472)
- 身份证 (358x441)
- 驾驶证 (260x378)
- 社保卡 (358x441)
- 教师资格证 (295x413)

### 支持的背景色
- 白色 (white)
- 蓝色 (blue)
- 红色 (red)
- 浅蓝 (light_blue)

### 使用示例

```
用户: [上传照片] 生成1寸白底证件照
AI: ✅ Successfully generated 1寸 ID photo with white background!
    📥 Download: http://localhost:8000/photos/id_photo_1寸_white_20260203_154550.jpg
```

## 🛠️ 常用命令

### 检查服务状态
```bash
ps aux | grep "app_gradio.py" | grep -v grep
ps aux | grep "file_server.py" | grep -v grep
```

### 停止服务
```bash
pkill -f 'app_gradio.py'
pkill -f 'file_server.py'
```

### 查看日志
```bash
tail -f /tmp/gradio.log
tail -f /tmp/file_server.log
```

### 测试下载功能
```bash
python3 -B test_download_link.py
```

### 清理旧文件
```bash
# 清理 7 天前的文件
find app/static/photos -name "id_photo_*.jpg" -mtime +7 -delete
find app/static/uploads -name "upload_*.jpg" -mtime +7 -delete
```

## 🧪 测试

### 运行所有测试
```bash
cd tests
bash run_all_tests.sh
```

### 单独测试
```bash
# 测试 HivisionIDPhotos 核心功能
python3 -B tests/unit/test_1_hivision_core.py

# 测试工具输出格式
python3 -B tests/unit/test_2_tool_output.py

# 测试 IMAGE_PATH 提取
python3 -B tests/unit/test_3_image_path_extraction.py

# 测试 Agent 工具调用
python3 -B tests/integration/test_4_agent_tool_call.py

# 测试 Gradio 显示
python3 -B tests/integration/test_5_gradio_display.py

# 测试下载链接
python3 -B test_download_link.py
```

## 📁 文件位置

### 生成的证件照
```
app/static/photos/id_photo_{尺寸}_{颜色}_{时间戳}.jpg
```

### 上传的原始照片
```
app/static/uploads/upload_{时间戳}.jpg
```

### 日志文件
```
/tmp/gradio.log
/tmp/file_server.log
```

## 🔧 故障排查

### 问题: 下载链接 404
```bash
# 检查文件服务器是否运行
ps aux | grep file_server.py

# 如果没有运行，启动它
python3 -B file_server.py &
```

### 问题: Gradio 界面无法访问
```bash
# 检查 Gradio 是否运行
ps aux | grep app_gradio.py

# 检查端口是否被占用
lsof -i :7860

# 重启服务
pkill -f 'app_gradio.py'
python3 -B app_gradio.py &
```

### 问题: 证件照生成失败
```bash
# 检查 HivisionIDPhotos 是否正确安装
python3 -B -c "from hivision import IDCreator; print('✅ HivisionIDPhotos 可用')"

# 检查模型文件
ls -lh HivisionIDPhotos/hivision/creator/weights/hivision_modnet.onnx
```

## 📚 文档

- **完整文档**: `证件照下载功能说明.md`
- **完成报告**: `文件下载功能完成报告.md`
- **开发流程**: `DEVELOPMENT_WORKFLOW.md`
- **测试说明**: `tests/README.md`

## 🔗 API 端点

### 文件服务器 (8000)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/photos/{filename}` | GET | 下载证件照 |
| `/uploads/{filename}` | GET | 下载上传文件 |
| `/health` | GET | 健康检查 |

### 示例
```bash
# 下载证件照
curl -O "http://localhost:8000/photos/id_photo_1寸_white_20260203_154550.jpg"

# 健康检查
curl "http://localhost:8000/health"
```

## 💡 提示

1. **首次使用**: 运行 `./start_all_services.sh` 启动所有服务
2. **测试优先**: 修改代码后先运行测试，确保功能正常
3. **查看日志**: 遇到问题时查看 `/tmp/gradio.log` 和 `/tmp/file_server.log`
4. **定期清理**: 定期清理 `app/static/photos/` 中的旧文件
5. **端口冲突**: 如果端口被占用，修改 `file_server.py` 和 `app/core/tools.py` 中的端口号

---

**更新时间**: 2026-02-03  
**版本**: v2.1
