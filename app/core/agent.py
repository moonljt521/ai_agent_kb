import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from app.core.rag import RAGManager
from app.core.tools import get_all_tools
from dotenv import load_dotenv

load_dotenv()

class SimpleMemory:
    """简单的对话记忆，保留最近 k 轮对话"""
    def __init__(self, k=5):
        self.k = k
        self.messages = []
    
    def save_context(self, inputs, outputs):
        """保存对话"""
        self.messages.append(HumanMessage(content=inputs["input"]))
        self.messages.append(AIMessage(content=outputs["output"]))
        # 只保留最近 k 轮（k*2 条消息）
        if len(self.messages) > self.k * 2:
            self.messages = self.messages[-(self.k * 2):]
    
    def load_memory_variables(self, inputs=None):
        """加载记忆"""
        return {"chat_history": self.messages}
    
    def clear(self):
        """清空记忆"""
        self.messages = []


class AgentManager:
    def __init__(self, session_id: str = "default"):
        # 获取模型提供商配置
        provider = os.getenv("MODEL_PROVIDER", "aliyun").lower()
        self.provider = provider
        self.session_id = session_id
        
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
        
        # 新增：记忆系统（保留最近5轮对话）
        self.memory = SimpleMemory(k=5)
        
        # 记录状态
        self.last_call_info = {
            "mode": None,
            "llm_called": False,
            "tools_used": [],
            "keyword_matched": None,
        }
        self.last_retrieved_docs = []
        self.used_knowledge_base = False
        self.used_direct_retrieval = False
        
        # 打印关键词统计
        print(f"🧠 记忆系统已启用（保留最近 5 轮对话）")

    def create_agent(self, chat_history=None):
        # 1. 创建检索器
        retriever = self.rag.get_retriever()
        
        # 2. 定义知识库检索工具
        @tool
        def search_knowledge_base(query: str) -> str:
            """搜索本地知识库中的信息。对于任何问题，都应该先使用此工具搜索知识库，看是否有相关内容。知识库中包含四大名著（红楼梦、三国演义、西游记、水浒传）的完整内容。"""
            docs = retriever.invoke(query)
            # 记录检索到的文档
            self.last_retrieved_docs = docs
            self.used_knowledge_base = True
            
            # 防幻觉机制：如果没有检索到文档，明确返回
            if not docs:
                return "【知识库检索结果】未找到相关内容。请告知用户：知识库中没有关于这个问题的信息。"
            
            # 防幻觉机制：如果检索结果太少，标注警告
            if len(docs) < 2:
                return f"【知识库检索结果】仅找到少量相关内容，请谨慎回答：\n\n{docs[0].page_content}\n\n【注意】如果内容不足以完整回答问题，请明确告知用户。"
            
            return "\n\n".join([d.page_content for d in docs])

        # 3. 获取所有工具（知识库检索 + 通用工具）
        tools = [search_knowledge_base] + get_all_tools()
        
        print(f"🔧 Agent 已加载 {len(tools)} 个工具：")
        for i, t in enumerate(tools, 1):
            print(f"   {i}. {t.name} - {t.description[:50]}...")

        # 4. 构建系统提示（包含对话历史）
        history_text = ""
        if chat_history:
            history_text = "\n\n【对话历史】\n"
            for msg in chat_history:
                role = "用户" if isinstance(msg, HumanMessage) else "AI"
                history_text += f"{role}: {msg.content}\n"
            history_text += "\n注意：理解对话历史中的上下文，特别是代词（如\"他\"、\"这本书\"）的指代关系。\n"

        system_prompt = f"""你是一个功能强大的 AI Agent，专门回答关于中国四大名著的问题。
{history_text}
【你的能力】
1. 搜索知识库：search_knowledge_base - 搜索四大名著的完整内容
2. 数学计算：calculator - 进行数学运算
3. 时间查询：get_current_time - 获取当前时间
4. 文本统计：count_characters - 统计文本信息
5. 文本搜索：text_search - 在文本中搜索关键词
6. 数字比较：compare_numbers - 比较数字大小
7. 名著列表：list_four_classics - 列出四大名著信息
8. 书籍信息：get_book_info - 获取指定书籍详情

【工作流程】
1. 分析用户问题，判断需要使用哪些工具
2. 如果问题涉及四大名著内容，先使用 search_knowledge_base 搜索
3. 如果需要计算、时间等信息，使用相应的工具
4. 可以组合使用多个工具来完成复杂任务
5. 基于工具返回的结果，给出完整准确的答案
6. 注意对话历史，理解代词指代

【核心规则】
1. 对于四大名著的问题，必须先使用 search_knowledge_base 搜索
2. 只能基于工具返回的结果回答，不要编造信息
3. 如果工具返回"未找到"，明确告知用户
4. 可以使用多个工具来完成任务
5. 保持回答的准确性和完整性
6. 结合对话历史理解问题中的代词指代

【示例】
用户："红楼梦有多少回？"
思考：这是关于书籍信息的问题
行动：使用 get_book_info 工具
结果：《红楼梦》有120回

用户："计算一下 123 + 456"
思考：这是数学计算问题
行动：使用 calculator 工具
结果：579

用户："贾宝玉和林黛玉的关系"
思考：这需要查询知识库
行动：使用 search_knowledge_base 工具
结果：根据知识库内容回答..."""

        # 5. 创建 Agent (新版本 LangChain 返回的是一个编译后的图)
        return create_agent(
            model=self.llm,
            tools=tools,
            system_prompt=system_prompt
        )

    def run_simple_rag(self, query: str):
        """简化的 RAG 实现，不使用 Agent（适用于 Groq）
        包含防幻觉机制和对话历史"""
        # 重置状态
        self.last_retrieved_docs = []
        self.used_knowledge_base = False
        
        # 1. 检索相关文档
        retriever = self.rag.get_retriever()
        docs = retriever.invoke(query)
        self.last_retrieved_docs = docs
        
        # 2. 获取对话历史
        memory_vars = self.memory.load_memory_variables({})
        chat_history = memory_vars.get("chat_history", [])
        history_text = ""
        if chat_history:
            history_text = "\n【对话历史】\n"
            for msg in chat_history:
                role = "用户" if isinstance(msg, HumanMessage) else "AI"
                history_text += f"{role}: {msg.content}\n"
            history_text += "\n"
        
        # 3. 构建提示词（防幻觉优化）
        if not docs:
            # 没有检索到文档
            prompt = f"""你是一个严谨的知识问答助手。

{history_text}【重要提示】
知识库中没有找到与问题相关的内容。

【用户问题】
{query}

【回答】
抱歉，知识库中没有找到与您的问题相关的内容。请尝试换一个问题或提供更多上下文。"""
        elif len(docs) < 2:
            # 检索结果太少
            self.used_knowledge_base = True
            context = docs[0].page_content
            prompt = f"""你是一个严谨的知识问答助手。

{history_text}【重要提示】
知识库中只找到了少量相关内容，请谨慎回答。

【知识库内容】
{context}

【用户问题】
{query}

【回答要求】
- 只基于知识库内容回答
- 如果内容不足，明确说明
- 不要编造或推测
- 注意对话历史中的上下文，理解代词指代"""
        else:
            # 正常情况
            self.used_knowledge_base = True
            context = "\n\n".join([doc.page_content for doc in docs])
            prompt = f"""你是一个严谨的知识问答助手。请严格遵守以下规则：

{history_text}【核心规则】
1. 只能基于下方提供的知识库内容回答问题
2. 如果知识库内容不足以回答问题，明确说明
3. 不要编造、推测或使用知识库外的信息
4. 引用原文时要准确，不要篡改或过度解读
5. 注意对话历史，理解代词（如\"他\"、\"这本书\"）的指代关系

【知识库内容】
{context}

【用户问题】
{query}

【回答要求】
- 如果知识库中有明确答案，请详细回答
- 如果知识库中只有部分信息，说明"根据知识库内容，可以回答以下部分：..."
- 如果知识库中完全没有相关信息，直接回答"抱歉，知识库中没有关于这个问题的信息"
- 回答时可以适当引用原文片段，用引号标注
- 结合对话历史理解问题中的代词指代"""
        
        # 4. 调用 LLM
        
        # 打印发送给 LLM 的 prompt
        print("\n" + "="*80)
        print("📤 发送给 LLM 的 Prompt (Simple RAG)：")
        print("="*80)
        print(prompt)
        print("="*80 + "\n")
        
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        return response.content

    def direct_retrieval(self, query: str) -> str:
        """
        直接检索模式 - 命中关键词后，检索相关文档并通过 LLM 生成答案
        这是优化后的 RAG 流程：跳过 Agent 工具调用，直接检索 + LLM 生成
        包含防幻觉机制：相似度阈值、知识库覆盖率检查、对话历史
        """
        # 重置状态
        self.last_retrieved_docs = []
        self.used_knowledge_base = True
        self.used_direct_retrieval = True
        
        # 1. 检索相关文档
        retriever = self.rag.get_retriever()
        docs = retriever.invoke(query)
        self.last_retrieved_docs = docs
        
        # 2. 获取对话历史
        memory_vars = self.memory.load_memory_variables({})
        chat_history = memory_vars.get("chat_history", [])
        history_text = ""
        if chat_history:
            history_text = "\n【对话历史】\n"
            for msg in chat_history:
                role = "用户" if isinstance(msg, HumanMessage) else "AI"
                history_text += f"{role}: {msg.content}\n"
            history_text += "\n"
        
        # 3. 知识库覆盖率检查（防幻觉机制 1）
        if not docs:
            # 没有检索到任何文档
            return "抱歉，知识库中没有找到与您的问题相关的内容。请尝试换一个问题或提供更多上下文。"
        
        # 4. 相似度阈值检查（防幻觉机制 2）
        if len(docs) < 2:
            # 检索结果太少，可能相关性不高
            context = docs[0].page_content
            prompt = f"""你是一个严谨的知识问答助手。

{history_text}【重要提示】
知识库中只找到了少量相关内容，请谨慎回答。如果内容不足以完整回答问题，请明确说明。

【知识库内容】
{context}

【用户问题】
{query}

【回答要求】
- 如果内容足够，请基于知识库回答
- 如果内容不足，请说明"知识库中的信息有限，只能提供以下内容：..."
- 不要编造或推测知识库外的信息
- 注意对话历史中的上下文，理解代词指代"""
            
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            return response.content
        
        # 5. 构建上下文（正常情况）
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # 6. 构建增强提示词（RAG 核心 - 防止幻觉）
        prompt = f"""你是一个严谨的知识问答助手。请严格遵守以下规则：

{history_text}【核心规则】
1. 只能基于下方提供的知识库内容回答问题
2. 如果知识库内容不足以回答问题，明确说明"知识库中没有足够的信息来回答这个问题"
3. 不要编造、推测或使用知识库外的信息
4. 引用原文时要准确，不要篡改或过度解读
5. 保持客观中立，不要添加个人观点
6. 注意对话历史，理解代词（如\"他\"、\"这本书\"）的指代关系

【知识库内容】
{context}

【用户问题】
{query}

【回答要求】
- 如果知识库中有明确答案，请详细回答
- 如果知识库中只有部分信息，说明"根据知识库内容，可以回答以下部分：..."
- 如果知识库中完全没有相关信息，直接回答"抱歉，知识库中没有关于这个问题的信息"
- 回答时可以适当引用原文片段，用引号标注
- 结合对话历史理解问题中的代词指代"""
        
        # 7. 调用 LLM 生成答案
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        return response.content

    def run(self, query: str):
        # 重置调用信息
        self.last_call_info = {
            "mode": None,
            "llm_called": False,
            "tools_used": [],
            "keyword_matched": None,
        }
        
        # Groq 使用简化的 RAG，阿里云使用 Agent
        if self.provider == "groq":
            print("🤖 使用 Groq 简化 RAG 模式")
            self.last_call_info["mode"] = "simple_rag"
            self.last_call_info["llm_called"] = True
            answer = self.run_simple_rag(query)
        else:
            print("🤖 使用 Agent 推理模式")
            self.last_call_info["mode"] = "agent"
            self.last_call_info["llm_called"] = True
            
            # 重置状态
            self.last_retrieved_docs = []
            self.used_knowledge_base = False
            
            # 获取对话历史
            memory_vars = self.memory.load_memory_variables({})
            chat_history = memory_vars.get("chat_history", [])
            
            # 创建 Agent（传入对话历史）
            graph = self.create_agent(chat_history=chat_history)
            
            # 调用图，输入消息列表
            
            inputs = {"messages": [{"role": "user", "content": query}]}
            
            # 打印发送给 LLM 的 prompt
            print("\n" + "="*80)
            print("📤 发送给 LLM 的消息：")
            print("="*80)
            for msg in inputs["messages"]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                print(f"\n[{role.upper()}]")
                print(content)
            if chat_history:
                print(f"\n[对话历史] {len(chat_history)} 条消息")
                for msg in chat_history[-4:]:
                    role = "用户" if msg.__class__.__name__ == "HumanMessage" else "AI"
                    content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                    print(f"  - {role}: {content_preview}")
            print("="*80 + "\n")
            
            result = graph.invoke(inputs)
            # 获取最后一条 AI 消息的内容
            messages = result.get("messages", [])
            if messages:
                answer = messages[-1].content
            else:
                answer = "未能生成回复。"
        
        # 保存到记忆
        self.memory.save_context(
            {"input": query},
            {"output": answer}
        )
        
        # 获取当前记忆中的消息数量
        memory_vars = self.memory.load_memory_variables({})
        msg_count = len(memory_vars.get("chat_history", []))
        print(f"💾 已保存到记忆，当前共 {msg_count} 条消息")
        
        return answer

    def get_chat_history(self):
        """获取对话历史"""
        memory_vars = self.memory.load_memory_variables({})
        return memory_vars.get("chat_history", [])
    
    def clear_memory(self):
        """清空对话记忆"""
        self.memory.clear()
        print("🗑️ 对话记忆已清空")
    
    def get_last_retrieval_info(self):
        """获取最后一次检索的详细信息"""
        return {
            "used_knowledge_base": self.used_knowledge_base,
            "used_direct_retrieval": self.used_direct_retrieval,
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

    def get_last_call_info(self):
        """获取最后一次调用的详细信息"""
        return self.last_call_info

    def get_last_call_info(self):
        """获取最后一次调用的详细信息"""
        return self.last_call_info
