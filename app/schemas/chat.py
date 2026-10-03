

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ChatItem(BaseModel):
    messages: list[dict]
    system_prompt: Optional[str] = None


class ChatReq(BaseModel):
    """
    聊天请求数据模型
    """
    session_id: Optional[str] = Field(default=None,description="会话ID,不传,自动生成")
    questions: str = Field(...,description="用户问题内容")

    # # 问题长度校验
    # def model_post_init(self, __context):
    #     if len(self.questions.strip()) > 2000:
    #         raise ValueError("问题内容不能超过2000个字符")

    @field_validator("questions")
    def question_not_empty(cls, v: str):
        # 去除首尾空白,如果是空字符串,则直接抛校验错误
        if not v or not v.strip():
            raise ValueError("问题内容不能为空")
        if len(v.strip()) > 2000:
            raise ValueError("问题内容不能超过2000个字符")
        return v
