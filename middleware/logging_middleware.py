
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import Logger

class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    日志中间件
    """

    # 获取日志配置器
    logger = Logger.get_logger(__name__)
    async def dispatch(self, request: Request, call_next):
        # 记录开始时间
        start_time = time.time()    
        # 放行请求,获取响应
        response = await call_next(request)
        # 记录结束时间
        end_time = time.time()
        # 计算耗时(四舍五入,保留2位小数)
        execution_time = round((end_time - start_time) * 1000,2)
        # 格式化日志信息
        self.logger.info(f"请求路径: {request.url.path} | 请求方法: {request.method} | 响应状态码: {response.status_code} | 耗时: {execution_time}ms")
        return response