#!/usr/bin/env python3
"""测试 Ollama 配置"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

def test_ollama_connection():
    """测试 Ollama 连接"""
    print("========================================")
    print("🧪 测试 Ollama 配置")
    print("========================================\n")
    
    # 读取配置
    provider = os.getenv("MODEL_PROVIDER", "aliyun")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model = os.getenv("OLLAMA_LLM_MODEL", "qwen3:8b")
    
    print(f"提供商: {provider}")
    print(f"Ollama 地址: {ollama_url}")
    print(f"Ollama 模型: {ollama_model}\n")
    
    if provider != "ollama":
        print(f"⚠️  当前提供商是 {provider}，不是 ollama")
        print("请运行: ./switch_provider.sh 切换到 Ollama\n")
        return False
    
    try:
        # 初始化 LLM
        print("🔗 连接 Ollama...")
        llm = ChatOpenAI(
            model=ollama_model,
            openai_api_base=f"{ollama_url}/v1",
            openai_api_key="ollama"
        )
        
        # 测试简单对话
        print("💬 发送测试消息...\n")
        test_query = "你好，请用一句话介绍你自己。"
        print(f"问题: {test_query}")
        print("回答: ", end="", flush=True)
        
        messages = [HumanMessage(content=test_query)]
        response = llm.invoke(messages)
        
        print(response.content)
        print("\n✅ Ollama 配置测试成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        print("\n请检查:")
        print("1. Ollama 是否正在运行: curl http://127.0.0.1:11434/")
        print("2. 模型是否已下载: ollama list")
        print("3. 模型名称是否正确: qwen3:8b")
        return False

if __name__ == "__main__":
    test_ollama_connection()
