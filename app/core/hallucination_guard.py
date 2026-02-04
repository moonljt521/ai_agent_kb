"""
反幻觉守卫 - 降低 LLM 幻觉的策略
"""
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document


class HallucinationGuard:
    """反幻觉守卫"""
    
    def __init__(self, min_similarity=0.5, min_docs=2):
        """
        初始化反幻觉守卫
        
        Args:
            min_similarity: 最低相似度阈值
            min_docs: 最少文档数量
        """
        self.min_similarity = min_similarity
        self.min_docs = min_docs
        
        print(f"🛡️  反幻觉守卫已启用")
        print(f"   最低相似度：{min_similarity}")
        print(f"   最少文档数：{min_docs}")
    
    def check_retrieval_quality(self, docs: List[Document], query: str) -> Dict[str, Any]:
        """
        检查检索质量
        
        Returns:
            {
                "quality": "good" | "medium" | "poor",
                "confidence": 0.0-1.0,
                "warning": str,
                "should_answer": bool
            }
        """
        # 1. 检查文档数量
        if not docs or len(docs) == 0:
            return {
                "quality": "poor",
                "confidence": 0.0,
                "warning": "未找到相关内容",
                "should_answer": False
            }
        
        if len(docs) < self.min_docs:
            return {
                "quality": "poor",
                "confidence": 0.3,
                "warning": f"相关内容较少（仅 {len(docs)} 个片段）",
                "should_answer": False
            }
        
        # 2. 检查相似度（如果有）
        max_similarity = self._get_max_similarity(docs)
        
        if max_similarity < self.min_similarity:
            return {
                "quality": "poor",
                "confidence": max_similarity,
                "warning": f"相关度较低（{max_similarity:.2f}）",
                "should_answer": False
            }
        
        # 3. 检查内容长度
        total_length = sum(len(doc.page_content) for doc in docs)
        if total_length < 100:
            return {
                "quality": "poor",
                "confidence": 0.4,
                "warning": "相关内容过少",
                "should_answer": False
            }
        
        # 4. 评估整体质量
        if max_similarity >= 0.8 and len(docs) >= 3:
            return {
                "quality": "good",
                "confidence": max_similarity,
                "warning": None,
                "should_answer": True
            }
        elif max_similarity >= 0.6 and len(docs) >= 2:
            return {
                "quality": "medium",
                "confidence": max_similarity,
                "warning": "相关内容有限，答案可能不完整",
                "should_answer": True
            }
        else:
            return {
                "quality": "poor",
                "confidence": max_similarity,
                "warning": "相关内容不足",
                "should_answer": False
            }
    
    def build_anti_hallucination_prompt(
        self, 
        query: str, 
        docs: List[Document],
        quality_check: Dict[str, Any]
    ) -> str:
        """
        构建反幻觉提示词
        
        策略：
        1. 明确告知 LLM 只能基于提供的内容回答
        2. 要求 LLM 承认不知道
        3. 禁止编造信息
        4. 要求引用来源
        """
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # 根据质量调整提示词
        if not quality_check["should_answer"]:
            # 质量差：明确告知无法回答
            prompt = f"""你是一个诚实的智能助手。

用户问题：{query}

知识库检索结果：
{context if context else "（未找到相关内容）"}

⚠️ 重要提示：
- 知识库中没有找到足够的相关内容
- 你必须诚实地告诉用户"我在知识库中没有找到相关信息"
- 绝对不要编造或猜测答案
- 不要使用你的训练数据中的知识

请回答用户的问题。"""
        
        elif quality_check["quality"] == "medium":
            # 质量中等：谨慎回答
            prompt = f"""你是一个诚实的智能助手。请严格基于以下知识库内容回答问题。

知识库内容：
{context}

用户问题：{query}

⚠️ 重要规则：
1. 只能使用上述知识库内容回答
2. 如果知识库内容不足以完整回答，明确说明"根据现有资料..."
3. 不要编造任何不在知识库中的信息
4. 不要使用你的训练数据补充答案
5. 如果不确定，说"我不确定"而不是猜测

请基于知识库内容回答问题。"""
        
        else:
            # 质量好：正常回答，但仍要约束
            prompt = f"""你是一个智能助手。请基于以下知识库内容回答用户的问题。

知识库内容：
{context}

用户问题：{query}

重要规则：
1. 主要基于上述知识库内容回答
2. 如果知识库内容不足，可以适当补充常识，但要明确说明
3. 不要编造具体的数字、日期、人名等细节
4. 保持客观和准确

请回答用户的问题。"""
        
        return prompt
    
    def validate_answer(
        self, 
        answer: str, 
        docs: List[Document],
        query: str
    ) -> Dict[str, Any]:
        """
        验证答案质量（简单版本）
        
        检查：
        1. 答案是否承认不知道
        2. 答案长度是否合理
        3. 是否包含警告词
        """
        answer_lower = answer.lower()
        
        # 检查是否承认不知道
        unknown_phrases = [
            "不知道", "没有找到", "无法确定", "不确定",
            "没有相关", "未找到", "无法回答", "不清楚"
        ]
        admits_unknown = any(phrase in answer_lower for phrase in unknown_phrases)
        
        # 检查是否有编造迹象（过于具体的数字、日期等）
        # 这是简化版本，实际可以更复杂
        suspicious_patterns = [
            "手机号", "电话", "邮箱", "qq", "微信",
            "身份证", "银行卡"
        ]
        has_suspicious = any(pattern in answer_lower for pattern in suspicious_patterns)
        
        # 检查答案长度
        if len(answer) < 10:
            quality = "poor"
        elif admits_unknown and len(docs) < 2:
            quality = "good"  # 正确承认不知道
        elif has_suspicious:
            quality = "suspicious"  # 可能有幻觉
        else:
            quality = "good"
        
        return {
            "quality": quality,
            "admits_unknown": admits_unknown,
            "has_suspicious": has_suspicious,
            "length": len(answer)
        }
    
    def _get_max_similarity(self, docs: List[Document]) -> float:
        """获取最高相似度"""
        if not docs:
            return 0.0
        
        scores = []
        for doc in docs:
            score = doc.metadata.get("score", 0.0)
            if score > 0:
                scores.append(score)
        
        if scores:
            return max(scores)
        
        # 如果没有分数，根据文档数量估算
        return 0.8 if len(docs) >= 3 else 0.6
    
    def get_fallback_response(self, query: str, warning: str) -> str:
        """
        获取降级响应（当检索质量太差时）
        """
        return f"""抱歉，我在知识库中没有找到关于"{query}"的相关信息。

原因：{warning}

建议：
1. 尝试换一种问法
2. 确认问题是否在知识库范围内
3. 检查是否有拼写错误

我只能基于已导入的文档回答问题，无法编造或猜测答案。"""


class CitationEnforcer:
    """引用强制器 - 要求 LLM 引用来源"""
    
    @staticmethod
    def add_citation_requirement(prompt: str, docs: List[Document]) -> str:
        """
        在提示词中添加引用要求
        """
        # 为每个文档添加编号
        numbered_context = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "未知")
            page = doc.metadata.get("page", "未知")
            numbered_context.append(
                f"[文档{i}]（来源：{source}，页码：{page}）\n{doc.page_content}"
            )
        
        context = "\n\n".join(numbered_context)
        
        # 修改提示词，要求引用
        enhanced_prompt = f"""你是一个严谨的智能助手。请基于以下编号的文档回答问题。

{context}

用户问题：{prompt.split('用户问题：')[-1] if '用户问题：' in prompt else prompt}

重要要求：
1. 回答时必须引用文档编号，如"根据[文档1]..."
2. 不同来源的信息要分别说明
3. 如果多个文档有矛盾，要指出差异
4. 只使用上述文档中的信息

请回答问题，并标注引用来源。"""
        
        return enhanced_prompt
    
    @staticmethod
    def extract_citations(answer: str) -> List[int]:
        """提取答案中的引用编号"""
        import re
        citations = re.findall(r'\[文档(\d+)\]', answer)
        return [int(c) for c in citations]


class FactChecker:
    """事实检查器 - 检查答案是否与文档一致"""
    
    @staticmethod
    def check_consistency(answer: str, docs: List[Document]) -> Dict[str, Any]:
        """
        检查答案与文档的一致性（简化版本）
        
        实际应该用更复杂的 NLP 技术
        """
        # 提取文档中的关键实体
        doc_entities = set()
        for doc in docs:
            # 简单提取：中文人名、地名等（实际应该用 NER）
            content = doc.page_content
            doc_entities.update(content.split())
        
        # 检查答案中的实体是否在文档中
        answer_words = set(answer.split())
        
        # 计算重叠度
        if not answer_words:
            overlap = 0.0
        else:
            overlap = len(answer_words & doc_entities) / len(answer_words)
        
        return {
            "overlap": overlap,
            "is_consistent": overlap > 0.3,  # 30% 重叠认为一致
            "doc_entities_count": len(doc_entities),
            "answer_words_count": len(answer_words)
        }
