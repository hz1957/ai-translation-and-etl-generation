from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional, Any
import json
import os
from ..services.data_labeling import map_data_schemas
from ..schemas import (
    SchemaMappingRequest, SchemaMappingResponse
)

router = APIRouter(prefix="/api/data-labeling")

@router.post("/map-schemas", response_model=SchemaMappingResponse)
async def map_schemas_endpoint(request: SchemaMappingRequest):
    """
    使用语义分析将源数据表和字段映射到目标模式
    
    Args:
        request: SchemaMappingRequest 包含源数据和目标模式
        
    Returns:
        SchemaMappingResponse 返回映射结果
    """
    try:
        # 调用 map_data_schemas 函数处理源数据和目标数据
        result = await map_data_schemas(
            source_data=request.model_dump(),
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error mapping data schemas: {str(e)}")