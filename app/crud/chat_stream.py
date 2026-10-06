


import json
import time
import uuid

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from app.core.content_filter import ContentFilter
from app.core.logger import Logger
from app.core.token_stats import add_token_stat
from app.llm.client_factory import get_llm_client

# 获取日志器
logger = Logger.get_logger(__name__)
# 创建内存存储会话(模拟数据库)
chat_sessions: dict[str, list[dict]] = {}
def llm_stream_chat(question: str, session_id: str | None, system_prompt: str | None):
    """
    流式输出的问答接口
    """
    # 获取session_id
    if not session_id:
        session_id = str(uuid.uuid4())
    # 读取当前会话历史，不存在则新建messages
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    messages = chat_sessions[session_id]
    # 将用户提问添加到会话中
    messages.append({"role": "user", "content": question})
    # 获取开始时间
    start_time = time.perf_counter()
    # 获取LLM客户端
    full_content = "" # 存储完整内容
    try:
        # 调用流式聊天接口
        llm_client = get_llm_client()
        stream = llm_client.chat_stream(messages=messages, system_prompt=system_prompt)
        for chunk in stream:
            # 跳过无效或空数据
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            # 提取内容,如果delta.content为空则赋值空字符串
            delta_content = delta.content or ""
            if not delta_content:
                continue
            full_content += delta_content
            # 流式安全校验,如果包含违规关键词则终止流式输出
            if ContentFilter.check_text(full_content):
                # 命中违规内容, 截断
                err_msg = json.dumps({
                    "code": 400,
                    "message": "检测到违规内容,请重新提问",
                    "data": None
                })
                yield f"data: {err_msg}\n\n"
                logger.warning(f"流式输出命中违规词, 会话session_id: {session_id} 被截断,已输出内容: {full_content}")
                return
            chunk_data = json.dumps(delta_content, ensure_ascii=False)
            yield f"data: {chunk_data}\n\n"
            messages.append({"role": "assistant", "content": full_content})
        usage_info = ""
        if chunk.usage:
            # 统计token消耗
            add_token_stat(chunk.usage.prompt_tokens, chunk.usage.completion_tokens)
            usage_info = (
                f"prompt_tokens: {chunk.usage.prompt_tokens}, |"
                f"completion_tokens: {chunk.usage.completion_tokens}, |"
                f"total_tokens: {chunk.usage.total_tokens} |"
            )
        # 获取调用模型消耗的时间
        end_time = time.perf_counter() - start_time
        logger.info(f"LLM输出:"
                    f"模型名: {llm_client.model} |"
                    f"模型输出: {full_content!r} |"
                    f"调用时间: {end_time:.2f}秒 |"
                    f"会话ID: {session_id} |"
                    f"Tokens: {usage_info}"
        )
        yield f"data: {json.dumps({'finish': True}, ensure_ascii=False)}\n\n"
    # 超时异常,重试耗尽后抛出
    except APITimeoutError:
        cost_time = round(time.perf_counter() - start_time, 4)
        logger.error("LLM调用超时", extra={"session_id": session_id, "cost_time_sec": cost_time})
        err_data = json.dumps({"code": 504, "message": "访问超时，请稍后重试","data": None})
        yield f"data: {err_data}\n\n"
        return
    # 429限流,重试3次失败进入这里
    except RateLimitError:
        cost_time = round(time.perf_counter() - start_time, 4)
        logger.error("LLM 429限流,重试耗尽", extra={"session_id": session_id, "cost_time_sec": cost_time})
        err_data = json.dumps({"code": 429, "message": "服务繁忙，请稍后重试","data": None})
        yield f"data: {err_data}\n\n"
        return
    # LLM侧API秘钥错误
    except AuthenticationError:
        cost_time = round(time.perf_counter() - start_time, 4)
        logger.error("LLM API秘钥错误", extra={"session_id": session_id, "cost_time_sec": cost_time})
        err_data = json.dumps({"code": 401, "message": "大模型配置API秘钥错误","data": None})
        yield f"data: {err_data}\n\n"
        return
    # 断网,连接异常
    except APIConnectionError:
        cost_time = round(time.perf_counter() - start_time, 4)
        logger.error("LLM连接异常", extra={"session_id": session_id, "cost_time_sec": cost_time})
        err_data = json.dumps({"code": 500, "message": "服务繁忙，请稍后重试","data": None})
        yield f"data: {err_data}\n\n"
        return
    # 其他模型调用异常,打印日志,抛出HTTPException
    except APIError:
        cost_time = round(time.perf_counter() - start_time, 4)
        logger.error("LLM通用 API异常", extra={"session_id": session_id, "cost_time_sec": cost_time})
        err_data = {"code": 500, "message": "大模型服务调用异常", "data": None}
        yield f"data: {err_data}\n\n"
        return
    except Exception:
        cost_time = round(time.perf_counter() - start_time, 4)
        logger.error("LLM未知异常", extra={"session_id": session_id, "cost_time_sec": cost_time}, exc_info=True)
        err_data = {"code": 500, "message": "服务内部错误", "data": None}
        yield f"data: {err_data}\n\n"
        return

