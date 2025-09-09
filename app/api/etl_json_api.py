from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from app.schemas import ETLResponse
from app.services.etl_json_service import generate_etl_json
from app.api.data_labeling_api import router as data_labeling_router

router = APIRouter(prefix="/api/etl-json")

@router.post("/generate", response_model=ETLResponse)
async def generate_etl_json_endpoint(task_description: Any = Body(..., description="ETL任务描述，可以是字符串或JSON对象")):
    """
    生成ETL JSON配置的API端点
    
    Args:
        task_description: ETL任务描述，可以是字符串或JSON对象
        
    Returns:
        ETLResponse 返回生成的ETL JSON配置
    """
    try:
        # 调用 ETL JSON 生成服务
        result = await generate_etl_json(task_description=task_description)
        
        # 如果生成失败，返回响应
        if "error" in result:
            raise HTTPException(status_code=500, detail="Operation failed")
        
        return ETLResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Operation failed")