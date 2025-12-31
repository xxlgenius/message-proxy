import time
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI, Request

from message_proxy.api import router
from message_proxy.config import settings
from message_proxy.logging_config import get_logger, setup_logging

# 初始化日志配置
setup_logging()
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI应用生命周期管理"""
    # 启动时创建httpx异步客户端
    app.state.http_client = httpx.AsyncClient()
    logger.info("HTTP客户端已初始化")

    yield

    # 关闭时释放httpx异步客户端
    await app.state.http_client.aclose()
    logger.info("HTTP客户端已关闭")


app = FastAPI(title="Personal Message Proxy", lifespan=lifespan)
app.include_router(router)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # 记录请求开始
    logger.info(f"Request started: {request.method} {request.url.path}")

    response = await call_next(request)

    # 计算处理时间
    process_time = time.time() - start_time

    # 记录请求完成
    logger.info(
        f"Request completed: {request.method} {request.url.path} "
        f"Status: {response.status_code} Duration: {process_time:.3f}s"
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port, reload_excludes=[".logs"])
