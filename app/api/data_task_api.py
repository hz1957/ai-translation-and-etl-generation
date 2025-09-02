from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import os
from tasks.data_task import map_data_schemas

app = FastAPI(title="Data Schema Mapping API", description="API for mapping source data schemas to target schemas using semantic analysis")

# Pydantic models based on source_data_case.json structure
class FieldConfig(BaseModel):
    configId: Optional[int] = None
    fieldName: str
    fieldLabel: str
    fieldType: str
    fieldLength: Optional[int] = None
    sortOrder: Optional[int] = None
    createTime: Optional[str] = None

class Table(BaseModel):
    tableName: str
    fields: List[Dict[str, Any]]
    detailData: List[Dict[str, Any]]

class SourceData(BaseModel):
    originalData: Dict[str, Any]
    labelVersion: Dict[str, Any]
    requestTime: Optional[str] = None
    requestType: Optional[str] = None

class FieldMapping(BaseModel):
    config: FieldConfig
    sampleValues: List[Any]
    valueCount: int

class FieldMappings(BaseModel):
    DOMAIN: FieldMapping
    VARIABLE: FieldMapping
    LABEL: FieldMapping
    TYPE: FieldMapping

class LabelVersion(BaseModel):
    versionId: Optional[str] = None
    versionName: Optional[str] = None
    description: Optional[str] = None
    createTime: Optional[str] = None
    tableConfig: List[FieldConfig]
    fieldMappings: FieldMappings

# Request and response models
class SchemaMappingRequest(BaseModel):
    source_data: SourceData
    target_schema: Dict[str, Any]

class TableMapping(BaseModel):
    sourceTable: Optional[str] = None
    targetTable: str
    mappings: Dict[str, str]
    confidence: float
    description: str

class SchemaMappingResponse(BaseModel):
    success: bool
    errorMessage: Optional[str] = None
    standardVersion: Dict[str, Any]
    tableMappings: List[TableMapping]
    statistics: Dict[str, Any]

@app.post("/map-schemas", response_model=SchemaMappingResponse)
async def map_schemas_endpoint(request: SchemaMappingRequest):
    """
    Map source data tables and fields to target schema using semantic analysis.
    
    Args:
        request: SchemaMappingRequest containing source_data and target_schema_path
        
    Returns:
        SchemaMappingResponse with the mapping results
    """
    try:
        # Call the map_data_schemas function with the provided source and target data
        result = await map_data_schemas(
            source_data=request.source_data.dict(),
            target_schema=request.target_schema
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error mapping data schemas: {str(e)}")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)