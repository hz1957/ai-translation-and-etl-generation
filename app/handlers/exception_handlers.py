# app/handlers/exception_handlers.py
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from ..schemas import ErrorDetail

logger = logging.getLogger(__name__)

async def generic_exception_handler(request: Request, exc: Exception):
    """
    捕获所有未处理的异常，并以统一的JSON格式返回。
    """
    logger.error(f"在处理请求 {request.url} 时发生未捕获的异常", exc_info=exc)
    
    # 区分HTTPException和其他通用异常
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        message = exc.detail
    else:
        status_code = 500
        message = "服务器内部发生未知错误"

    error_detail = ErrorDetail(code=status_code, message=message)
    
    return JSONResponse(
        status_code=status_code,
        content=error_detail.model_dump(),
    )