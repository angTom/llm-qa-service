


import os

from dotenv import load_dotenv
from openai import OpenAI

from app.core.logger import Logger
from app.llm.base import BaseLLMClient


class QwenClient(BaseLLMClient):
    """
    通义千问适配器实现类
    """
    # 读取.env文件
    load_dotenv()
    logger = Logger.get_logger(__name__)

    def __init__(self):
        self.api_key = os.getenv("QWEN_API_KEY")
        self.base_url = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.timeout = os.getenv("QWEN_TIMEOUT", "60")
        self.model = os.getenv("QWEN_MODEL")
        if self.api_key is None:
            raise ValueError("请设置环境变量 QWEN_API_KEY")
        if self.model is None:
            raise ValueError("请设置环境变量 QWEN_MODEL")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=int(self.timeout)
        )
        self.logger.info("LLMClient 启动完成")

    def chat_completion(self, messages, system_prompt = None, max_tokens = 1024):
        """
        qwen聊天接口
        """
        fail_messages = [] # 最终的消息列表
        self.add_system_prompt(fail_messages,system_prompt)
        # 追加消息列表
        fail_messages.extend(messages)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=fail_messages,
            max_tokens=max_tokens,
            temperature=0
        )
        return response


    def stream_chat_completion(self, messages, system_prompt, max_token):
        fail_messages = [] # 最终的消息列表
        self.add_system_prompt(fail_messages,system_prompt)
        # 追加消息列表
        fail_messages.extend(messages)
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            max_tokens=max_token,
            temperature=0,
            stream=True,
            stream_options={"include_usage": True}
        )
        yield from stream
