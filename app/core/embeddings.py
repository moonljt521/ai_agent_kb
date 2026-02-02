"""
Embedding 模型管理模块
支持多种 Embedding 提供商：阿里云、BGE、M3E、Text2Vec、OpenAI
"""

import os
from dotenv import load_dotenv

load_dotenv()

def get_embeddings():
    """
    根据环境变量返回相应的 Embedding 模型
    
    支持的提供商：
    - aliyun: 阿里云 DashScope (付费，性能最强)
    - bge: BGE 系列本地模型 (免费，推荐)
    - m3e: M3E 本地模型 (免费)
    - text2vec: Text2Vec 本地模型 (免费)
    - openai: OpenAI (付费)
    
    环境变量配置：
    EMBEDDING_PROVIDER=bge  # 提供商选择
    BGE_MODEL=BAAI/bge-large-zh-v1.5  # BGE 模型选择
    DEVICE=cpu  # 设备选择 (cpu 或 cuda)
    """
    provider = os.getenv("EMBEDDING_PROVIDER", "bge").lower()
    
    print(f"\n{'='*60}")
    print(f"🔧 初始化 Embedding 模型")
    print(f"{'='*60}")
    print(f"📦 提供商: {provider}")
    
    if provider == "aliyun":
        from langchain_community.embeddings import DashScopeEmbeddings
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
        print(f"✅ 使用阿里云模型: {model}")
        print(f"📊 维度: 1536")
        print(f"💰 费用: ¥0.0007/千tokens")
        print(f"🌐 需要网络连接")
        print(f"{'='*60}\n")
        return DashScopeEmbeddings(model=model)
    
    elif provider == "bge":
        from langchain_community.embeddings import HuggingFaceEmbeddings
        model_name = os.getenv("BGE_MODEL", "BAAI/bge-large-zh-v1.5")
        device = os.getenv("DEVICE", "cpu")
        
        # 根据模型名称确定维度
        if "large" in model_name:
            dimension = 1024
            size = "1.3GB"
        elif "base" in model_name:
            dimension = 768
            size = "400MB"
        elif "small" in model_name:
            dimension = 512
            size = "100MB"
        else:
            dimension = "未知"
            size = "未知"
        
        print(f"✅ 使用 BGE 模型: {model_name}")
        print(f"📊 维度: {dimension}")
        print(f"💾 大小: {size}")
        print(f"🖥️  设备: {device.upper()}")
        print(f"💰 费用: 完全免费")
        print(f"📡 本地运行，无需网络")
        print(f"⏳ 首次使用会自动下载模型到 ~/.cache/huggingface/")
        print(f"{'='*60}\n")
        
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': device},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    elif provider == "m3e":
        from langchain_community.embeddings import HuggingFaceEmbeddings
        device = os.getenv("DEVICE", "cpu")
        
        print(f"✅ 使用 M3E 模型: moka-ai/m3e-base")
        print(f"📊 维度: 768")
        print(f"💾 大小: 400MB")
        print(f"🖥️  设备: {device.upper()}")
        print(f"💰 费用: 完全免费")
        print(f"📡 本地运行，无需网络")
        print(f"{'='*60}\n")
        
        return HuggingFaceEmbeddings(
            model_name="moka-ai/m3e-base",
            model_kwargs={'device': device},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    elif provider == "text2vec":
        from langchain_community.embeddings import HuggingFaceEmbeddings
        device = os.getenv("DEVICE", "cpu")
        
        print(f"✅ 使用 Text2Vec 模型: shibing624/text2vec-base-chinese")
        print(f"📊 维度: 768")
        print(f"💾 大小: 400MB")
        print(f"🖥️  设备: {device.upper()}")
        print(f"💰 费用: 完全免费")
        print(f"📡 本地运行，无需网络")
        print(f"{'='*60}\n")
        
        return HuggingFaceEmbeddings(
            model_name="shibing624/text2vec-base-chinese",
            model_kwargs={'device': device},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    elif provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        
        print(f"✅ 使用 OpenAI 模型: {model}")
        print(f"📊 维度: 1536 (small) 或 3072 (large)")
        print(f"💰 费用: $0.00002/千tokens (small)")
        print(f"🌐 需要网络连接")
        print(f"{'='*60}\n")
        
        return OpenAIEmbeddings(model=model)
    
    else:
        raise ValueError(
            f"\n❌ 未知的 Embedding 提供商: {provider}\n"
            f"支持的提供商: aliyun, bge, m3e, text2vec, openai\n"
            f"请在 .env 文件中设置 EMBEDDING_PROVIDER"
        )

def get_embedding_info():
    """获取当前 Embedding 模型的详细信息"""
    provider = os.getenv("EMBEDDING_PROVIDER", "bge").lower()
    
    info = {
        "provider": provider,
        "is_local": provider in ["bge", "m3e", "text2vec"],
        "is_free": provider in ["bge", "m3e", "text2vec"],
    }
    
    if provider == "aliyun":
        info["model"] = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
        info["dimension"] = 1536
        info["cost_per_1k_tokens"] = 0.0007
        info["requires_network"] = True
    
    elif provider == "bge":
        model_name = os.getenv("BGE_MODEL", "BAAI/bge-large-zh-v1.5")
        info["model"] = model_name
        info["requires_network"] = False
        
        if "large" in model_name:
            info["dimension"] = 1024
            info["size"] = "1.3GB"
            info["performance"] = "最强"
        elif "base" in model_name:
            info["dimension"] = 768
            info["size"] = "400MB"
            info["performance"] = "优秀"
        elif "small" in model_name:
            info["dimension"] = 512
            info["size"] = "100MB"
            info["performance"] = "良好"
    
    elif provider == "m3e":
        info["model"] = "moka-ai/m3e-base"
        info["dimension"] = 768
        info["size"] = "400MB"
        info["requires_network"] = False
    
    elif provider == "text2vec":
        info["model"] = "shibing624/text2vec-base-chinese"
        info["dimension"] = 768
        info["size"] = "400MB"
        info["requires_network"] = False
    
    elif provider == "openai":
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        info["model"] = model
        info["dimension"] = 1536 if "small" in model else 3072
        info["cost_per_1k_tokens"] = 0.00002
        info["requires_network"] = True
    
    return info

def print_embedding_comparison():
    """打印 Embedding 模型对比表"""
    print("\n" + "="*80)
    print("📊 Embedding 模型对比")
    print("="*80)
    print(f"{'模型':<30} {'维度':<8} {'大小':<10} {'费用':<15} {'性能':<10}")
    print("-"*80)
    print(f"{'阿里云 text-embedding-v3':<30} {'1536':<8} {'API':<10} {'¥0.0007/千tokens':<15} {'⭐⭐⭐⭐⭐':<10}")
    print(f"{'BGE-large-zh-v1.5':<30} {'1024':<8} {'1.3GB':<10} {'免费':<15} {'⭐⭐⭐⭐⭐':<10}")
    print(f"{'BGE-base-zh-v1.5':<30} {'768':<8} {'400MB':<10} {'免费':<15} {'⭐⭐⭐⭐':<10}")
    print(f"{'BGE-small-zh-v1.5':<30} {'512':<8} {'100MB':<10} {'免费':<15} {'⭐⭐⭐':<10}")
    print(f"{'M3E-base':<30} {'768':<8} {'400MB':<10} {'免费':<15} {'⭐⭐⭐⭐':<10}")
    print(f"{'Text2Vec-base':<30} {'768':<8} {'400MB':<10} {'免费':<15} {'⭐⭐⭐':<10}")
    print("="*80)
    print("\n💡 推荐：BGE-large-zh-v1.5 (免费 + 高性能)")
    print("💡 轻量：BGE-small-zh-v1.5 (快速 + 低内存)")
    print("💡 最强：阿里云 text-embedding-v3 (付费 + 最佳性能)\n")

# 测试代码
if __name__ == "__main__":
    print_embedding_comparison()
    
    print("\n测试当前配置：")
    embeddings = get_embeddings()
    
    print("\n测试向量化：")
    text = "贾宝玉是红楼梦的主角"
    vector = embeddings.embed_query(text)
    print(f"文本: {text}")
    print(f"向量维度: {len(vector)}")
    print(f"向量前5个值: {vector[:5]}")
    
    info = get_embedding_info()
    print(f"\n模型信息: {info}")
