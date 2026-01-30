# ✅ 处理流程显示功能已添加

## 功能说明
在查询结果中清晰显示当次查询是否使用了 LLM 和本地知识库，让用户了解系统的处理流程。

## 显示效果

### 处理流程区域
```
⚙️ 处理流程
┌─────────────────────────────────────────────┐
│ ✅ 本地知识库  ✅ LLM 处理  🎯 关键词匹配   │
└─────────────────────────────────────────────┘
```

### 状态标识
```
✅ 使用知识库    🤖 使用 LLM    📄 检索 5 个片段
```

## 实现内容

### 1. 新增样式

#### 处理流程信息框
```css
.process-info {
    background: #f8f9fa;
    border-left: 4px solid #667eea;
    padding: 12px 15px;
    margin-bottom: 15px;
    border-radius: 5px;
}
```

#### 处理步骤
```css
.process-step {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 5px 10px;
    background: white;
    border-radius: 5px;
    border: 1px solid #e0e0e0;
}

.process-step.active {
    border-color: #667eea;
    background: #f0f4ff;
}

.process-step.inactive {
    opacity: 0.5;
}
```

#### 新增徽章颜色
```css
.badge.danger {
    background: #f8d7da;
    color: #721c24;
}

.badge.primary {
    background: #cce5ff;
    color: #004085;
}
```

### 2. 处理流程显示逻辑

```javascript
// 判断是否使用了 LLM
const usedLLM = !data.used_direct_retrieval;

// 构建处理流程信息
const processInfoHtml = `
    <div class="process-info">
        <h4>⚙️ 处理流程</h4>
        <div class="process-steps">
            <div class="process-step ${data.knowledge_base_used ? 'active' : 'inactive'}">
                <span class="icon">${data.knowledge_base_used ? '✅' : '❌'}</span>
                <span>本地知识库</span>
            </div>
            <div class="process-step ${usedLLM ? 'active' : 'inactive'}">
                <span class="icon">${usedLLM ? '✅' : '❌'}</span>
                <span>LLM 处理</span>
            </div>
            ${data.keyword_matched ? `
                <div class="process-step active">
                    <span class="icon">🎯</span>
                    <span>关键词匹配</span>
                </div>
            ` : ''}
            ${data.used_few_shot ? `
                <div class="process-step active">
                    <span class="icon">📝</span>
                    <span>Few-Shot</span>
                </div>
            ` : ''}
        </div>
    </div>
`;
```

### 3. 底部徽章显示

```javascript
<div class="meta">
    <span class="badge ${data.knowledge_base_used ? 'success' : 'warning'}">
        ${data.knowledge_base_used ? '✅ 使用知识库' : '❌ 未使用知识库'}
    </span>
    <span class="badge ${usedLLM ? 'primary' : 'info'}">
        ${usedLLM ? '🤖 使用 LLM' : '⚡ 直接检索'}
    </span>
    ${data.knowledge_base_used && data.retrieved_docs_count ? `
        <span class="badge info">
            📄 检索 ${data.retrieved_docs_count} 个片段
        </span>
    ` : ''}
</div>
```

## 显示场景

### 场景 1: 使用知识库 + LLM
**查询**: "贾宝玉是谁？"

**处理流程**:
```
⚙️ 处理流程
✅ 本地知识库  ✅ LLM 处理  🎯 关键词匹配  📝 Few-Shot
```

**状态标识**:
```
✅ 使用知识库  🤖 使用 LLM  📄 检索 5 个片段
```

### 场景 2: 仅使用知识库（直接检索）
**查询**: "贾宝玉"

**处理流程**:
```
⚙️ 处理流程
✅ 本地知识库  ❌ LLM 处理  🎯 关键词匹配
```

**状态标识**:
```
✅ 使用知识库  ⚡ 直接检索  📄 检索 3 个片段
```

### 场景 3: 仅使用 LLM（未找到相关知识）
**查询**: "今天天气怎么样？"

**处理流程**:
```
⚙️ 处理流程
❌ 本地知识库  ✅ LLM 处理
```

**状态标识**:
```
❌ 未使用知识库  🤖 使用 LLM
```

## 视觉设计

### 1. 处理流程区域
- **背景**: 浅灰色 (#f8f9fa)
- **左边框**: 蓝色粗边框 (4px)
- **圆角**: 5px
- **间距**: 上下 15px

### 2. 处理步骤
- **激活状态**: 蓝色边框 + 浅蓝背景
- **未激活状态**: 灰色边框 + 50% 透明度
- **图标**: emoji 表情增强视觉效果
- **布局**: 横向排列，自动换行

### 3. 状态徽章
- **使用知识库**: 绿色徽章 (success)
- **未使用知识库**: 黄色徽章 (warning)
- **使用 LLM**: 蓝色徽章 (primary)
- **直接检索**: 青色徽章 (info)

## 信息层级

### 第一层: 处理流程（最重要）
显示系统处理的主要步骤，让用户一目了然：
- 是否使用本地知识库
- 是否使用 LLM 处理
- 是否命中关键词
- 是否使用 Few-Shot

### 第二层: 答案内容
Markdown 渲染的答案文本

### 第三层: 详细标识
底部徽章显示更多细节：
- 知识库使用状态
- LLM 使用状态
- 检索片段数量

### 第四层: 引用来源
如果使用了知识库，显示具体的文档来源

## 用户体验优化

### 1. 清晰的视觉层级
- 处理流程放在最前面，用户首先看到
- 使用边框和背景色区分不同区域
- 激活/未激活状态对比明显

### 2. 直观的图标
- ✅/❌ 表示是否使用
- 🤖 表示 LLM
- 📚 表示知识库
- 🎯 表示关键词匹配
- 📝 表示 Few-Shot
- ⚡表示直接检索

### 3. 响应式布局
- 处理步骤自动换行
- 适配手机和平板
- 保持良好的可读性

### 4. 一致的配色
- 成功: 绿色
- 警告: 黄色
- 信息: 青色
- 主要: 蓝色
- 危险: 红色

## 技术实现

### 判断 LLM 使用
```javascript
const usedLLM = !data.used_direct_retrieval;
```

逻辑：
- `used_direct_retrieval = true` → 直接检索，未使用 LLM
- `used_direct_retrieval = false` → 使用了 LLM 处理

### 动态显示步骤
```javascript
${data.keyword_matched ? `
    <div class="process-step active">
        <span class="icon">🎯</span>
        <span>关键词匹配</span>
    </div>
` : ''}
```

只有当条件满足时才显示对应的步骤。

## 优势

1. **透明度**: 用户清楚知道系统如何处理查询
2. **可信度**: 显示数据来源增强信任
3. **教育性**: 帮助用户理解 RAG 系统的工作原理
4. **调试友好**: 开发者可以快速判断系统行为
5. **视觉美观**: 统一的设计风格和配色

## 总结

成功添加了处理流程显示功能，用户现在可以清楚地看到：
- ✅ 是否使用了本地知识库
- ✅ 是否使用了 LLM 处理
- ✅ 是否命中关键词
- ✅ 是否使用 Few-Shot
- ✅ 检索了多少个文档片段

通过清晰的视觉设计和直观的图标，让用户一目了然地了解系统的处理流程。
