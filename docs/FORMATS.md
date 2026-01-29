# 📚 支持的文档格式

## 当前支持的格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| PDF | `.pdf` | PDF 文档 |
| 文本 | `.txt` | 纯文本文件 |
| Markdown | `.md` | Markdown 文档 |
| EPUB | `.epub` | 电子书格式 |

## 使用方法

### 1. 放置文档

将任意支持格式的文档放到 `data/` 目录：

```bash
# PDF
cp ~/Downloads/book.pdf data/

# EPUB
cp ~/Downloads/ebook.epub data/

# TXT
cp ~/Downloads/notes.txt data/

# Markdown
cp ~/Downloads/readme.md data/
```

### 2. 导入文档

```bash
python scripts/ingest.py
```

系统会自动识别并加载所有支持格式的文档。

## 格式说明

### PDF (.pdf)
- ✅ 最常用的文档格式
- ✅ 支持多页文档
- ✅ 保留页码信息
- 📝 使用 PyPDFLoader 加载

### TXT (.txt)
- ✅ 纯文本文件
- ✅ 简单快速
- 📝 使用 TextLoader 加载

### Markdown (.md)
- ✅ Markdown 格式文档
- ✅ 保留文本结构
- 📝 使用 TextLoader 加载

### EPUB (.epub)
- ✅ 电子书标准格式
- ✅ 支持章节结构
- ✅ 适合小说、技术书籍
- 📝 使用 UnstructuredEPubLoader 加载
- ⚠️ 需要安装 `ebooklib` 库

## 测试 EPUB 支持

如果你想测试 EPUB 文件是否能正常加载：

```bash
python test_epub.py
```

## 添加新格式支持

如果需要支持其他格式（如 DOCX、HTML 等），可以编辑 `app/core/rag.py`：

```python
from langchain_community.document_loaders import UnstructuredWordDocumentLoader

loaders = [
    DirectoryLoader(self.data_dir, glob="**/*.pdf", loader_cls=PyPDFLoader),
    DirectoryLoader(self.data_dir, glob="**/*.txt", loader_cls=TextLoader),
    DirectoryLoader(self.data_dir, glob="**/*.md", loader_cls=TextLoader),
    DirectoryLoader(self.data_dir, glob="**/*.epub", loader_cls=UnstructuredEPubLoader),
    DirectoryLoader(self.data_dir, glob="**/*.docx", loader_cls=UnstructuredWordDocumentLoader),  # 新增
]
```

## 常见问题

### Q: EPUB 文件加载失败？

A: 确保已安装 `ebooklib`：
```bash
venv/bin/python3.13 -m pip install ebooklib
```

### Q: 可以混合使用多种格式吗？

A: 可以！系统会自动识别并加载 `data/` 目录下所有支持格式的文档。

### Q: 哪种格式效果最好？

A: 
- **PDF**: 适合扫描文档、技术书籍
- **EPUB**: 适合电子书、小说
- **TXT/MD**: 适合纯文本、笔记

### Q: 文档大小有限制吗？

A: 没有硬性限制，但建议：
- 单个文档 < 100MB
- 总文档数 < 1000 个
- 文档越大，导入时间越长，费用越高

## 依赖说明

```txt
pypdf          # PDF 支持
ebooklib       # EPUB 支持
unstructured   # 通用文档解析
```

安装所有依赖：
```bash
pip install -r requirements.txt
```
