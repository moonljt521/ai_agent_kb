"""
简单的对话记忆实现
不依赖 langchain.memory，使用基础的 LangChain 消息类型
"""

from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Dict, Any


class SimpleConversationMemory:
    """简单的对话记忆，保留最近 N 轮对话"""
    
    def __init__(self, k: int = 5):
        """
        初始化记忆
        
        Args:
            k: 保留最近 k 轮对话（每轮包含用户消息和AI回复）
        """
        self.k = k
        self.messages: List[Any] = []
    
    def save_context(self, inputs: Dict[str, str], outputs: Dict[str, str]):
        """
        保存一轮对话
        
        Args:
            inputs: 包含用户输入的字典，如 {"input": "用户问题"}
            outputs: 包含AI输出的字典，如 {"output": "AI回答"}
        """
        # 添加用户消息
        user_message = HumanMessage(content=inputs.get("input", ""))
        self.messages.append(user_message)
        
        # 添加AI消息
        ai_message = AIMessage(content=outputs.get("output", ""))
        self.messages.append(ai_message)
        
        # 只保留最近 k 轮对话（k*2 条消息）
        max_messages = self.k * 2
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]
    
    def load_memory_variables(self, inputs: Dict[str, Any] = None) -> Dict[str, List]:
        """
        加载记忆变量
        
        Returns:
            包含对话历史的字典
        """
        return {"chat_history": self.messages}
    
    def clear(self):
        """清空记忆"""
        self.messages = []
    
    def get_messages(self) -> List[Any]:
        """获取所有消息"""
        return self.messages
    
    def get_last_n_messages(self, n: int) -> List[Any]:
        """获取最近 n 条消息"""
        return self.messages[-n:] if n > 0 else []
