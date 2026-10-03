


import logging
import os
import time

from dotenv import load_dotenv
from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, OpenAI, RateLimitError
from tenacity import before_sleep_log, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    timeout=60
)

def get_call_llm(messages: list, model: str="gpt-3.5-turbo-0301", max_retry: int=3, wait_sec: int=2):
    """
    获取LLM的回复,且实现重试机制
    :param messages: 聊天消息列表
    :param model: 模型名称
    :param max_retry: 最大重试次数
    :param wait_sec: 重试间隔时间
    """
    for attemt in range(max_retry + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
            return response.choices[0].message.content
        except AuthenticationError:
            # 401错误直接抛出,不重试
            print("401错误!API秘钥错误/鉴权失败,请检查key")
            raise
        except APITimeoutError:
            print(f"请求超时,第{attemt + 1}次调用超时")
            
        except APIError as e:
            print(f"请求错误,第{attemt + 1}次调用失败,错误信息: {e}")
            if e.status_code == 429:
                print(f"[429限流]请求被限制,等待{wait_sec}s重试,剩余重试次数: {max_retry - attemt - 1}")
            else:
                print(f"服务端异常, status={e.status_code}, {e}")

        # 最后一次失败,不再sleep
        if attemt == max_retry: 
            break
        time.sleep(wait_sec)    
    raise Exception(f"调用LLm失败, 已达到最大重试次数: {max_retry}")

@retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=30), # 2s → 4s → 8s...最大30s
        retry=retry_if_exception_type(RateLimitError, APIConnectionError), # 仅对429限流,网络异常进行重试
        before_sleep=lambda retry_state: logging.warning(
            f"⚠️ 请求失败, {retry_state.seconds_since_start:.1f}s 后进行第: {retry_state.attempt_number} 次重试, 错误信息: {retry_state.outcome.exception()}"
        ),
        reraise=True
)
def call_llm(msg, model="gpt-3.5-turbo-0301", max_retry=5, wait_sec=1):  
    """
    使用OpenAI API调用LLM(使用tenacity实现重试机制)
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=msg,
        )
        return response.choices[0].message.content
    except AuthenticationError:
        # 401认证错误
        print("401错误!API秘钥错误/鉴权失败,请检查key")
        raise
    except Exception as e:
        # 其他错误
        print(f"其他错误: {e}")
        raise

if __name__ == "__main__":
    msg = [{"role":"system", "content":"简短回答"}, {"role":"user","content":"你好"}]
    model = os.getenv("DEEPSEEK_MODEL")
    res = get_call_llm(msg,model=model)
    print(res)
       

        