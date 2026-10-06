"""
全局异常拦截处理
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.utils.response import success_response

app = FastAPI(title="全局异常")


def register_exception_handlers(app: FastAPI):

    # 捕获未处理的python常规异常(兜底所有未知异常)
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        err_msg = exc.detail if hasattr(exc, "detail") else str(exc)
        return JSONResponse(
            status_code=500,
            content=success_response(
                code=500,
                message=f"服务器内部错误: {err_msg}",
                data=None
            )
        )
    # 捕获fastAPI参数效验异常 (422错误)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=success_response(
                code=422,
                message="参数效验错误",
                data=[{"field": err["loc"][-1], "msg": err["msg"]} for err in exc.errors()]
            )
        )

    # 捕获401异常
    @app.exception_handler(HTTPException)
    async def unauthorized_exception_handler(request: Request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
                "data": None
            }
        )
