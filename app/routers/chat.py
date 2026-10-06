

# 创建路由实例
import json
import time
import uuid

from fastapi import APIRouter, HTTPException, Security
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)
from schemas.chat import ChatItem, ChatReq
from utils.response import success_response

from app.core.logger import Logger
from app.core.security import verify_api_key
from app.llm.client_factory import get_llm_client

router = APIRouter(
    prefix="/chat",
    tags=["对话接口"],
    dependencies=[Security(verify_api_key)],  # 整个路由组全部开启鉴权
)

# 获取日志器
logger = Logger.get_logger(__name__)
# 创建LLM客户端
llm_client = get_llm_client()

# 内存存储会话(模拟数据库)
chat_sessions: dict[str, list[dict]] = {}

@router.post("/")
async def chat(item: ChatItem):

    response = llm_client.chat(item.messages, item.system_prompt)
    json_data = json.loads(response)
    return success_response(message="请求成功", data=json_data)

@router.get("/query")
async def query(item: ChatItem):
    messages = item.messages

    return success_response(message="请求成功", data=messages)


@router.post("/ask")
async def chat_ask():
    return {
        "code": 200,
        "msg": "success",
        "data": "LLM问答结果"
    }

@router.post("")
async def chat_request(req: ChatReq):
    """
    获取用户问题，调用LLM模型，返回结果
    """
    # 开始时间
    start_time = time.perf_counter()
    # 获取会话ID
    session_id = req.session_id
    # 如果会话ID不存在，则生成一个新的会话ID
    if not session_id or session_id == "":
        session_id = str(uuid.uuid4())
    logger.info(f"session_id: {session_id}")
    # 读取当前会话历史，不存在则新建messages
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    messages = chat_sessions[session_id]

    # 将用户提问添加到会话中
    messages.append({"role": "user", "content": req.question})
    # 调用LLM客户端进行问答
    try:
        llm_resp = llm_client.chat(messages=messages, system_prompt=req.system_prompt)
        answer = llm_resp.choices[0].message.content
        prompt_tokens = llm_resp.usage.prompt_tokens
        completion_tokens = llm_resp.usage.completion_tokens
        # 把assistant回答写入会话
        messages.append({"role": "assistant", "content": answer})
        chat_sessions[session_id] = messages

        cost_time = round(time.perf_counter() - start_time, 4)

        # 打印输出日志
        logger.info(
           f"LLM调用成功! 模型: {llm_client.model} |",
            f"session_id: {session_id} |",
            f"questions: {req.question} |",
            f"answer: {answer} |",
            f"prompt_tokens: {prompt_tokens} |",
            f"completion_tokens: {completion_tokens} |",
            f"cost_time: {cost_time}",

        )

        return success_response(message="请求成功", data={
            "model": llm_client.model,
            "session_id": session_id,
            "questions": req.question,
            "answer": answer,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost_time": cost_time,
        })
    # 超时异常,重试耗尽后抛出
    except APITimeoutError:
        cost_time = round(time.perf_counter() - start_time, 4)
        logger.error("LLM调用超时", extra={"session_id": session_id, "cost_time_sec": cost_time})
        raise HTTPException(status_code=500, detail="服务繁忙，请稍后重试")
    # 429限流,重试3次失败进入这里
    except RateLimitError:
        cost_time = round(time.perf_counter() - start_time, 4)
        logger.error("LLM 429限流,重试耗尽", extra={"session_id": session_id, "cost_time_sec": cost_time})
        raise HTTPException(status_code=500, detail="服务繁忙，请稍后重试")
    # LLM侧API秘钥错误
    except AuthenticationError:
        cost_time = round(time.perf_counter() - start_time, 4)
        logger.error("LLM 鉴权失败,API_KEY错误", extra={"session_id": session_id, "cost_time_sec": cost_time})
        raise HTTPException(status_code=500, detail="大模型服务配置异常")
    # 断网,连接异常
    except APIConnectionError:
        cost_time = round(time.perf_counter() - start_time, 4)
        logger.error("LLM网络连接异常", extra={"session_id": session_id, "cost_time_sec": cost_time})
        raise HTTPException(status_code=500, detail="服务繁忙，请稍后重试")
    # 其他模型错误 (模型名写错等)
    except APIError as e:
        cost_time = round(time.perf_counter() - start_time, 4)
        logger.error(f"LLM通用 API异常: {e!s}", extra={"session_id": session_id, "cost_time_sec": cost_time})
        raise HTTPException(status_code=500, detail="大模型服务调用异常")
    # 兜底捕获所有未知异常
    except Exception as e:
        cost_time = round(time.perf_counter() - start_time, 4)
        logger.error(f"LLM未知异常: {e!s}", extra={"session_id": session_id, "cost_time_sec": cost_time}, exc_info=True)
        raise HTTPException(status_code=500, detail="服务内部错误") from e
