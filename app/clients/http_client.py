# app/clients/http_client.py
import logging
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    管理应用的生命周期事件，特别关注 HTTP 客户端的创建和销毁。
    """
    # 在应用启动时，创建一个全局共享的 httpx.AsyncClient
    async with httpx.AsyncClient() as client:
        app.state.http_client = client  # type: ignore
        logger.info("HTTPX 客户端已启动并注入到应用状态")
        yield
    # 在应用关闭时，客户端会被自动关闭
    logger.info("HTTPX 客户端已关闭")