


import os

from dotenv import load_dotenv
from openai import OpenAI

from app.llm.base import BaseLLMClient


class DeepSeekClient(BaseLLMClient):
    """
    deepseek client 实现类
    """

    # 读取.env文件
    load_dotenv()

    def __init__(self):
        """
        初始化 DeepSeekClient
        """
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.timeout = os.getenv("DEEPSEEK_TIMEOUT", "60")
        self.model = os.getenv("DEEPSEEK_MODEL")
        if self.api_key is None:
            raise ValueError("请设置环境变量 DEEPSEEK_API_KEY")
        if self.model is None:
            raise ValueError("请设置环境变量 DEEPSEEK_MODEL")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=int(self.timeout)
        )
        self.logger.info("LLMClient 启动完成")

    def chat_completion(self, messages, system_prompt, max_tokens):
        """
        聊天接口
        :param messages: list[dict], 聊天消息列表
        :param system_prompt: str, 系统提示
        :param max_tokens: int, 最大token数
        :return: str, 聊天结果
        """
        self.logger.info("LLMClient 正在请求")
        fail_messages = []   # 最终传入的消息列表
        self.add_system_prompt(fail_messages, system_prompt)
        # 追加多轮对话
        fail_messages.extend(messages)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.0,
        )
        return response

    def chat_stream_completion(self,messages,system_prompt,max_tokens):
        """
        流式聊天接口
        :param messages: list[dict], 聊天消息列表
        :param system_prompt: str, 系统提示
        :param max_tokens: int, 最大token数
        :return: str, 聊天结果
        """
        self.logger.info("开始调用流式LLM API")
        fail_messages = []  # 最终的聊天消息列表
        self.add_system_prompt(fail_messages, system_prompt)
        fail_messages.extend(messages) # 追加聊天消息
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=fail_messages,
            stream=True,
            stream_options={"include_usage": True},
            max_tokens=max_tokens,
            temperature=0.0,
        )
        yield from stream


