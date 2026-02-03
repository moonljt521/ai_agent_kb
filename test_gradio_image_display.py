#!/usr/bin/env python3
"""测试 Gradio 图片显示方式"""

import gradio as gr
import os
from PIL import Image

# 测试不同的图片显示方式

def test_image_display(method):
    """测试不同的图片显示方法"""
    
    # 使用一个已存在的图片
    test_image = "app/static/photos/id_photo_2寸_blue_20260203_162931.jpg"
    
    if not os.path.exists(test_image):
        return "❌ 测试图片不存在"
    
    abs_path = os.path.abspath(test_image)
    
    if method == "markdown":
        # 方法 1: Markdown 格式
        return f"## 方法 1: Markdown\n\n![测试图片]({abs_path})"
    
    elif method == "markdown_file":
        # 方法 2: Markdown with file= prefix
        return f"## 方法 2: Markdown with file=\n\n![测试图片](file={abs_path})"
    
    elif method == "html":
        # 方法 3: HTML img 标签
        return f'## 方法 3: HTML\n\n<img src="{abs_path}" width="300">'
    
    elif method == "relative":
        # 方法 4: 相对路径
        rel_path = os.path.relpath(test_image)
        return f"## 方法 4: 相对路径\n\n![测试图片]({rel_path})"
    
    elif method == "info":
        # 显示图片信息
        img = Image.open(test_image)
        return f"""## 图片信息
        
**路径**: {test_image}
**绝对路径**: {abs_path}
**相对路径**: {os.path.relpath(test_image)}
**尺寸**: {img.size}
**格式**: {img.format}
**文件大小**: {os.path.getsize(test_image)} bytes
"""

with gr.Blocks() as demo:
    gr.Markdown("# Gradio 图片显示测试")
    
    with gr.Row():
        method_dropdown = gr.Dropdown(
            choices=["markdown", "markdown_file", "html", "relative", "info"],
            value="info",
            label="选择测试方法"
        )
        test_btn = gr.Button("测试")
    
    output = gr.Markdown()
    
    test_btn.click(
        fn=test_image_display,
        inputs=method_dropdown,
        outputs=output
    )
    
    gr.Markdown("""
    ## 说明
    
    测试 Gradio 中显示图片的不同方法：
    
    1. **markdown**: 标准 Markdown 格式 `![](path)`
    2. **markdown_file**: 带 file= 前缀 `![](file=path)`
    3. **html**: HTML img 标签
    4. **relative**: 使用相对路径
    5. **info**: 显示图片信息
    
    **注意**: Gradio 需要在 `launch()` 时设置 `allowed_paths` 才能访问本地文件
    """)

if __name__ == "__main__":
    demo.launch(
        server_port=7861,
        allowed_paths=["app/static/photos", "app/static/uploads"]
    )
