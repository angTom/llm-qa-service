
from fastapi import FastAPI
from routers import chat, health, sessions

from app.core.exception_handler import register_exception_handlers
from app.routers import chat_stream
from middleware.logging_middleware import AccessLogMiddleware

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
app.include_router(chat_stream.router)  # 注册流式输出路由
@app.get("/")
async def root():
    return {"message": "Hello World"}


