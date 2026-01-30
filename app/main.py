from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from app.core.agent import AgentManager
from dotenv import load_dotenv
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

@app.get("/")
async def root():
    """返回网页界面"""
    return FileResponse("app/static/index.html")

@app.get("/chat")
async def chat(query: str, book: str = None):
    """
    流式聊天接口
    
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
            
        except Exception as e:
            error_data = {"type": "error", "error": str(e)}
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
