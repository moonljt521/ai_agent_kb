#!/usr/bin/env python
"""
使用 Gradio 的聊天界面
"""

import gradio as gr
from app.core.agent import AgentManager
import os
from dotenv import load_dotenv

load_dotenv()

# 初始化 Agent
agent = AgentManager()

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
    
    try:
        # 先显示"正在思考..."
        yield "🤔 正在思考..."
        time.sleep(0.3)
        
        # 调用 Agent
        answer = agent.run(message)
        
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
with gr.Blocks(title="四大名著知识问答 Agent") as demo:
    gr.Markdown(
        """
        # 🎭 四大名著知识问答 Agent
        
        基于 RAG + Agent 的智能问答系统，支持对话记忆和上下文理解
        """
    )
    
    with gr.Tabs():
        with gr.Tab("💬 对话"):
            # 使用 ChatInterface 组件，它会自动处理消息格式
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
                ],
            )
            
            # 添加清空记忆按钮
            with gr.Row():
                clear_mem_btn = gr.Button("🧠 清空记忆", size="sm")
                clear_mem_btn.click(clear_memory_and_notify)
            
            # 添加提示
            gr.Markdown("""
            💡 **提示**：
            - 推理过程会在控制台（终端）中显示
            - 使用 `verbose=True` 可以看到 Agent 的思考步骤
            - 支持上下文追问（如："他是谁？"、"这本书有多少回？"）
            """)
        
        with gr.Tab("ℹ️ 系统信息"):
            model_info = gr.Markdown(get_model_info())
            refresh_btn = gr.Button("🔄 刷新信息")
            refresh_btn.click(get_model_info, outputs=model_info)
            
            gr.Markdown(
                """
                ### 📊 系统能力
                
                - ✅ 知识库检索（四大名著完整内容）
                - ✅ 对话记忆（保留最近 5 轮对话）
                - ✅ 上下文理解（理解代词指代）
                - ✅ 智能路由（关键词直接检索）
                - ✅ 防幻觉机制
                - ✅ 9 个工具（计算、时间、文本处理、人物关系等）
                
                ### 🎯 使用技巧
                
                1. **上下文追问**: 可以使用"他"、"这本书"等代词
                2. **清空记忆**: 开始新话题前建议清空记忆
                3. **直接检索**: 包含关键词（如"是谁"、"什么"）会触发快速检索
                
                ### 💡 示例对话
                
                ```
                用户: 红楼梦的作者是谁？
                AI: 曹雪芹
                
                用户: 他是哪个朝代的？  ← 理解"他"指代曹雪芹
                AI: 清代
                
                用户: 这本书有多少回？  ← 理解"这本书"指代红楼梦
                AI: 120回
                ```
                """
            )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
