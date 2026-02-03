#!/usr/bin/env python
"""
使用 Gradio 的聊天界面
支持文本对话和图片上传（证件照生成）
"""

import gradio as gr
from app.core.agent import AgentManager
import os
from dotenv import load_dotenv
from PIL import Image
import tempfile

load_dotenv()

# 初始化 Agent
agent = AgentManager()

# 全局变量存储上传的图片路径
uploaded_image_path = None

def handle_image_upload(image):
    """处理图片上传"""
    global uploaded_image_path
    
    if image is None:
        uploaded_image_path = None
        return "📷 请上传图片"
    
    try:
        # 保存上传的图片到临时文件
        temp_dir = "app/static/uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 生成临时文件名
        import time
        filename = f"upload_{int(time.time())}.jpg"
        filepath = os.path.join(temp_dir, filename)
        
        # 保存图片
        if isinstance(image, str):
            # 如果是文件路径
            img = Image.open(image)
        else:
            # 如果是 numpy array
            img = Image.fromarray(image)
        
        img.save(filepath, "JPEG")
        uploaded_image_path = filepath
        
        return f"✅ 图片上传成功！\n\n现在您可以要求生成证件照，例如：\n- 生成1寸白底证件照\n- 生成2寸蓝底证件照\n- 生成护照照片"
        
    except Exception as e:
        uploaded_image_path = None
        return f"❌ 图片上传失败：{str(e)}"


def chat(message, history):
    """
    处理聊天消息（流式输出）
    
    Args:
        message: 用户输入的消息
        history: 对话历史 [[user_msg, bot_msg], ...]
    
    Yields:
        逐步生成的回复消息
    """
    import time
    import re
    import os
    from PIL import Image as PILImage
    
    try:
        # 如果用户提到证件照相关内容，且有上传的图片，自动添加图片路径
        global uploaded_image_path
        
        if uploaded_image_path and any(keyword in message for keyword in ["证件照", "1寸", "2寸", "护照", "身份证", "蓝底", "白底", "红底", "生成"]):
            # 在消息中明确添加图片路径信息，让 Agent 能够识别
            message = f"{message}\n\n【系统提示】用户已上传图片，路径为：{uploaded_image_path}"
        
        # 先显示"正在思考..."
        yield "🤔 正在思考..."
        time.sleep(0.3)
        
        # 调用 Agent
        answer = agent.run(message)
        
        # 检查是否包含图片路径标记
        image_match = re.search(r'\[IMAGE_PATH:(.*?)\]', answer)
        generated_image_path = None
        
        if image_match:
            image_path = image_match.group(1).strip()  # 去除空格
            
            # 移除标记
            answer = answer.replace(image_match.group(0), "")
            
            # 检查文件是否存在
            if os.path.exists(image_path):
                generated_image_path = image_path
                
                # 获取文件信息
                filename = os.path.basename(image_path)
                file_size = os.path.getsize(image_path)
                
                # 读取图片尺寸
                try:
                    img = PILImage.open(image_path)
                    img_size = f"{img.size[0]} x {img.size[1]} px"
                except:
                    img_size = "未知"
                
                # 在答案中添加图片信息和提示
                answer = answer.strip() + f"\n\n---\n\n### 📸 生成的证件照\n\n"
                answer += f"**文件名**: {filename}\n\n"
                answer += f"**尺寸**: {img_size}\n\n"
                answer += f"**文件大小**: {file_size / 1024:.1f} KB\n\n"
                answer += f"**保存路径**: `{image_path}`\n\n"
                answer += f"💡 **提示**: 图片已保存到本地，您可以在文件管理器中打开查看，或者使用下面的路径直接访问。\n\n"
                
                # 尝试使用 Gradio 的图片显示（如果支持）
                # 注意：ChatInterface 的 Markdown 可能不支持本地图片
                # 我们提供文件路径让用户可以手动打开
                answer += f"📂 **文件路径**: `{os.path.abspath(image_path)}`\n\n"
                
            else:
                answer = answer.strip() + f"\n\n⚠️ 图片文件未找到: {image_path}"
        
        # 获取检索信息
        retrieval_info = agent.get_last_retrieval_info()
        
        # 获取调用信息
        call_info = agent.get_last_call_info()
        
        # 添加调用信息（在答案前面）
        debug_info = "\n\n---\n### 🔍 调用信息\n\n"
        
        # 模式信息
        mode_map = {
            "agent": "🤖 Agent 推理（ReAct 模式）",
            "simple_rag": "📚 简化 RAG（Groq 模式）"
        }
        debug_info += f"**模式**: {mode_map.get(call_info['mode'], '未知')}\n\n"
        
        # LLM 调用
        debug_info += f"**LLM 调用**: {'✅ 是' if call_info['llm_called'] else '❌ 否'}\n\n"
        
        # 工具使用
        if call_info['tools_used']:
            tools_str = ", ".join(call_info['tools_used'])
            debug_info += f"**使用的工具**: {tools_str}\n\n"
        else:
            debug_info += f"**使用的工具**: 无\n\n"
        
        # 知识库信息
        if retrieval_info["used_knowledge_base"]:
            debug_info += f"**知识库**: ✅ 已使用\n\n"
            if retrieval_info["sources"]:
                debug_info += f"**文档数量**: {retrieval_info['retrieved_docs_count']} 个\n\n"
        else:
            debug_info += f"**知识库**: ❌ 未使用\n\n"
        
        # 将调试信息添加到答案后面
        answer += debug_info
        
        # 流式输出答案（模拟打字效果）
        current_text = ""
        for i, char in enumerate(answer):
            current_text += char
            # 每5个字符更新一次，或遇到标点符号
            if i % 5 == 0 or char in '，。！？；：\n':
                yield current_text
                time.sleep(0.02)  # 添加小延迟
        
        # 确保输出完整答案
        yield answer
            
    except Exception as e:
        yield f"❌ 错误: {str(e)}"
        yield f"❌ 错误: {str(e)}"

def clear_memory_and_notify():
    """清空对话记忆并通知"""
    agent.clear_memory()
    return gr.Info("✅ 对话记忆已清空")

def get_latest_generated_photo():
    """获取最新生成的证件照"""
    photos_dir = "app/static/photos"
    
    if not os.path.exists(photos_dir):
        return None
    
    # 获取所有照片文件
    photos = []
    for f in os.listdir(photos_dir):
        if f.endswith(('.jpg', '.jpeg', '.png')) and f.startswith('id_photo_'):
            filepath = os.path.join(photos_dir, f)
            photos.append((filepath, os.path.getmtime(filepath)))
    
    if not photos:
        return None
    
    # 按修改时间排序，返回最新的
    photos.sort(key=lambda x: x[1], reverse=True)
    return photos[0][0]

def get_model_info():
    """获取模型信息"""
    provider = os.getenv("MODEL_PROVIDER", "aliyun").lower()
    if provider == "groq":
        llm_model = os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile")
        llm_provider = "Groq"
    else:
        llm_model = os.getenv("LLM_MODEL", "qwen-plus")
        llm_provider = "阿里云"
    
    from app.core.embeddings import get_embedding_info
    embedding_info = get_embedding_info()
    
    info = f"""
### 🤖 当前模型配置

**LLM 模型**: {llm_provider} - {llm_model}  
**Embedding 模型**: {embedding_info.get('model', 'unknown')}  
**向量维度**: {embedding_info.get('dimension', 'unknown')}  
**是否免费**: {'✅ 是' if embedding_info.get('is_free') else '❌ 否'}  
**是否本地**: {'✅ 是' if embedding_info.get('is_local') else '❌ 否'}
"""
    return info

# 创建 Gradio 界面
with gr.Blocks(title="四大名著知识问答 + 证件照生成 Agent") as demo:
    gr.Markdown(
        """
        # 🎭 四大名著知识问答 + 📸 证件照生成 Agent
        
        基于 RAG + Agent 的智能问答系统，支持对话记忆、上下文理解和证件照生成
        """
    )
    
    with gr.Tabs():
        with gr.Tab("💬 对话"):
            with gr.Row():
                with gr.Column(scale=2):
                    # 使用 ChatInterface 组件
                    chat_interface = gr.ChatInterface(
                        fn=chat,
                        chatbot=gr.Chatbot(height=500),
                        textbox=gr.Textbox(placeholder="输入你的问题...", container=False, scale=7),
                        examples=[
                            "红楼梦的作者是谁？",
                            "计算一下 123 + 456",
                            "贾宝玉和林黛玉是什么关系？",
                            "现在几点了？",
                            "列出四大名著",
                            "支持哪些证件照规格？",
                        ],
                    )
                    
                    # 添加清空记忆按钮
                    with gr.Row():
                        clear_mem_btn = gr.Button("🧠 清空记忆", size="sm")
                        clear_mem_btn.click(clear_memory_and_notify)
                
                with gr.Column(scale=1):
                    gr.Markdown("### 📸 证件照生成")
                    
                    image_input = gr.Image(
                        label="1. 上传照片",
                        type="filepath",
                        height=250
                    )
                    
                    upload_status = gr.Textbox(
                        label="上传状态",
                        value="📷 请上传图片",
                        interactive=False,
                        lines=3
                    )
                    
                    # 添加生成的证件照显示区域
                    gr.Markdown("### 2. 生成的证件照")
                    generated_image = gr.Image(
                        label="生成结果",
                        type="filepath",
                        height=300,
                        interactive=False
                    )
                    
                    # 添加刷新按钮
                    refresh_btn = gr.Button("🔄 刷新显示最新照片", size="sm")
                    refresh_btn.click(
                        fn=get_latest_generated_photo,
                        outputs=generated_image
                    )
                    
                    image_input.change(
                        fn=handle_image_upload,
                        inputs=image_input,
                        outputs=upload_status
                    )
                    
                    gr.Markdown("""
                    **使用方法：**
                    1. 上传您的照片
                    2. 在对话框中输入要求，例如：
                       - "生成1寸白底证件照"
                       - "生成2寸蓝底证件照"
                    3. 生成的照片会显示在上方
                    4. 如未显示，点击"刷新显示"
                    """)
            
            # 添加提示
            gr.Markdown("""
            💡 **提示**：
            - 推理过程会在控制台（终端）中显示
            - 使用 `verbose=True` 可以看到 Agent 的思考步骤
            - 支持上下文追问（如："他是谁？"、"这本书有多少回？"）
            - 证件照会自动检测人脸并智能裁剪
            """)
        
        with gr.Tab("ℹ️ 系统信息"):
            model_info = gr.Markdown(get_model_info())
            refresh_btn = gr.Button("🔄 刷新信息")
            refresh_btn.click(get_model_info, outputs=model_info)
            
            gr.Markdown(
                """
                ### 📊 系统能力
                
                **知识问答：**
                - ✅ 知识库检索（四大名著完整内容）
                - ✅ 对话记忆（保留最近 5 轮对话）
                - ✅ 上下文理解（理解代词指代）
                - ✅ 智能路由（关键词直接检索）
                - ✅ 防幻觉机制
                - ✅ 11 个工具（计算、时间、文本处理、人物关系、证件照生成等）
                
                **证件照生成：**
                - ✅ 自动人脸检测和智能裁剪
                - ✅ 背景移除和替换
                - ✅ 10+ 种标准尺寸（1寸、2寸、护照等）
                - ✅ 4 种背景颜色（白色、蓝色、红色、浅蓝）
                - ✅ 图像质量增强
                - ✅ 高清输出（300 DPI）
                
                ### 🎯 使用技巧
                
                **知识问答：**
                1. **上下文追问**: 可以使用"他"、"这本书"等代词
                2. **清空记忆**: 开始新话题前建议清空记忆
                3. **直接检索**: 包含关键词（如"是谁"、"什么"）会触发快速检索
                
                **证件照生成：**
                1. **上传照片**: 支持 JPG、PNG 等常见格式
                2. **人脸居中**: 拍照时确保人脸清晰、居中
                3. **光线充足**: 使用光线充足的照片效果更好
                4. **多种规格**: 可以一次生成多个尺寸
                
                ### 💡 示例对话
                
                **知识问答：**
                ```
                用户: 红楼梦的作者是谁？
                AI: 曹雪芹
                
                用户: 他是哪个朝代的？  ← 理解"他"指代曹雪芹
                AI: 清代
                
                用户: 这本书有多少回？  ← 理解"这本书"指代红楼梦
                AI: 120回
                ```
                
                **证件照生成：**
                ```
                用户: [上传照片] 生成1寸白底证件照
                AI: ✅ 已成功生成 1寸 白色底证件照！
                    📏 尺寸：295 x 413 px
                    📥 下载链接：/static/photos/id_photo_1寸_白色_20240130_153045.jpg
                
                用户: 再生成一个2寸蓝底的
                AI: ✅ 已成功生成 2寸 蓝色底证件照！
                    📏 尺寸：413 x 579 px
                    📥 下载链接：/static/photos/id_photo_2寸_蓝色_20240130_153102.jpg
                ```
                """
            )

if __name__ == "__main__":
    # 启动服务
    # allowed_paths 参数允许 Gradio 在界面中显示这些目录的文件
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        allowed_paths=["app/static/photos", "app/static/uploads"]
    )
