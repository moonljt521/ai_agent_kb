"""
文档标签管理器
用于给知识库文档添加标签，实现精准检索和过滤
"""
import json
import os
from pathlib import Path

class DocumentTagger:
    def __init__(self, config_path="config/document_tags.json"):
        self.config_path = config_path
        self.tags_config = self._load_config()
        self.file_mapping = self.tags_config.get("文件名映射", {})
        self.doc_tags = self.tags_config.get("文档标签映射", {})
    
    def _load_config(self):
        """加载标签配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_tags_for_file(self, file_path: str) -> dict:
        """
        根据文件路径获取标签
        
        参数:
            file_path: 文件路径（如 "data/红楼梦.epub"）
        
        返回:
            标签字典，如 {"book": "红楼梦", "category": ["人物", "情节"], ...}
        """
        # 提取文件名
        filename = os.path.basename(file_path)
        
        # 查找映射
        book_name = self.file_mapping.get(filename)
        
        if not book_name:
            # 尝试模糊匹配
            for key in self.file_mapping.keys():
                if key in filename or filename in key:
                    book_name = self.file_mapping[key]
                    break
        
        if not book_name:
            # 尝试从文件名中提取书名
            for book in self.doc_tags.keys():
                if book in filename:
                    book_name = book
                    break
        
        # 返回标签
        if book_name and book_name in self.doc_tags:
            return self.doc_tags[book_name]
        
        return {"book": "未知", "category": ["其他"]}
    
    def filter_by_tags(self, documents: list, filters: dict) -> list:
        """
        根据标签过滤文档
        
        参数:
            documents: 文档列表
            filters: 过滤条件，如 {"book": "红楼梦", "category": "人物"}
        
        返回:
            过滤后的文档列表
        """
        filtered = []
        
        for doc in documents:
            # 获取文档的标签
            doc_tags = doc.metadata.get("tags", {})
            
            # 检查是否匹配所有过滤条件
            match = True
            for key, value in filters.items():
                doc_value = doc_tags.get(key)
                
                if doc_value is None:
                    match = False
                    break
                
                # 如果是列表，检查是否包含
                if isinstance(doc_value, list):
                    if value not in doc_value:
                        match = False
                        break
                else:
                    if doc_value != value:
                        match = False
                        break
            
            if match:
                filtered.append(doc)
        
        return filtered
    
    def get_available_tags(self) -> dict:
        """获取所有可用的标签"""
        return self.tags_config.get("标签定义", {})
    
    def get_books(self) -> list:
        """获取所有书籍列表"""
        return list(self.doc_tags.keys())

    def get_book_tags_map(self) -> dict:
        """获取按书籍组织的标签映射"""
        return self.doc_tags.copy()
    
    def get_statistics(self) -> dict:
        """获取标签统计信息"""
        return {
            "书籍数量": len(self.doc_tags),
            "书籍列表": list(self.doc_tags.keys()),
            "标签类型": list(self.tags_config.get("标签定义", {}).keys()),
            "文件映射数": len(self.file_mapping)
        }
