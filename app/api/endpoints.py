# app/api/endpoints.py
from fastapi import APIRouter, Request, HTTPException
from ..schemas import TranslationRequest, TranslationResponse
from ..services.llm_service import translate_list_to_map, translation_cache
from ..monitoring.llm_monitoring import get_llm_stats
from fastapi.responses import JSONResponse, FileResponse

router = APIRouter(prefix="/api/model-platform")

@router.get("/dashboard", include_in_schema=False)
async def get_dashboard():
    """
    提供监控仪表盘的前端页面。
    """
    return FileResponse("static/index.html")

@router.get("/status")
async def get_status():
    """
    获取LLM服务的运行状态和最近的调用记录。
    """
    stats = get_llm_stats()
    # 添加缓存大小到统计数据中
    stats['cache_size'] = len(translation_cache)
    return JSONResponse(content=stats)

@router.post("/translate", response_model=TranslationResponse)
async def create_translation(payload: TranslationRequest, request: Request):
    """
    接收一个待翻译字符串的列表，将其翻译成一个map并返回。
    """
    if not payload.items:
        # 对于已知的业务逻辑错误，我们仍然可以主动抛出HTTPException
        raise HTTPException(status_code=400, detail="输入的列表不能为空")

    # 从应用状态(request.app.state)中获取共享的http_client并传递给服务层
    client = request.app.state.http_client
    translated_map = await translate_list_to_map(
        payload.source_lang, payload.target_lang, payload.items, client
    )
    return TranslationResponse(translated_map=translated_map)

@router.get("/")
async def root():
    """
    根路径，提供一个简单的欢迎信息和文档链接。
    """
    return {
        "message": "欢迎使用数统模型服务！",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }