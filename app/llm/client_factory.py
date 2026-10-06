"""
LLM客户端工厂
"""


import os

from app.llm.base import BaseLLMClient
from app.llm.deepseek_client import DeepSeekClient
from app.llm.openai_client import OpenAIClient
from app.llm.qwen_client import QwenClient


def get_llm_client() -> BaseLLMClient:
    """工厂函数,根据环境变量选择模型厂商,获取模型客户端"""

    model_vendor = os.getenv("LLM_MODEL_VENDOR", "openai").lower()
    if model_vendor == "openai":
        return OpenAIClient()
    elif model_vendor == "deepseek":
        return DeepSeekClient()
    elif model_vendor == "qwen":
        return QwenClient()
    else:
        raise ValueError(f"不支持的模型厂商: {model_vendor},可选模型厂商: openai,deepseek,qwen")
