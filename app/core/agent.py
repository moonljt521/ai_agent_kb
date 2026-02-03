import os
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
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

        # 4. 创建 ReAct 提示词模板
        history_text = ""
        if chat_history:
            history_text = "【对话历史】\n"
            for msg in chat_history:
                role = "用户" if isinstance(msg, HumanMessage) else "AI"
                history_text += f"{role}: {msg.content}\n"
            history_text += "\n注意：理解对话历史中的上下文，特别是代词（如\"他\"、\"这本书\"）的指代关系。\n\n"

        # 使用 ReAct 提示词模板
        react_prompt = PromptTemplate.from_template("""你是一个功能强大的 AI Agent，专门回答关于中国四大名著的问题。

{history_text}你可以使用以下工具：

{tools}

使用以下格式进行推理：

Question: 用户的问题
Thought: 你应该思考要做什么
Action: 要使用的工具，应该是 [{tool_names}] 中的一个
Action Input: 工具的输入
Observation: 工具返回的结果
... (这个 Thought/Action/Action Input/Observation 可以重复 N 次)
Thought: 我现在知道最终答案了
Final Answer: 对用户问题的最终答案

【重要规则】
1. 对于四大名著的问题，必须使用 search_knowledge_base 工具
2. 只能基于工具返回的结果回答，不要编造信息
3. 如果工具返回"未找到"，明确告知用户
4. 结合对话历史理解问题中的代词指代

开始！

Question: {input}
Thought: {agent_scratchpad}""")

        # 5. 创建 ReAct Agent
        agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=react_prompt.partial(history_text=history_text)
        )
        
        # 6. 创建 AgentExecutor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,  # 显示推理过程
            max_iterations=5,  # 最多5步推理
            handle_parsing_errors=True,  # 处理解析错误
            return_intermediate_steps=True,  # 返回中间步骤
        )
        
        print("🎯 ReAct Agent 已创建，verbose=True")
        
        return agent_executor

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
            self.used_direct_retrieval = False
            
            # 获取对话历史
            memory_vars = self.memory.load_memory_variables({})
            chat_history = memory_vars.get("chat_history", [])
            
            # 创建 ReAct Agent（传入对话历史）
            agent_executor = self.create_agent(chat_history=chat_history)
            
            # 调用 Agent（ReAct 模式）
            print(f"🚀 开始 ReAct 推理：{query}")
            print("="*60)
            
            # 调用 Agent
            result = agent_executor.invoke({"input": query})
            
            print("="*60)
            print("✅ ReAct 推理完成")
            
            answer = result.get("output", "未能生成回复。")
            
            
            # 从 intermediate_steps 中提取图片路径并添加到答案
            print(f"\n🔍 DEBUG: 检查 intermediate_steps")
            if "intermediate_steps" in result:
                print(f"   找到 {len(result['intermediate_steps'])} 个步骤")
                for i, (action, observation) in enumerate(result['intermediate_steps']):
                    print(f"   步骤 {i+1}: {action.tool}")
                    if isinstance(observation, str) and "[IMAGE_PATH:" in observation:
                        import re
                        image_match = re.search(r'\[IMAGE_PATH:(.*?)\]', observation)
                        if image_match:
                            image_path = image_match.group(1).strip()
                            answer = answer + f"\n\n[IMAGE_PATH:{image_path}]"
                            print(f"   ✅ 已添加 IMAGE_PATH: {image_path}")
                            break
            
            # 记录使用的工具
            if "intermediate_steps" in result:
                print(f"\n📊 推理步骤数：{len(result['intermediate_steps'])}")
                for i, (action, observation) in enumerate(result['intermediate_steps'], 1):
                    tool_name = action.tool
                    self.last_call_info["tools_used"].append(tool_name)
                    print(f"\n  步骤 {i}:")
                    print(f"    🔧 工具: {tool_name}")
                    print(f"    📥 输入: {action.tool_input}")
                    obs_preview = str(observation)[:200] + "..." if len(str(observation)) > 200 else str(observation)
                    print(f"    📤 结果: {obs_preview}")

        
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
