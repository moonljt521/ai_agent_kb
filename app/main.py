from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.agent import AgentManager
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="AI Agent Knowledge Base API")
agent_manager = AgentManager()

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    """返回网页界面"""
    return FileResponse("app/static/index.html")

@app.get("/chat")
async def chat(query: str):
    try:
        answer = agent_manager.run(query)
        retrieval_info = agent_manager.get_last_retrieval_info()
        
        return {
            "query": query,
            "answer": answer,
            "knowledge_base_used": retrieval_info["used_knowledge_base"],
            "used_direct_retrieval": retrieval_info["used_direct_retrieval"],  # 新增
            "retrieved_docs_count": retrieval_info["retrieved_docs_count"],
            "sources": retrieval_info["sources"],
            "data_source": "本地知识库（直接检索）" if retrieval_info["used_direct_retrieval"] 
                          else ("本地知识库" if retrieval_info["used_knowledge_base"] else "模型通用知识")
        }
    except Exception as e:
        return {"query": query, "error": str(e)}

@app.get("/model-info")
async def get_model_info():
    """获取当前使用的模型信息"""
    from app.core.embeddings import get_embedding_info
    
    # 获取 LLM 提供商和模型
    provider = os.getenv("MODEL_PROVIDER", "aliyun").lower()
    if provider == "groq":
        llm_model = os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile")
        llm_provider = "Groq"
    else:
        llm_model = os.getenv("LLM_MODEL", "qwen-plus")
        llm_provider = "阿里云"
    
    # 获取 Embedding 信息
    embedding_info = get_embedding_info()
    
    return {
        "llm": {
            "provider": llm_provider,
            "model": llm_model
        },
        "embedding": {
            "provider": embedding_info.get("provider", "unknown"),
            "model": embedding_info.get("model", "unknown"),
            "dimension": embedding_info.get("dimension", "unknown"),
            "is_free": embedding_info.get("is_free", False),
            "is_local": embedding_info.get("is_local", False)
        }
    }

@app.post("/ingest")
async def ingest_docs():
    """手动触发知识库更新"""
    try:
        agent_manager.rag.load_and_index()
        return {"status": "success", "message": "Documents indexed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/memory/history")
async def get_chat_history():
    """获取对话历史"""
    try:
        history = agent_manager.get_chat_history()
        formatted_history = []
        for msg in history:
            formatted_history.append({
                "role": "user" if msg.__class__.__name__ == "HumanMessage" else "assistant",
                "content": msg.content
            })
        return {
            "status": "success",
            "history": formatted_history,
            "count": len(formatted_history)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/memory/clear")
async def clear_memory():
    """清空对话记忆"""
    try:
        agent_manager.clear_memory()
        return {"status": "success", "message": "对话记忆已清空"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
