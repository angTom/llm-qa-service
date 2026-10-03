"""
全局异常拦截处理
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError

from app.utils.response import success_response


app = FastAPI(title="统一响应+全局异常")


def register_exception_handlers(app: FastAPI):

    # 捕获未处理的python常规异常(兜底所有未知异常)
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc):
        return success_response(
            code=500,
            message=f"服务器异常: {str(exc.detail)}"
        )
    # 捕获fastAPI参数效验异常 (422错误)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        err_msg = exc.errors()[0]["msg"]
        return success_response(
            code=422,
            message=f"参数效验错误:{err_msg}"
        )

    # 捕获401异常
    @app.exception_handler(HTTPException)
    async def unauthorized_exception_handler(request: Request, exc):
        return success_response(
            code=exc.status_code,
            message=f"访问失败: {str(exc.detail)}"
        )