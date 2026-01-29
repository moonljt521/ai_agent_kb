"""
纯 LLM 对话脚本 - 不使用知识库，完全免费
适合：
- 调试 LLM
- 通用对话
- 不需要知识库的场景
"""
import sys
import os
sys.path.append(os.getcwd())

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """获取 LLM 实例"""
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

def single_question_mode(llm, query):
    """单次提问模式"""
    print("=" * 70)
    print("🤖 纯 LLM 对话（无知识库）")
    print("=" * 70)
    print(f"\n💬 问题：{query}\n")
    print("⏳ 正在思考...\n")
    
    try:
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

def interactive_mode(llm):
    """交互式对话模式"""
    print("=" * 70)
    print("🤖 纯 LLM 对话（无知识库）")
    print("=" * 70)
    print("\n💡 提示：")
    print("  - 直接输入问题，按回车获得答案")
    print("  - 输入 'exit' 或 'quit' 退出")
    print("  - 输入 'clear' 清屏")
    print("  - 不使用知识库，完全免费（Groq）")
    print_separator()
    
    # 对话历史
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
                conversation_history = []
                print("🗑️  对话历史已清空")
                continue
            
            if query.lower() == 'history':
                print("\n📜 对话历史：")
                for i, msg in enumerate(conversation_history, 1):
                    role = "👤" if msg.type == "human" else "🤖"
                    print(f"{role} {i}: {msg.content[:100]}...")
                continue
            
            print("\n⏳ 正在思考...\n")
            
            try:
                # 构建消息（包含历史）
                messages = conversation_history + [HumanMessage(content=query)]
                response = llm.invoke(messages)
                
                # 保存到历史
                conversation_history.append(HumanMessage(content=query))
                conversation_history.append(response)
                
                # 限制历史长度（最多保留 10 轮对话）
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
    llm = get_llm()
    print()
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 单次提问模式
        query = " ".join(sys.argv[1:])
        single_question_mode(llm, query)
    else:
        # 交互式模式
        interactive_mode(llm)

if __name__ == "__main__":
    main()
