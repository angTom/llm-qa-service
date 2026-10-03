
from fastapi import FastAPI


from middleware.logging_middleware import AccessLogMiddleware
from routers import chat, health, sessions

from app.core.exception_handler import register_exception_handlers


app = FastAPI()


# 关键步骤：在 app 创建后立即注册
# 异常处理注册
register_exception_handlers(app)
# 注册日志中间件
app.add_middleware(AccessLogMiddleware)
# 注册路由
app.include_router(chat.router)
app.include_router(health.router)
app.include_router(sessions.router)

@app.get("/") 
async def root():
    return {"message": "Hello World"}


