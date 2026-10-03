
"""
会话CRUD路由
"""

from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Security

from schemas.session import SessionCreate
from utils.response import success_response
from app.core.security import verify_api_key

router = APIRouter(
    prefix="/api/v1/sessions",
    tags=["Session"],
    dependencies=[Security(verify_api_key)]
    )
# 内存存储会话(模拟数据库)
sessions: dict[str, dict] = {}

@router.post("", summary="创建新会话")
async def create_session(body: SessionCreate):
    """创建新会话"""
    session_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat() # 获取当前时间,并将其转换为符合ISO 8601标准的标准化字符串格式
    sessions[session_id] = {
        "id": session_id,
        "title": body.title,
        "user_id": body.user_id,
        "created_at": now,
        "updated_at": now,
        "messages": []
    }
    return success_response(message="创建成功",data=sessions[session_id])

@router.get("/{session_id}", summary="查询会话历史")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"会话{session_id}不存在")
    return success_response(message="查询成功",data=sessions[session_id])

@router.delete("/{session_id}", summary="删除会话")
async def delete_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"会话{session_id}不存在")
    del sessions[session_id]
    return success_response(message="删除成功")