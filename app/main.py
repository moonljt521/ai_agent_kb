from fastapi import FastAPI
from app.core.agent import AgentManager
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="AI Agent Knowledge Base API")
agent_manager = AgentManager()

@app.get("/")
async def root():
    return {"message": "AI Agent Knowledge Base is running"}

@app.get("/chat")
async def chat(query: str):
    try:
        answer = agent_manager.run(query)
        retrieval_info = agent_manager.get_last_retrieval_info()
        
        return {
            "query": query,
            "answer": answer,
            "knowledge_base_used": retrieval_info["used_knowledge_base"],
            "retrieved_docs_count": retrieval_info["retrieved_docs_count"],
            "sources": retrieval_info["sources"],
            "data_source": "本地知识库" if retrieval_info["used_knowledge_base"] else "模型通用知识"
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
