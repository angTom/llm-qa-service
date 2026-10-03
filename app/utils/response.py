"""
定义统一响应格式
"""

from fastapi.responses import JSONResponse

# 响应格式
def success_response(code: int = 200, message: str = "success",data: any=None) -> JSONResponse:
    return JSONResponse(
        status_code=200, 
        content={
            "code": code, 
            "msg": message, 
            "data": data
        }
    )

