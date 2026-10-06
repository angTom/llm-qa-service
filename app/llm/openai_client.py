


import os

from openai import OpenAI

from app.core.logger import Logger
from app.llm.base import BaseLLMClient


class OpenAIClient(BaseLLMClient):

    logger = Logger.get_logger(__name__)
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.timeout = os.getenv("OPENAI_TIMEOUT","60")
        self.model = os.getenv("OPENAI_MODEL")
        if self.api_key is None:
            raise ValueError("请设置环境变量 OPENAI_API_KEY")
        if self.model is None:
            raise ValueError("请设置环境变量 OPENAI_MODEL")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=int(self.timeout)
        )
        self.logger.info("OpenAI LLMClient 启动完成")

    def chat_completion(self, messages, system_prompt, max_tokens):
        """
        聊天接口
        :param messages: list[dict], 聊天消息列表
        :param system_prompt: str, 系统提示
        :param max_tokens: int, 最大token数
        :return: str, 聊天结果
        """
        fail_messages = []
        self.add_system_prompt(fail_messages, system_prompt)
        # 追加系统提示
        fail_messages.extend(messages)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=fail_messages,
            temperature=0,
            max_tokens=max_tokens
        )
        return response

    def chat_stream_completion(self, messages, system_prompt, max_tokens):
        """
        流式聊天接口
        :param messages: list[dict], 聊天消息列表
        :param system_prompt: str, 系统提示
        :param max_tokens: int, 最大token数
        :return: str, 聊天结果
        """
        fail_messages = []
        self.add_system_prompt(fail_messages, system_prompt)
        # 追加系统提示
        fail_messages.extend(messages)
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=fail_messages,
            temperature=0,
            stream=True,
            stream_options={"include_usage": True},
            max_tokens=max_tokens
        )
        yield from stream
