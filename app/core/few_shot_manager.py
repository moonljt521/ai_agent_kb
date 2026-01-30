"""
Few-Shot 示例管理器
根据问题类型自动选择合适的示例
"""
import json
import os
from typing import List, Dict, Optional

class FewShotManager:
    def __init__(self, config_path="config/few_shot_examples.json"):
        self.config_path = config_path
        self.examples = self._load_examples()
    
    def _load_examples(self) -> Dict:
        """加载 Few-Shot 示例配置"""
        if not os.path.exists(self.config_path):
            print(f"⚠️  Few-Shot 配置文件不存在: {self.config_path}")
            return {}
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def detect_question_type(self, query: str) -> Optional[str]:
        """
        检测问题类型
        
        返回: "人物介绍" | "人物关系" | "故事情节" | None
        """
        # 人物介绍关键词
        if any(keyword in query for keyword in ["是谁", "什么人", "介绍", "哪里人"]):
            return "人物介绍"
        
        # 人物关系关键词
        if any(keyword in query for keyword in ["关系", "和", "与", "之间"]):
            # 检查是否包含两个人名（简单判断：包含"和"或"与"）
            if "和" in query or "与" in query:
                return "人物关系"
        
        # 故事情节关键词
        if any(keyword in query for keyword in ["故事", "情节", "经过", "怎么", "如何", "为什么"]):
            return "故事情节"
        
        return None
    
    def get_examples(self, question_type: Optional[str] = None, max_examples: int = 2) -> List[Dict]:
        """
        获取 Few-Shot 示例
        
        参数:
            question_type: 问题类型，如果为 None 则返回所有类型的示例
            max_examples: 每种类型最多返回的示例数
        
        返回:
            示例列表
        """
        if not self.examples:
            return []
        
        if question_type and question_type in self.examples:
            # 返回指定类型的示例
            return self.examples[question_type][:max_examples]
        
        # 返回所有类型的示例（每种类型取1个）
        all_examples = []
        for examples in self.examples.values():
            if examples:
                all_examples.append(examples[0])
        return all_examples[:max_examples]
    
    def format_examples_for_prompt(self, examples: List[Dict]) -> str:
        """
        将示例格式化为提示词
        
        返回:
            格式化后的示例文本
        """
        if not examples:
            return ""
        
        formatted = "以下是一些回答示例，请参考这种格式和风格回答：\n\n"
        
        for i, example in enumerate(examples, 1):
            formatted += f"【示例 {i}】\n"
            formatted += f"问题：{example['query']}\n"
            if 'context' in example:
                formatted += f"知识库内容：{example['context']}\n"
            formatted += f"回答：{example['answer']}\n\n"
        
        formatted += "---\n\n现在请回答用户的问题：\n"
        return formatted
    
    def build_few_shot_prompt(self, query: str, context: str, auto_detect: bool = True) -> str:
        """
        构建包含 Few-Shot 示例的完整提示词
        
        参数:
            query: 用户问题
            context: 从知识库检索到的内容
            auto_detect: 是否自动检测问题类型
        
        返回:
            完整的提示词
        """
        # 检测问题类型
        question_type = self.detect_question_type(query) if auto_detect else None
        
        # 获取示例
        examples = self.get_examples(question_type, max_examples=2)
        
        # 构建提示词
        prompt = ""
        
        if examples:
            prompt += self.format_examples_for_prompt(examples)
        
        prompt += f"问题：{query}\n"
        
        if context:
            prompt += f"知识库内容：{context}\n"
        
        prompt += "回答："
        
        return prompt
    
    def get_statistics(self) -> Dict:
        """获取 Few-Shot 示例统计"""
        stats = {
            "总示例数": sum(len(examples) for examples in self.examples.values()),
            "分类统计": {}
        }
        
        for category, examples in self.examples.items():
            stats["分类统计"][category] = len(examples)
        
        return stats

# 测试代码
if __name__ == "__main__":
    manager = FewShotManager()
    
    print("=" * 60)
    print("Few-Shot 示例管理器测试")
    print("=" * 60)
    
    # 测试问题类型检测
    test_queries = [
        "贾宝玉是谁？",
        "刘备和诸葛亮是什么关系？",
        "三顾茅庐的故事是什么？",
        "今天天气怎么样？",
    ]
    
    print("\n【问题类型检测】")
    for query in test_queries:
        qtype = manager.detect_question_type(query)
        print(f"问题: {query}")
        print(f"类型: {qtype or '未识别'}\n")
    
    # 测试获取示例
    print("=" * 60)
    print("【获取人物介绍示例】")
    examples = manager.get_examples("人物介绍", max_examples=1)
    print(manager.format_examples_for_prompt(examples))
    
    # 测试构建完整提示词
    print("=" * 60)
    print("【构建完整提示词】")
    prompt = manager.build_few_shot_prompt(
        query="武松是谁？",
        context="武松是《水浒传》中的人物，绰号行者，因在景阳冈打虎而闻名。",
        auto_detect=True
    )
    print(prompt)
    
    # 统计信息
    print("=" * 60)
    print("【统计信息】")
    stats = manager.get_statistics()
    print(json.dumps(stats, ensure_ascii=False, indent=2))
