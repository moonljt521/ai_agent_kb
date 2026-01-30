import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from app.core.rag import RAGManager
from app.core.keyword_matcher import KeywordMatcher
from app.core.few_shot_manager import FewShotManager
from dotenv import load_dotenv

load_dotenv()

class AgentManager:
    def __init__(self, enable_few_shot=True, enable_direct_retrieval=False):
        # 获取模型提供商配置
        provider = os.getenv("MODEL_PROVIDER", "aliyun").lower()
        self.provider = provider
        self.enable_few_shot = enable_few_shot
        self.enable_direct_retrieval = enable_direct_retrieval  # 新增：是否启用直接检索
        
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
        self.keyword_matcher = KeywordMatcher()
        self.few_shot_manager = FewShotManager() if enable_few_shot else None
        self.last_retrieved_docs = []
        self.used_knowledge_base = False
        self.used_direct_retrieval = False
        self.used_few_shot = False
        self.keyword_matched = False  # 新增：标记是否命中关键词
        
        # 打印关键词统计
        stats = self.keyword_matcher.get_statistics()
        print(f"📚 已加载 {stats['总关键词数']} 个关键词")
        if self.enable_direct_retrieval:
            print("💡 命中关键词将使用增强检索（k=8），提高准确度")
        else:
            print("💡 关键词检查已禁用，所有查询使用标准检索（k=5）")
        
        # 打印 Few-Shot 统计
        if self.few_shot_manager:
            few_shot_stats = self.few_shot_manager.get_statistics()
            print(f"📝 已加载 {few_shot_stats['总示例数']} 个 Few-Shot 示例")
            print("💡 Few-Shot 将统一回答格式和风格")

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

    def run_simple_rag(self, query: str, keyword_matched=False, book_filter=None):
        """
        简化的 RAG 实现，不使用 Agent（适用于 Groq）
        
        参数:
            query: 用户查询
            keyword_matched: 是否命中关键词（用于优化检索策略）
            book_filter: 书名过滤（如 "红楼梦"），只检索指定书籍
        """
        # 重置状态
        self.last_retrieved_docs = []
        self.used_knowledge_base = False
        self.used_few_shot = False
        self.keyword_matched = keyword_matched  # 记录是否命中关键词
        
        # 1. 检索相关文档
        # 如果命中关键词，增加检索数量以获得更全面的信息
        k = 8 if keyword_matched else 5
        
        # 如果指定了书名过滤
        if book_filter:
            print(f"📚 限定检索范围：{book_filter}")
            docs = self.rag.search_by_book(query, book_filter, k=k)
        else:
            retriever = self.rag.get_retriever(k=k)
            docs = retriever.invoke(query)
        
        self.last_retrieved_docs = docs
        
        if keyword_matched:
            print(f"🎯 命中关键词，使用增强检索（k={k}）")
        
        # 2. 构建提示词
        if docs:
            self.used_knowledge_base = True
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # 使用 Few-Shot（如果启用）
            if self.few_shot_manager:
                self.used_few_shot = True
                prompt = self.few_shot_manager.build_few_shot_prompt(query, context)
            else:
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
    
    def run_simple_rag_stream(self, query: str, keyword_matched=False, book_filter=None):
        """
        简化的 RAG 实现（流式版本）
        
        参数:
            query: 用户查询
            keyword_matched: 是否命中关键词（用于优化检索策略）
            book_filter: 书名过滤（如 "红楼梦"），只检索指定书籍
        
        返回:
            生成器，逐个返回文本块
        """
        # 重置状态
        self.last_retrieved_docs = []
        self.used_knowledge_base = False
        self.used_few_shot = False
        self.keyword_matched = keyword_matched
        
        # 1. 检索相关文档
        k = 8 if keyword_matched else 5
        
        if book_filter:
            print(f"📚 限定检索范围：{book_filter}")
            docs = self.rag.search_by_book(query, book_filter, k=k)
        else:
            retriever = self.rag.get_retriever(k=k)
            docs = retriever.invoke(query)
        
        self.last_retrieved_docs = docs
        
        if keyword_matched:
            print(f"🎯 命中关键词，使用增强检索（k={k}）")
        
        # 2. 构建提示词
        if docs:
            self.used_knowledge_base = True
            context = "\n\n".join([doc.page_content for doc in docs])
            
            if self.few_shot_manager:
                self.used_few_shot = True
                prompt = self.few_shot_manager.build_few_shot_prompt(query, context)
            else:
                prompt = f"""你是一个智能助手。请基于以下知识库内容回答用户的问题。

知识库内容：
{context}

用户问题：{query}

请基于上述知识库内容回答问题。如果知识库内容不足以回答问题，可以结合你的通用知识补充。"""
        else:
            prompt = f"""你是一个智能助手。

用户问题：{query}

请回答用户的问题。"""
        
        # 3. 流式调用 LLM
        messages = [HumanMessage(content=prompt)]
        for chunk in self.llm.stream(messages):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
    
    def run_stream(self, query: str):
        """流式运行（入口方法）"""
        # 检查是否启用直接检索
        if self.enable_direct_retrieval:
            should_direct, reason = self.keyword_matcher.should_use_direct_retrieval(query)
            
            if should_direct:
                print(f"🎯 {reason}")
                return self.run_simple_rag_stream(query, keyword_matched=True)
            else:
                print(f"🤖 {reason}")
        
        # 未命中关键词或未启用直接检索
        return self.run_simple_rag_stream(query, keyword_matched=False)

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
        # 检查是否启用直接检索
        if self.enable_direct_retrieval:
            # 先检查是否命中关键词
            should_direct, reason = self.keyword_matcher.should_use_direct_retrieval(query)
            
            if should_direct:
                print(f"🎯 {reason}")
                # 不再直接返回检索结果，而是传递给 LLM 处理
                # return self.direct_retrieval(query)  # 旧方式：直接返回
                
                # 新方式：命中关键词时使用增强检索，但仍通过 LLM 处理
                if self.provider == "groq":
                    return self.run_simple_rag(query, keyword_matched=True)
                else:
                    # 阿里云 Agent 模式暂时保持原样
                    return self.run_agent_mode(query)
            else:
                print(f"🤖 {reason}")
        
        # 未命中关键词或未启用直接检索
        # Groq 使用简化的 RAG，阿里云使用 Agent
        if self.provider == "groq":
            return self.run_simple_rag(query, keyword_matched=False)
        else:
            return self.run_agent_mode(query)
    
    def run_agent_mode(self, query: str):
        """阿里云 Agent 模式"""
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
            "used_direct_retrieval": self.used_direct_retrieval,
            "used_few_shot": self.used_few_shot,
            "keyword_matched": self.keyword_matched,  # 新增：是否命中关键词
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
