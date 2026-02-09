#!/usr/bin/env python3
"""
API 接口测试脚本
用于快速测试四大名著知识问答系统的所有接口
"""

import requests
import json
import time

BASE_URL = "http://localhost:8888"

def print_section(title):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_config():
    """测试获取配置信息"""
    print_section("1. 测试获取配置信息")
    
    response = requests.get(f"{BASE_URL}/config")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ LLM 模型: {data['llm_model']}")
        print(f"✅ Embedding 模型: {data['embedding_model']}")
        print(f"✅ 模型提供商: {data['model_provider']}")
        print(f"✅ 直接检索: {data['enable_direct_retrieval']}")
    else:
        print(f"❌ 错误: {response.text}")

def test_books():
    """测试获取书籍列表"""
    print_section("2. 测试获取书籍列表")
    
    response = requests.get(f"{BASE_URL}/books")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 可用书籍: {', '.join(data['books'])}")
        print(f"\n📊 统计信息:")
        for book, stats in data['statistics'].items():
            print(f"  - {book}: {stats.get('文档数', 0)} 个文档")
        
        if 'summary' in data:
            summary = data['summary']
            print(f"\n📌 标签概览:")
            print(f"  - 书籍数量: {summary.get('书籍数量', 0)}")
            print(f"  - 文件映射数: {summary.get('文件映射数', 0)}")
    else:
        print(f"❌ 错误: {response.text}")

def test_chat_simple():
    """测试简单聊天（无历史）"""
    print_section("3. 测试简单聊天（无历史）")
    
    payload = {
        "query": "贾宝玉是谁？",
        "book": "红楼梦",
        "history": []
    }
    
    print(f"📤 发送请求:")
    print(f"  问题: {payload['query']}")
    print(f"  书籍: {payload['book']}")
    print(f"\n📥 接收响应:\n")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload,
        stream=True
    )
    
    if response.status_code == 200:
        answer = ""
        metadata = None
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    json_str = line[6:]
                    try:
                        data = json.loads(json_str)
                        
                        if data['type'] == 'text':
                            answer += data['content']
                            print(data['content'], end='', flush=True)
                        elif data['type'] == 'metadata':
                            metadata = data
                        elif data['type'] == 'done':
                            print("\n")
                            break
                        elif data['type'] == 'error':
                            print(f"\n❌ 错误: {data['error']}")
                            break
                    except json.JSONDecodeError:
                        pass
        
        if metadata:
            print(f"\n📊 元数据:")
            print(f"  - 使用知识库: {'✅' if metadata['knowledge_base_used'] else '❌'}")
            print(f"  - 命中关键词: {'✅' if metadata['keyword_matched'] else '❌'}")
            print(f"  - 检索文档数: {metadata['retrieved_docs_count']}")
            print(f"  - 引用来源数: {len(metadata['sources'])}")
    else:
        print(f"❌ 错误: {response.text}")

def test_chat_with_context():
    """测试多轮对话"""
    print_section("4. 测试多轮对话（带历史）")
    
    # 第一轮对话
    payload1 = {
        "query": "林黛玉是谁？",
        "book": "红楼梦",
        "history": []
    }
    
    print(f"📤 第一轮提问: {payload1['query']}\n")
    
    response1 = requests.post(
        f"{BASE_URL}/chat",
        json=payload1,
        stream=True
    )
    
    answer1 = ""
    for line in response1.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                json_str = line[6:]
                try:
                    data = json.loads(json_str)
                    if data['type'] == 'text':
                        answer1 += data['content']
                        print(data['content'], end='', flush=True)
                    elif data['type'] == 'done':
                        print("\n")
                        break
                except json.JSONDecodeError:
                    pass
    
    # 第二轮对话（续问）
    time.sleep(1)
    
    payload2 = {
        "query": "她和贾宝玉是什么关系？",
        "book": "红楼梦",
        "history": [
            {
                "role": "user",
                "content": payload1['query'],
                "timestamp": int(time.time() * 1000)
            },
            {
                "role": "assistant",
                "content": answer1,
                "timestamp": int(time.time() * 1000)
            }
        ]
    }
    
    print(f"\n📤 第二轮提问（续问）: {payload2['query']}")
    print(f"   💡 系统应该理解'她'指林黛玉\n")
    
    response2 = requests.post(
        f"{BASE_URL}/chat",
        json=payload2,
        stream=True
    )
    
    for line in response2.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                json_str = line[6:]
                try:
                    data = json.loads(json_str)
                    if data['type'] == 'text':
                        print(data['content'], end='', flush=True)
                    elif data['type'] == 'metadata':
                        if data['has_context']:
                            print("\n\n✅ 成功使用对话历史！")
                    elif data['type'] == 'done':
                        print("\n")
                        break
                except json.JSONDecodeError:
                    pass

def test_chat_all_books():
    """测试搜索全部书籍"""
    print_section("5. 测试搜索全部书籍")
    
    payload = {
        "query": "孙悟空的师傅是谁？",
        "book": None,
        "history": []
    }
    
    print(f"📤 发送请求:")
    print(f"  问题: {payload['query']}")
    print(f"  书籍: 全部")
    print(f"\n📥 接收响应:\n")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload,
        stream=True
    )
    
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    json_str = line[6:]
                    try:
                        data = json.loads(json_str)
                        if data['type'] == 'text':
                            print(data['content'], end='', flush=True)
                        elif data['type'] == 'done':
                            print("\n")
                            break
                    except json.JSONDecodeError:
                        pass
    else:
        print(f"❌ 错误: {response.text}")

def main():
    """主函数"""
    print("\n" + "🚀 开始测试 API 接口".center(60, "="))
    print(f"Base URL: {BASE_URL}\n")
    
    try:
        # 测试各个接口
        test_config()
        test_books()
        test_chat_simple()
        test_chat_with_context()
        test_chat_all_books()
        
        print_section("✅ 所有测试完成")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ 错误: 无法连接到服务器 {BASE_URL}")
        print("   请确保服务已启动（运行 ./start_web.sh）")
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    main()
