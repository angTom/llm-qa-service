"""
会话数据模型库
"""

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(...,pattern="^(system|user|assistant)$", description="角色")
    content: str = Field(..., min_length=1, max_length=4096)

class SessionCreate(BaseModel):
    """创建会话"""
    title: str = Field(default="新会话",max_length=100)
    user_id: int = Field(...,ge=1,description="用户ID")

class SessionResponse(BaseModel):
    """会话返回"""
    id: str
    title: str
    user_id: int
    messages: list[Message] = []
    created_at: str
    updated_at: str
