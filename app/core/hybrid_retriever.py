"""
混合检索器 - 支持本地向量库 + 外部 API
"""
import os
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
import requests


class HybridRetriever:
    """混合检索器：本地向量库 + 外部 API"""
    
    def __init__(self, local_rag_manager, similarity_threshold=0.7):
        """
        初始化混合检索器
        
        Args:
            local_rag_manager: 本地 RAG 管理器
            similarity_threshold: 相似度阈值，低于此值时调用外部 API
        """
        self.local_rag = local_rag_manager
        self.similarity_threshold = similarity_threshold
        
        # 外部 API 配置（从环境变量读取）
        self.external_api_enabled = os.getenv("EXTERNAL_API_ENABLED", "false").lower() == "true"
        self.external_api_url = os.getenv("EXTERNAL_API_URL", "")
        self.external_api_key = os.getenv("EXTERNAL_API_KEY", "")
        
        print(f"🔗 混合检索器初始化")
        print(f"   本地向量库：✅")
        print(f"   外部 API：{'✅ 已启用' if self.external_api_enabled else '❌ 未启用'}")
        if self.external_api_enabled:
            print(f"   相似度阈值：{similarity_threshold}")
    
    def retrieve(self, query: str, k: int = 5, book_filter: Optional[str] = None) -> List[Document]:
        """
        混合检索
        
        Args:
            query: 查询问题
            k: 返回文档数量
            book_filter: 书籍过滤（仅本地）
            
        Returns:
            文档列表
        """
        # 1. 先查本地向量库
        print(f"📚 检索本地向量库...")
        local_docs = self._retrieve_local(query, k, book_filter)
        
        # 2. 评估本地结果质量
        if local_docs:
            max_similarity = self._get_max_similarity(local_docs)
            print(f"   最高相似度：{max_similarity:.2f}")
            
            # 如果本地结果足够好，直接返回
            if max_similarity >= self.similarity_threshold:
                print(f"   ✅ 本地结果质量良好，使用本地数据")
                return local_docs
        
        # 3. 本地结果不够好，尝试外部 API
        if self.external_api_enabled:
            print(f"   ⚠️  本地结果不足（相似度 < {self.similarity_threshold}），查询外部 API...")
            external_docs = self._retrieve_external(query, k)
            
            if external_docs:
                print(f"   ✅ 外部 API 返回 {len(external_docs)} 个结果")
                # 合并本地和外部结果
                return self._merge_results(local_docs, external_docs, k)
            else:
                print(f"   ⚠️  外部 API 无结果，使用本地数据")
        else:
            print(f"   ℹ️  外部 API 未启用，仅使用本地数据")
        
        return local_docs
    
    def _retrieve_local(self, query: str, k: int, book_filter: Optional[str] = None) -> List[Document]:
        """从本地向量库检索"""
        try:
            if book_filter:
                return self.local_rag.search_by_book(query, book_filter, k=k)
            else:
                retriever = self.local_rag.get_retriever(k=k)
                return retriever.invoke(query)
        except Exception as e:
            print(f"   ❌ 本地检索失败：{e}")
            return []
    
    def _retrieve_external(self, query: str, k: int) -> List[Document]:
        """从外部 API 检索"""
        try:
            # 调用外部 API
            response = requests.post(
                self.external_api_url,
                json={
                    "query": query,
                    "k": k
                },
                headers={
                    "Authorization": f"Bearer {self.external_api_key}",
                    "Content-Type": "application/json"
                },
                timeout=5  # 5秒超时
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 将 API 返回的数据转换为 Document 对象
                docs = []
                for item in data.get("results", []):
                    doc = Document(
                        page_content=item.get("content", ""),
                        metadata={
                            "source": "外部API",
                            "type": "external",
                            "api_source": item.get("source", "unknown"),
                            "score": item.get("score", 0.0)
                        }
                    )
                    docs.append(doc)
                
                return docs
            else:
                print(f"   ❌ API 返回错误：{response.status_code}")
                return []
                
        except requests.Timeout:
            print(f"   ❌ API 请求超时")
            return []
        except Exception as e:
            print(f"   ❌ API 调用失败：{e}")
            return []
    
    def _get_max_similarity(self, docs: List[Document]) -> float:
        """获取文档列表中的最高相似度"""
        if not docs:
            return 0.0
        
        # 尝试从元数据中获取相似度分数
        scores = []
        for doc in docs:
            score = doc.metadata.get("score", 0.0)
            if score > 0:
                scores.append(score)
        
        if scores:
            return max(scores)
        
        # 如果没有分数，假设第一个文档相似度最高
        # ChromaDB 默认按相似度排序
        return 0.8  # 默认假设较高相似度
    
    def _merge_results(self, local_docs: List[Document], external_docs: List[Document], k: int) -> List[Document]:
        """合并本地和外部结果"""
        # 简单策略：本地结果优先，然后是外部结果
        merged = local_docs + external_docs
        
        # 去重（基于内容）
        seen_content = set()
        unique_docs = []
        for doc in merged:
            content_hash = hash(doc.page_content[:100])  # 用前100字符去重
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_docs.append(doc)
        
        # 限制返回数量
        return unique_docs[:k]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "本地向量库": "已启用",
            "外部API": "已启用" if self.external_api_enabled else "未启用",
            "相似度阈值": self.similarity_threshold,
            "API地址": self.external_api_url if self.external_api_enabled else "未配置"
        }


class ExternalAPIAdapter:
    """外部 API 适配器 - 用于不同 API 格式的转换"""
    
    @staticmethod
    def adapt_custom_api(response_data: Dict) -> List[Dict]:
        """
        适配自定义 API 格式
        
        示例输入：
        {
            "data": [
                {"text": "内容1", "source": "来源1", "relevance": 0.9},
                {"text": "内容2", "source": "来源2", "relevance": 0.8}
            ]
        }
        
        输出：
        [
            {"content": "内容1", "source": "来源1", "score": 0.9},
            {"content": "内容2", "source": "来源2", "score": 0.8}
        ]
        """
        results = []
        for item in response_data.get("data", []):
            results.append({
                "content": item.get("text", ""),
                "source": item.get("source", "unknown"),
                "score": item.get("relevance", 0.0)
            })
        return results
    
    @staticmethod
    def adapt_elasticsearch(response_data: Dict) -> List[Dict]:
        """适配 Elasticsearch 格式"""
        results = []
        hits = response_data.get("hits", {}).get("hits", [])
        for hit in hits:
            results.append({
                "content": hit.get("_source", {}).get("content", ""),
                "source": hit.get("_source", {}).get("source", "unknown"),
                "score": hit.get("_score", 0.0)
            })
        return results
    
    @staticmethod
    def adapt_meilisearch(response_data: Dict) -> List[Dict]:
        """适配 Meilisearch 格式"""
        results = []
        for hit in response_data.get("hits", []):
            results.append({
                "content": hit.get("content", ""),
                "source": hit.get("source", "unknown"),
                "score": hit.get("_rankingScore", 0.0)
            })
        return results
