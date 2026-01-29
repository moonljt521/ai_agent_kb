"""
聊天脚本 - 支持交互式和单次提问两种模式
支持 --no-rag 参数，不使用知识库（完全免费）
"""
import sys
import os
sys.path.append(os.getcwd())

from app.core.agent import AgentManager
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

# 检查是否使用 --no-rag 模式
USE_RAG = "--no-rag" not in sys.argv
if not USE_RAG:
    sys.argv.remove("--no-rag")

def get_llm():
    """获取纯 LLM 实例（不使用 RAG）"""
    provider = os.getenv("MODEL_PROVIDER", "aliyun").lower()
    
    if provider == "groq":
        llm = ChatOpenAI(
            model=os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile"),
            openai_api_base="https://api.groq.com/openai/v1",
            openai_api_key=os.getenv("GROQ_API_KEY")
        )
        print(f"✅ 使用 Groq 模型: {os.getenv('GROQ_LLM_MODEL', 'llama-3.3-70b-versatile')}")
        print("💰 完全免费模式（不使用知识库）")
    else:
        llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "qwen-plus"),
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            openai_api_key=os.getenv("DASHSCOPE_API_KEY")
        )
        print(f"✅ 使用阿里云模型: {os.getenv('LLM_MODEL', 'qwen-plus')}")
        print("💰 按 Token 计费（不使用知识库）")
    
    return llm

def print_separator():
    print("\n" + "=" * 70 + "\n")

def print_source_info(retrieval_info):
    """打印数据来源信息"""
    if retrieval_info['used_knowledge_base']:
        print(f"📊 数据来源：✅ 本地知识库")
        print(f"📄 检索到的文档数量：{retrieval_info['retrieved_docs_count']}")
        
        if retrieval_info['sources']:
            print(f"\n📚 引用的文档：")
            for i, source in enumerate(retrieval_info['sources'], 1):
                print(f"  [{i}] {source['source']} (页码: {source['page']})")
    else:
        print(f"📊 数据来源：❌ 模型通用知识")

def single_question_mode(query):
    """单次提问模式"""
    print("=" * 70)
    print(f"🤖 AI Agent 知识库问答系统 {'（纯 LLM 模式）' if not USE_RAG else ''}")
    print("=" * 70)
    print(f"\n💬 问题：{query}\n")
    print("⏳ 正在思考...\n")
    
    try:
        if USE_RAG:
            agent = AgentManager()
            answer = agent.run(query)
            retrieval_info = agent.get_last_retrieval_info()
            
            print("🤖 回答：")
            print("-" * 70)
            print(answer)
            print("-" * 70)
            print()
            print_source_info(retrieval_info)
        else:
            llm = get_llm()
            messages = [HumanMessage(content=query)]
            response = llm.invoke(messages)
            
            print("🤖 回答：")
            print("-" * 70)
            print(response.content)
            print("-" * 70)
            print("\n📊 数据来源：❌ 纯 LLM（未使用知识库）")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)

def interactive_mode():
    """交互式聊天模式"""
    print("=" * 70)
    print(f"🤖 AI Agent 知识库问答系统 {'（纯 LLM 模式）' if not USE_RAG else ''}")
    print("=" * 70)
    print("\n💡 提示：")
    print("  - 直接输入问题，按回车获得答案")
    print("  - 输入 'exit' 或 'quit' 退出")
    print("  - 输入 'clear' 清屏")
    if not USE_RAG:
        print("  - 💰 不使用知识库，完全免费（Groq）")
    print_separator()
    
    if USE_RAG:
        print("⏳ 正在初始化...")
        try:
            agent = AgentManager()
            print("✅ 初始化成功！\n")
        except Exception as e:
            print(f"❌ 初始化失败：{e}")
            print("\n💡 请确保已运行 'python scripts/ingest.py' 导入文档")
            return
        
        conversation_history = None
    else:
        llm = get_llm()
        print()
        conversation_history = []
    
    while True:
        try:
            query = input("💬 你的问题：").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 再见！")
                break
            
            if query.lower() == 'clear':
                os.system('clear' if os.name != 'nt' else 'cls')
                if not USE_RAG:
                    conversation_history = []
                    print("🗑️  对话历史已清空")
                continue
            
            print("\n⏳ 正在思考...\n")
            
            try:
                if USE_RAG:
                    answer = agent.run(query)
                    retrieval_info = agent.get_last_retrieval_info()
                    
                    print("🤖 回答：")
                    print("-" * 70)
                    print(answer)
                    print("-" * 70)
                    print()
                    print_source_info(retrieval_info)
                else:
                    # 纯 LLM 模式（带对话历史）
                    messages = conversation_history + [HumanMessage(content=query)]
                    response = llm.invoke(messages)
                    
                    # 保存到历史
                    conversation_history.append(HumanMessage(content=query))
                    conversation_history.append(response)
                    
                    # 限制历史长度
                    if len(conversation_history) > 20:
                        conversation_history = conversation_history[-20:]
                    
                    print("🤖 回答：")
                    print("-" * 70)
                    print(response.content)
                    print("-" * 70)
                    print("\n📊 数据来源：❌ 纯 LLM（未使用知识库）")
                
            except Exception as e:
                print(f"❌ 处理问题时出错：{e}")
            
            print_separator()
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except EOFError:
            print("\n\n👋 再见！")
            break

def main():
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 单次提问模式
        query = " ".join(sys.argv[1:])
        single_question_mode(query)
    else:
        # 交互式模式
        interactive_mode()

if __name__ == "__main__":
    main()
