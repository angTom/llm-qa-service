
"""
健康检测
"""

from fastapi import APIRouter

# 实例化路由
router = APIRouter(tags=["健康检测"])

@router.get("/health", summary="健康检测")
async def health():
    """健康检测"""
    return {
        "code": 200,
        "message": "ok",
        "data": {
            "status": "healthy"
        }
    }
