
import json
import logging
import os
import re
import time
from typing import Optional

from dotenv import load_dotenv
from openai import APIConnectionError, APITimeoutError, AuthenticationError, OpenAI, RateLimitError
from tenacity import before_sleep_log, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

load_dotenv()

class LLMClient:
    """
    封装LLM API
    """
   
    # 初始化日志,配置基础日志格式
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)

    def __init__(self):
        """
        初始化函数，从环境变量中获取API密钥
        """
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL")
        self.timeout = os.getenv("DEEPSEEK_TIMEOUT")
        self.model = os.getenv("DEEPSEEK_MODEL")
        self.client = OpenAI(
            api_key=self.api_key, 
            base_url=self.base_url,
            timeout=self.timeout
        )
        self.messages = []  # 存储对话消息,实现多轮对话
        
        logging.info(f"LLMClient初始化完成, 历史消息数= {len(self.messages)}")

    @retry(
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((APIConnectionError, APITimeoutError, RateLimitError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.warning),  # 重试前打印日志
        reraise=True   # 重试耗尽后抛出原始异常
    )
    def chat(self,messages: list[dict],system_prompt: Optional[str] = None,max_tokens: int=1024):
        
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
        self.messages.extend(messages)
        # 记录开始时刻
        start_time = time.perf_counter()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=0.0,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            resp = response.choices[0].message.content
            # 记录结束时刻
            end_time = time.perf_counter()
            # 计算运行时间
            run_time = end_time - start_time
            # token消耗
            usage = response.usage
            json_data = self.parse_llm_json(resp)
            self.logger.info(f"输出日志:"
                        f"模型为: {response.model} |"
                        f"消耗时间: {run_time:.2f}s |"
                        f"token消耗: {usage.total_tokens} |"
                        f"输入token消耗: {usage.prompt_tokens} |"
                        f"输出token消耗: {usage.completion_tokens} |"
                        f"输出: {json_data}"
            )
            return resp
        except json.JSONDecodeError as e:
            logging.error(f"JSON解析错误: {e}")  
            raise
        except AuthenticationError as e:
            logging.error(f"API鉴权错误: {e}")
            raise
        except Exception as e:
            print(f"请求错误: {e}")

    def parse_llm_json(self,data: str) -> dict:
        """
        数据清洗
        :param data: 模型返回的json数据
        """
        pattern = r"```(?:json)?\n?(.*?)\n?```"
        match = re.search(pattern, data, re.DOTALL)
        if match:
            # 获取匹配到的json数据,并去除字符串首尾的空格
            raw_json = match.group(1).strip()
        else:
            # 没有匹配到json数据块，返回原始数据
            raw_json = data.strip()
        try:
            json_data = json.loads(raw_json)
            return json_data
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析错误,清洗后的数据为: {raw_json}, err: {e}") from e
        except Exception as e:
            raise ValueError(f"未知错误, err: {e}") from e
        
     

