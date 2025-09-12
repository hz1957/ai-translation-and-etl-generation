# app/main.py
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config.logging import configure_logging
from .api.translate_api import router as translate_router
from .api.data_labeling_api import router as data_annotation_router
from .api.etl_json_api import router as etl_json_router
from .handlers.exception_handlers import generic_exception_handler
from .clients.http_client import lifespan

# --- 日志配置 ---
configure_logging()
logger = logging.getLogger(__name__)


# 创建FastAPI应用实例
app = FastAPI(
    title="数统模型服务",
    description="供数统服务调用的模型服务",
    version="1.0.0",
    lifespan=lifespan,
)

# --- 全局异常处理器 ---
app.add_exception_handler(Exception, generic_exception_handler)

# --- 静态文件 ---
# 挂载static目录，用于提供前端文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- 路由 ---
app.include_router(translate_router)
app.include_router(data_annotation_router)
app.include_router(etl_json_router)