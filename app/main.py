from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from app.core.agent import AgentManager
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import asyncio

load_dotenv()

app = FastAPI(title="AI Agent Knowledge Base API")

# 读取配置
enable_direct_retrieval = os.getenv("ENABLE_DIRECT_RETRIEVAL", "false").lower() == "true"
agent_manager = AgentManager(enable_direct_retrieval=enable_direct_retrieval)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 定义请求模型
class Message(BaseModel):
    role: str  # 'user' 或 'assistant'
    content: str
    timestamp: Optional[int] = None
    book: Optional[str] = None

class ChatRequest(BaseModel):
    query: str
    book: Optional[str] = None
    history: Optional[List[Message]] = []

@app.get("/")
async def root():
    """返回网页界面"""
    return FileResponse("app/static/index.html")

@app.post("/chat")
async def chat_post(request: ChatRequest):
    """
    流式聊天接口（支持多轮对话）
    
    参数:
        query: 用户问题
        book: 可选，限定检索的书名
        history: 对话历史（最近 5 轮）
    """
    async def generate():
        try:
            query = request.query
            book = request.book
            history = [msg.dict() for msg in request.history] if request.history else []
            
            # 使用历史上下文生成答案
            if book:
                answer = agent_manager.run_simple_rag_stream_with_context(
                    query, history=history, keyword_matched=False, book_filter=book
                )
            else:
                answer = agent_manager.run_stream_with_context(query, history=history)
            
            # 流式输出答案
            full_answer = ""
            for chunk in answer:
                full_answer += chunk
                # 发送文本块
                yield f"data: {json.dumps({'type': 'text', 'content': chunk}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)
            
            # 获取检索信息
            retrieval_info = agent_manager.get_last_retrieval_info()
            
            # 发送元数据
            metadata = {
                "type": "metadata",
                "query": query,
                "book_filter": book,
                "has_context": len(history) > 0,
                "knowledge_base_used": retrieval_info["used_knowledge_base"],
                "used_direct_retrieval": retrieval_info["used_direct_retrieval"],
                "used_few_shot": retrieval_info["used_few_shot"],
                "keyword_matched": retrieval_info["keyword_matched"],
                "retrieved_docs_count": retrieval_info["retrieved_docs_count"],
                "sources": retrieval_info["sources"]
            }
            yield f"data: {json.dumps(metadata, ensure_ascii=False)}\n\n"
            
            # 发送结束标记
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
            
        except ConnectionError as e:
            # Ollama 连接错误
            provider = os.getenv("MODEL_PROVIDER", "aliyun")
            if provider == "ollama":
                error_msg = "无法连接到 Ollama 服务。请确保 Ollama 正在运行（访问 http://127.0.0.1:11434/ 检查）"
            else:
                error_msg = f"连接 {provider} 服务失败，请检查网络连接"
            error_data = {"type": "error", "error": error_msg}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        except Exception as e:
            # 其他错误的友好提示
            error_str = str(e)
            provider = os.getenv("MODEL_PROVIDER", "aliyun")
            
            # 根据错误类型提供友好提示
            if "502" in error_str or "Bad Gateway" in error_str:
                if provider == "ollama":
                    error_msg = "Ollama 服务未响应。请检查：\n1. Ollama 是否正在运行\n2. 模型是否已下载（ollama list）\n3. 访问 http://127.0.0.1:11434/ 验证服务状态"
                else:
                    error_msg = f"{provider} 服务暂时不可用，请稍后重试"
            elif "timeout" in error_str.lower():
                error_msg = "请求超时，请检查网络连接或稍后重试"
            elif "api" in error_str.lower() and "key" in error_str.lower():
                error_msg = f"API Key 配置错误，请检查 .env 文件中的 {provider.upper()}_API_KEY"
            else:
                error_msg = f"处理请求时出错：{error_str}"
            
            error_data = {"type": "error", "error": error_msg}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/chat")
async def chat_get(query: str, book: str = None):
    """
    流式聊天接口（GET 方法，兼容旧版本）
    
    参数:
        query: 用户问题
        book: 可选，限定检索的书名（如 "红楼梦"）
    """
    async def generate():
        try:
            # 如果指定了书名，传递给 agent
            if book:
                answer = agent_manager.run_simple_rag_stream(query, keyword_matched=False, book_filter=book)
            else:
                answer = agent_manager.run_stream(query)
            
            # 流式输出答案
            full_answer = ""
            for chunk in answer:
                full_answer += chunk
                # 发送文本块
                yield f"data: {json.dumps({'type': 'text', 'content': chunk}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)  # 控制输出速度
            
            # 获取检索信息
            retrieval_info = agent_manager.get_last_retrieval_info()
            
            # 发送元数据
            metadata = {
                "type": "metadata",
                "query": query,
                "book_filter": book,
                "has_context": False,
                "knowledge_base_used": retrieval_info["used_knowledge_base"],
                "used_direct_retrieval": retrieval_info["used_direct_retrieval"],
                "used_few_shot": retrieval_info["used_few_shot"],
                "keyword_matched": retrieval_info["keyword_matched"],
                "retrieved_docs_count": retrieval_info["retrieved_docs_count"],
                "sources": retrieval_info["sources"]
            }
            yield f"data: {json.dumps(metadata, ensure_ascii=False)}\n\n"
            
            # 发送结束标记
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
            
        except ConnectionError as e:
            # Ollama 连接错误
            provider = os.getenv("MODEL_PROVIDER", "aliyun")
            if provider == "ollama":
                error_msg = "无法连接到 Ollama 服务。请确保 Ollama 正在运行（访问 http://127.0.0.1:11434/ 检查）"
            else:
                error_msg = f"连接 {provider} 服务失败，请检查网络连接"
            error_data = {"type": "error", "error": error_msg}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        except Exception as e:
            # 其他错误的友好提示
            error_str = str(e)
            provider = os.getenv("MODEL_PROVIDER", "aliyun")
            
            # 根据错误类型提供友好提示
            if "502" in error_str or "Bad Gateway" in error_str:
                if provider == "ollama":
                    error_msg = "Ollama 服务未响应。请检查：\n1. Ollama 是否正在运行\n2. 模型是否已下载（ollama list）\n3. 访问 http://127.0.0.1:11434/ 验证服务状态"
                else:
                    error_msg = f"{provider} 服务暂时不可用，请稍后重试"
            elif "timeout" in error_str.lower():
                error_msg = "请求超时，请检查网络连接或稍后重试"
            elif "api" in error_str.lower() and "key" in error_str.lower():
                error_msg = f"API Key 配置错误，请检查 .env 文件中的 {provider.upper()}_API_KEY"
            else:
                error_msg = f"处理请求时出错：{error_str}"
            
            error_data = {"type": "error", "error": error_msg}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/ingest")
async def ingest_docs():
    """手动触发知识库更新"""
    try:
        agent_manager.rag.load_and_index()
        return {"status": "success", "message": "Documents indexed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/books")
async def get_books():
    """获取知识库中的所有书籍列表"""
    try:
        books = agent_manager.rag.get_books_list()
        stats = agent_manager.rag.get_tag_statistics()
        return {
            "books": books,
            "statistics": stats
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/config")
async def get_config():
    """获取当前配置信息（LLM 和 Embedding 模型）"""
    try:
        model_provider = os.getenv("MODEL_PROVIDER", "aliyun")
        
        # LLM 模型信息
        if model_provider == "aliyun":
            llm_model = os.getenv("LLM_MODEL", "qwen-plus")
            llm_display = f"阿里云 {llm_model}"
        elif model_provider == "groq":
            llm_model = os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile")
            llm_display = f"Groq {llm_model}"
        elif model_provider == "ollama":
            llm_model = os.getenv("OLLAMA_LLM_MODEL", "qwen3:8b")
            llm_display = f"Ollama {llm_model} (本地)"
        else:
            llm_display = "未知"
        
        # Embedding 模型信息（仅本地）
        embedding_model = os.getenv("LOCAL_EMBEDDING_MODEL", "BAAI/bge-large-zh-v1.5")
        if "bge-large-zh" in embedding_model:
            embedding_display = "BGE-large-zh-v1.5 (本地)"
        elif "bge" in embedding_model:
            embedding_display = "BGE (本地)"
        else:
            embedding_display = f"{embedding_model.split('/')[-1]} (本地)"
        
        return {
            "llm_model": llm_display,
            "embedding_model": embedding_display,
            "model_provider": model_provider,
            "enable_direct_retrieval": enable_direct_retrieval
        }
    except Exception as e:
        return {"error": str(e)}
