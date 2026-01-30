from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.agent import AgentManager
from dotenv import load_dotenv
import os

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
    聊天接口
    
    参数:
        query: 用户问题
        book: 可选，限定检索的书名（如 "红楼梦"）
    """
    try:
        # 如果指定了书名，传递给 agent
        if book:
            # 临时修改 run_simple_rag 调用
            answer = agent_manager.run_simple_rag(query, keyword_matched=False, book_filter=book)
        else:
            answer = agent_manager.run(query)
        
        retrieval_info = agent_manager.get_last_retrieval_info()
        
        return {
            "query": query,
            "answer": answer,
            "book_filter": book,  # 新增：返回书名过滤信息
            "knowledge_base_used": retrieval_info["used_knowledge_base"],
            "used_direct_retrieval": retrieval_info["used_direct_retrieval"],
            "used_few_shot": retrieval_info["used_few_shot"],
            "keyword_matched": retrieval_info["keyword_matched"],
            "retrieved_docs_count": retrieval_info["retrieved_docs_count"],
            "sources": retrieval_info["sources"],
            "data_source": "本地知识库（直接检索）" if retrieval_info["used_direct_retrieval"] 
                          else ("本地知识库" if retrieval_info["used_knowledge_base"] else "模型通用知识")
        }
    except Exception as e:
        return {"query": query, "error": str(e)}

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
        embedding_type = os.getenv("EMBEDDING_TYPE", "local")
        
        # LLM 模型信息
        if model_provider == "aliyun":
            llm_model = os.getenv("LLM_MODEL", "qwen-plus")
            llm_display = f"阿里云 {llm_model}"
        elif model_provider == "groq":
            llm_model = os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile")
            llm_display = f"Groq {llm_model}"
        else:
            llm_display = "未知"
        
        # Embedding 模型信息
        if embedding_type == "aliyun":
            embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
            embedding_display = f"阿里云 {embedding_model}"
        elif embedding_type == "local":
            embedding_model = os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            # 简化显示名称
            if "bge-large-zh" in embedding_model:
                embedding_display = "BGE-large-zh-v1.5 (本地)"
            elif "bge" in embedding_model:
                embedding_display = "BGE (本地)"
            else:
                embedding_display = f"{embedding_model.split('/')[-1]} (本地)"
        else:
            embedding_display = "未知"
        
        return {
            "llm_model": llm_display,
            "embedding_model": embedding_display,
            "model_provider": model_provider,
            "embedding_type": embedding_type,
            "enable_direct_retrieval": enable_direct_retrieval
        }
    except Exception as e:
        return {"error": str(e)}
