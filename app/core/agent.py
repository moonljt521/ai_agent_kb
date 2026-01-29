import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from app.core.rag import RAGManager
from app.core.keyword_matcher import KeywordMatcher
from dotenv import load_dotenv

load_dotenv()

class AgentManager:
    def __init__(self):
        # 获取模型提供商配置
        provider = os.getenv("MODEL_PROVIDER", "aliyun").lower()
        self.provider = provider
        
        # 根据提供商初始化 LLM
        if provider == "groq":
            self.llm = ChatOpenAI(
                model=os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile"),
                openai_api_base="https://api.groq.com/openai/v1",
                openai_api_key=os.getenv("GROQ_API_KEY")
            )
            print(f"✅ 使用 Groq 模型: {os.getenv('GROQ_LLM_MODEL', 'llama-3.3-70b-versatile')}")
            print("ℹ️  Groq 使用简化的 RAG 模式（不使用 Agent）")
        else:  # 默认使用阿里云
            self.llm = ChatOpenAI(
                model=os.getenv("LLM_MODEL", "qwen-plus"),
                openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
                openai_api_key=os.getenv("DASHSCOPE_API_KEY")
            )
            print(f"✅ 使用阿里云模型: {os.getenv('LLM_MODEL', 'qwen-plus')}")
        
        self.rag = RAGManager()
        self.keyword_matcher = KeywordMatcher()  # 新增：关键词匹配器
        self.last_retrieved_docs = []  # 记录最后检索的文档
        self.used_knowledge_base = False  # 标记是否使用了知识库
        self.used_direct_retrieval = False  # 标记是否使用了直接检索（不走LLM）
        
        # 打印关键词统计
        stats = self.keyword_matcher.get_statistics()
        print(f"📚 已加载 {stats['总关键词数']} 个关键词")
        print("💡 命中关键词将直接检索，节省 LLM 调用")

    def create_agent(self):
        # 1. 创建检索器
        retriever = self.rag.get_retriever()
        
        # 2. 定义工具函数
        @tool
        def search_knowledge_base(query: str) -> str:
            """搜索本地知识库中的信息。对于任何问题，都应该先使用此工具搜索知识库，看是否有相关内容。知识库中可能包含书籍、文档、技术资料等各种内容。"""
            docs = retriever.invoke(query)
            # 记录检索到的文档
            self.last_retrieved_docs = docs
            self.used_knowledge_base = True
            return "\n\n".join([d.page_content for d in docs])

        tools = [search_knowledge_base]

        # 3. 创建 Agent (新版本 LangChain 返回的是一个编译后的图)
        return create_agent(
            model=self.llm,
            tools=tools,
            system_prompt="你是一个智能助手。对于用户的任何问题，你都应该先使用 search_knowledge_base 工具搜索本地知识库。如果知识库中有相关内容，请基于知识库内容回答；如果知识库中没有相关内容，再使用你的通用知识回答。"
        )

    def run_simple_rag(self, query: str):
        """简化的 RAG 实现，不使用 Agent（适用于 Groq）"""
        # 重置状态
        self.last_retrieved_docs = []
        self.used_knowledge_base = False
        
        # 1. 检索相关文档
        retriever = self.rag.get_retriever()
        docs = retriever.invoke(query)
        self.last_retrieved_docs = docs
        
        # 2. 构建提示词
        if docs:
            self.used_knowledge_base = True
            context = "\n\n".join([doc.page_content for doc in docs])
            prompt = f"""你是一个智能助手。请基于以下知识库内容回答用户的问题。

知识库内容：
{context}

用户问题：{query}

请基于上述知识库内容回答问题。如果知识库内容不足以回答问题，可以结合你的通用知识补充。"""
        else:
            prompt = f"""你是一个智能助手。

用户问题：{query}

请回答用户的问题。"""
        
        # 3. 调用 LLM
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        return response.content

    def direct_retrieval(self, query: str) -> str:
        """
        直接检索模式 - 不使用 LLM，直接返回向量库检索结果
        适用于命中关键词的简单查询
        """
        # 重置状态
        self.last_retrieved_docs = []
        self.used_knowledge_base = True
        self.used_direct_retrieval = True
        
        # 检索相关文档
        retriever = self.rag.get_retriever()
        docs = retriever.invoke(query)
        self.last_retrieved_docs = docs
        
        if not docs:
            return "抱歉，在知识库中没有找到相关内容。"
        
        # 直接返回检索到的文档内容（不经过 LLM 加工）
        # 取前3个最相关的文档片段
        result_parts = []
        for i, doc in enumerate(docs[:3], 1):
            content = doc.page_content.strip()
            source = doc.metadata.get("source", "未知")
            page = doc.metadata.get("page", "未知")
            
            result_parts.append(f"【片段 {i}】（来源：{source}，页码：{page}）\n{content}")
        
        return "\n\n" + "\n\n".join(result_parts)

    def run(self, query: str):
        # 先检查是否命中关键词
        should_direct, reason = self.keyword_matcher.should_use_direct_retrieval(query)
        
        if should_direct:
            print(f"🎯 {reason}")
            return self.direct_retrieval(query)
        else:
            print(f"🤖 {reason}")
            # Groq 使用简化的 RAG，阿里云使用 Agent
            if self.provider == "groq":
                return self.run_simple_rag(query)
            else:
                # 重置状态
                self.last_retrieved_docs = []
                self.used_knowledge_base = False
                self.used_direct_retrieval = False
                
                graph = self.create_agent()
                # 调用图，输入消息列表
                inputs = {"messages": [{"role": "user", "content": query}]}
                result = graph.invoke(inputs)
                # 获取最后一条 AI 消息的内容
                messages = result.get("messages", [])
                if messages:
                    return messages[-1].content
                return "未能生成回复。"
    
    def get_last_retrieval_info(self):
        """获取最后一次检索的详细信息"""
        return {
            "used_knowledge_base": self.used_knowledge_base,
            "used_direct_retrieval": self.used_direct_retrieval,  # 新增
            "retrieved_docs_count": len(self.last_retrieved_docs),
            "sources": [
                {
                    "source": doc.metadata.get("source", "未知"),
                    "page": doc.metadata.get("page", "未知"),
                    "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
                for doc in self.last_retrieved_docs
            ]
        }
