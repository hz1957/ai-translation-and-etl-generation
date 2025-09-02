# app/config/logging.py
import logging
import sys
from .settings import settings

class EndpointFilter(logging.Filter):
    """
    一个日志过滤器，用于过滤掉特定端点的访问日志。
    """
    def __init__(self, path: str):
        super().__init__()
        self._path = path

    def filter(self, record: logging.LogRecord) -> bool:
        # 检查日志消息是否包含指定的路径
        return record.getMessage().find(self._path) == -1

def configure_logging():
    """
    根据应用环境配置日志记录器。
    - 开发环境 (dev): 日志级别为 DEBUG。
    - 生产环境 (prod): 日志级别为 INFO。
    """
    log_level = logging.DEBUG if settings.app_env == "dev" else logging.INFO
    
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
        stream=sys.stdout,
    )
    
    # --- 过滤特定端点的访问日志 ---
    # 实例化我们的过滤器，并将其添加到uvicorn.access记录器中
    # 这可以防止前端仪表盘的轮询请求刷屏
    status_filter = EndpointFilter(path="/api/model-platform/status")
    logging.getLogger("uvicorn.access").addFilter(status_filter)

    logger = logging.getLogger(__name__)
    logger.info(f"日志系统已配置完成，当前日志级别: {logging.getLevelName(log_level)}")