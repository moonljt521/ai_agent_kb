# Web 页面证件照显示修复

## 修复时间
2026年2月3日

## 问题描述
在 Web 页面中，证件照生成成功后，图片没有显示出来。文件下载功能正常。

## 问题分析

### 1. 数据流程
```
用户请求 → Agent 生成证件照 → 返回答案（包含 [IMAGE_PATH:...] 标记）
→ 前端接收 → 需要解析标记并显示图片
```

### 2. 问题原因
前端代码使用 `marked.parse()` 渲染 Markdown，但没有处理自定义的 `[IMAGE_PATH:...]` 标记，导致：
- 标记被当作普通文本显示
- 图片路径没有被提取
- 没有生成 `<img>` 标签

## 修复方案

### 1. 前端 JavaScript 修改

**文件**: `app/static/index.html`

**修改位置**: `addAssistantMessage()` 函数

**新增功能**:
```javascript
// 处理图片路径标记
let answerText = data.answer;
let imageHtml = '';

// 提取图片路径
const imageMatch = answerText.match(/\[IMAGE_PATH:(.*?)\]/);
if (imageMatch) {
    const imagePath = imageMatch[1].trim();
    // 移除标记
    answerText = answerText.replace(/\[IMAGE_PATH:.*?\]/g, '').trim();
    
    // 生成图片 HTML
    const filename = imagePath.split('/').pop();
    const imageUrl = `http://localhost:8000/photos/${filename}`;
    
    imageHtml = `
        <div class="id-photo-container">
            <img src="${imageUrl}" alt="生成的证件照" class="id-photo" />
            <div class="id-photo-actions">
                <a href="${imageUrl}" download="${filename}" class="download-btn">
                    📥 下载证件照
                </a>
            </div>
        </div>
    `;
}
```

**处理流程**:
1. 从答案中提取 `[IMAGE_PATH:...]` 标记
2. 获取图片路径
3. 从答案中移除标记（避免显示）
4. 生成图片 URL（使用文件服务器地址）
5. 创建图片 HTML（包含下载按钮）
6. 插入到消息内容中

### 2. CSS 样式添加

**新增样式**:
```css
/* 证件照显示样式 */
.id-photo-container {
    margin-top: 15px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 10px;
    text-align: center;
}

.id-photo {
    max-width: 100%;
    max-height: 400px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    margin-bottom: 12px;
    display: block;
    margin-left: auto;
    margin-right: auto;
}

.id-photo-actions {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 12px;
}

.download-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 10px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-decoration: none;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.download-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
}
```

**样式特点**:
- 图片居中显示
- 最大高度 400px（保持合理尺寸）
- 圆角和阴影效果
- 下载按钮带悬停动画
- 响应式设计

## 修复效果

### 修复前
```
用户: 生成2寸蓝底证件照
助手: ✅ 已成功生成证件照！
      [IMAGE_PATH:app/static/photos/id_photo_2寸_blue_20260203_155625.jpg]
      📥 Download: http://localhost:8000/photos/...
```
- 图片路径标记直接显示为文本
- 没有图片预览
- 只能通过下载链接查看

### 修复后
```
用户: 生成2寸蓝底证件照
助手: ✅ 已成功生成证件照！
      
      [显示证件照图片]
      
      [📥 下载证件照] 按钮
      
      📥 Download: http://localhost:8000/photos/...
```
- 图片直接显示在对话中
- 美观的容器和样式
- 下载按钮方便保存
- 图片路径标记被隐藏

## 测试方法

### 1. 自动化测试
```bash
# 确保服务运行
python app/main.py  # 端口 5000
python file_server.py  # 端口 8000

# 运行测试
python test_web_image_display.py
```

### 2. 手动测试
1. 访问 http://localhost:5000
2. 在输入框中输入：
   ```
   请帮我生成一张2寸蓝底证件照，图片路径是 app/static/uploads/upload_1770105006.jpg
   ```
3. 查看返回结果：
   - ✅ 应该看到证件照图片
   - ✅ 图片下方有下载按钮
   - ✅ 没有显示 `[IMAGE_PATH:...]` 标记

### 3. 测试检查点
- [ ] 图片正确显示
- [ ] 图片尺寸合适（不会太大或太小）
- [ ] 下载按钮可点击
- [ ] 下载功能正常
- [ ] 图片路径标记被隐藏
- [ ] 样式美观（居中、圆角、阴影）
- [ ] 响应式（在不同屏幕尺寸下正常显示）

## 技术细节

### 1. 图片 URL 生成
```javascript
const filename = imagePath.split('/').pop();
const imageUrl = `http://localhost:8000/photos/${filename}`;
```
- 从完整路径提取文件名
- 使用文件服务器地址（端口 8000）
- 路径格式：`/photos/{filename}`

### 2. 标记移除
```javascript
answerText = answerText.replace(/\[IMAGE_PATH:.*?\]/g, '').trim();
```
- 使用正则表达式匹配标记
- 全局替换（`g` 标志）
- 非贪婪匹配（`.*?`）
- 移除后 trim 空白

### 3. HTML 注入
```javascript
messageDiv.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content">
        <div class="message-text">${renderedAnswer}</div>
        ${imageHtml}  <!-- 图片插入在这里 -->
        <div class="message-meta">...</div>
    </div>
`;
```
- 图片在文本和元数据之间
- 使用模板字符串动态插入
- 只在有图片时显示

## 兼容性

### 浏览器支持
- ✅ Chrome/Edge (最新版)
- ✅ Firefox (最新版)
- ✅ Safari (最新版)
- ✅ 移动浏览器

### 功能降级
如果图片加载失败：
- 显示 alt 文本："生成的证件照"
- 下载按钮仍然可用
- 不影响其他功能

## 相关文件

- `app/static/index.html` - 前端页面（已修改）
- `app/core/tools.py` - 证件照生成工具
- `app/core/agent.py` - Agent 逻辑
- `file_server.py` - 文件服务器
- `test_web_image_display.py` - 测试脚本

## 后续优化建议

### 1. 图片加载状态
```javascript
<img 
    src="${imageUrl}" 
    alt="生成的证件照" 
    class="id-photo"
    onload="this.style.opacity=1"
    onerror="this.src='placeholder.png'"
/>
```

### 2. 图片预览功能
- 点击图片放大查看
- 添加灯箱效果
- 支持缩放和旋转

### 3. 多图片支持
- 支持一次生成多张证件照
- 图片轮播或网格显示
- 批量下载功能

### 4. 图片编辑
- 在线裁剪
- 调整亮度/对比度
- 添加水印

## 总结

通过在前端添加图片路径解析和显示逻辑，成功实现了证件照在 Web 页面中的直接显示：

1. ✅ 提取 `[IMAGE_PATH:...]` 标记
2. ✅ 生成图片 URL
3. ✅ 创建图片 HTML
4. ✅ 添加美观样式
5. ✅ 保留下载功能

用户现在可以在对话中直接看到生成的证件照，无需先下载再查看，大大提升了用户体验。
