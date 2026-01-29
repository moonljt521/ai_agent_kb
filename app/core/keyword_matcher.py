"""
关键词匹配模块
用于判断用户问题是否命中词条，从而决定是否直接检索向量库
"""
import json
import os
from typing import Tuple, List, Dict

class KeywordMatcher:
    def __init__(self, config_path="config/keywords.json"):
        self.config_path = config_path
        self.keywords = self._load_keywords()
        self.all_keywords_flat = self._flatten_keywords()
    
    def _load_keywords(self) -> Dict:
        """加载关键词配置"""
        if not os.path.exists(self.config_path):
            print(f"⚠️  关键词配置文件不存在: {self.config_path}")
            return {}
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _flatten_keywords(self) -> List[str]:
        """将所有关键词展平为一维列表"""
        keywords = []
        
        # 四大名著的关键词
        if "四大名著" in self.keywords:
            for book, categories in self.keywords["四大名著"].items():
                for category, words in categories.items():
                    keywords.extend(words)
        
        # 通用词条
        if "通用词条" in self.keywords:
            keywords.extend(self.keywords["通用词条"])
        
        return keywords
    
    def match(self, query: str) -> Tuple[bool, List[str], str]:
        """
        匹配用户问题是否包含关键词
        
        返回:
            (是否命中, 命中的关键词列表, 匹配原因)
        """
        matched_keywords = []
        
        # 检查是否包含任何关键词
        for keyword in self.all_keywords_flat:
            if keyword in query:
                matched_keywords.append(keyword)
        
        # 判断是否命中
        if matched_keywords:
            reason = f"命中关键词: {', '.join(matched_keywords[:3])}"
            if len(matched_keywords) > 3:
                reason += f" 等 {len(matched_keywords)} 个"
            return True, matched_keywords, reason
        
        return False, [], "未命中任何关键词"
    
    def should_use_direct_retrieval(self, query: str) -> Tuple[bool, str]:
        """
        判断是否应该使用直接检索（不走LLM）
        
        返回:
            (是否直接检索, 原因说明)
        """
        is_matched, keywords, reason = self.match(query)
        
        if is_matched:
            return True, f"✅ {reason}，直接检索向量库"
        else:
            return False, f"❌ {reason}，使用 LLM 处理"
    
    def get_statistics(self) -> Dict:
        """获取关键词统计信息"""
        stats = {
            "总关键词数": len(self.all_keywords_flat),
            "四大名著": {}
        }
        
        if "四大名著" in self.keywords:
            for book, categories in self.keywords["四大名著"].items():
                book_count = sum(len(words) for words in categories.values())
                stats["四大名著"][book] = {
                    "总数": book_count,
                    "分类": {cat: len(words) for cat, words in categories.items()}
                }
        
        if "通用词条" in self.keywords:
            stats["通用词条数"] = len(self.keywords["通用词条"])
        
        return stats

# 测试代码
if __name__ == "__main__":
    matcher = KeywordMatcher()
    
    # 测试用例
    test_queries = [
        "贾宝玉是谁？",
        "诸葛亮的故事",
        "孙悟空的师傅是谁",
        "武松打虎的故事",
        "今天天气怎么样",
        "什么是人工智能",
        "林黛玉和薛宝钗的关系",
    ]
    
    print("=" * 60)
    print("关键词匹配测试")
    print("=" * 60)
    
    for query in test_queries:
        should_direct, reason = matcher.should_use_direct_retrieval(query)
        print(f"\n问题: {query}")
        print(f"结果: {reason}")
    
    print("\n" + "=" * 60)
    print("关键词统计")
    print("=" * 60)
    stats = matcher.get_statistics()
    print(json.dumps(stats, ensure_ascii=False, indent=2))
