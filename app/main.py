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
async def chat(query: str):
    try:
        answer = agent_manager.run(query)
        retrieval_info = agent_manager.get_last_retrieval_info()
        
        return {
            "query": query,
            "answer": answer,
            "knowledge_base_used": retrieval_info["used_knowledge_base"],
            "used_direct_retrieval": retrieval_info["used_direct_retrieval"],
            "used_few_shot": retrieval_info["used_few_shot"],  # 新增
            "retrieved_docs_count": retrieval_info["retrieved_docs_count"],
            "sources": retrieval_info["sources"],
            "data_source": "本地知识库（直接检索）" if retrieval_info["used_direct_retrieval"] 
                          else ("本地知识库" if retrieval_info["used_knowledge_base"] else "模型通用知识")
        }
    except Exception as e:
        return {"query": query, "error": str(e)}

@app.post("/ingest")
async def ingest_docs():
    """手动触发知识库更新"""
    try:
        agent_manager.rag.load_and_index()
        return {"status": "success", "message": "Documents indexed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
