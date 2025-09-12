from fastapi import APIRouter, HTTPException, Body
from app.schemas import ETLResponse, ETLRequest
from app.services.etl_json_service import generate_etl_json

router = APIRouter(prefix="/api/etl-json")

@router.post("/generate", response_model=ETLResponse)
async def generate_etl_json_endpoint(etl_request: ETLRequest):
    """
    生成ETL JSON配置的API端点
    
    Args:
        etl_request: ETL请求配置，包含dataFlowId、etlLib、output、tableList等字段
        
    Returns:
        ETLResponse 返回生成的ETL JSON配置
    """
    try:
        # 调用 ETL JSON 生成服务
        result = await generate_etl_json(request_description=etl_request.model_dump())
        
        # 如果生成失败，返回响应
        if "error" in result:
            raise HTTPException(status_code=500, detail="Operation failed")
        
        return ETLResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Operation failed")