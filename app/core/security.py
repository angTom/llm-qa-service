"""
使用APIKeyHeader实现鉴权
"""


import os

from dotenv import load_dotenv
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

# 定义Header 名称, auto_error=True 表示缺失时自动返回403
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
# 读取.env文件
load_dotenv()
# 合法密钥, 支持多个密钥! 用逗号分隔
VALID_API_KEY = set(os.getenv("API_KEY", "").split(","))

async def verify_api_key(api_key: str | None = Security(api_key_header)):
    """
    鉴权依赖项, 校验X-API-Key

    args:
        api_key: str | None = Security(api_key_header)  # 获取请求头X-API-Key

    return:
        api_key  获取的请求头X-API-Key    
    """
    # 没有传header
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺失X-API-Key请求头"
        )
    # 密钥不在合法列表
    if api_key not in VALID_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥"
        )
    return api_key
