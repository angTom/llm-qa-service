"""
调用LLM进行问答(流式输出)
"""




from fastapi import APIRouter, Security
from fastapi.responses import StreamingResponse

from app.core.logger import Logger
from app.core.security import verify_api_key
from app.core.token_stats import get_token_stat
from app.crud.chat_stream import llm_stream_chat
from app.schemas.chat_stream import ChatStreamRequest

logger = Logger.get_logger(__name__)



router = APIRouter(
    prefix="/chat",
    tags=["对话接口(流式输出)"],
    dependencies=[Security(verify_api_key)],  # 整个路由组全部开启鉴权
)
@router.post("/stream",response_class=StreamingResponse)
async def stream_chat(req: ChatStreamRequest):
    """
    调用LLM进行问答(流式输出)

    args:
        req: ChatStreamRequest  请求参数
    """
    logger.info(f"收到请求: {req.model_dump(by_alias=False)}")

    stream_resp = llm_stream_chat(question=req.question, session_id=req.session_id,system_prompt=req.system_prompt)

    return StreamingResponse(stream_resp, media_type="text/event-stream")

@router.get("/stream/status")
async def get_status():
    """
    获取流式对话状态
    """
    data = get_token_stat()
    return {
        "code": 200,
        "message": "success",
        "data": data
    }
