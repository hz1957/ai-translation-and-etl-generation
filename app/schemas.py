# app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class TranslationItem(BaseModel):
    """
    单个翻译任务的模型 (内部使用)
    """
    source_lang: str = Field(..., alias="from", description="源语言代码 (例如 'ZH')")
    target_lang: str = Field(..., alias="to", description="目标语言代码 (例如 'EN')")
    content: str = Field(..., description="需要翻译的文本内容")

class TranslationRequest(BaseModel):
    """
    翻译请求体模型
    """
    source_lang: str = Field(..., alias="from", description="源语言代码 (例如 'ZH')")
    target_lang: str = Field(..., alias="to", description="目标语言代码 (例如 'EN')")
    # 定义输入数据为一个待翻译字符串的列表
    items: List[str] = Field(..., description="需要翻译的文本内容列表")

    class Config:
        # 允许使用 'from' 这样的Python保留关键字作为字段名
        populate_by_name = True
        # 为FastAPI文档提供一个示例
        json_schema_extra = {
            "example": {
                "from": "ZH",
                "to": "EN",
                "items": [
                    "你好世界",
                    "这是一个测试"
                ]
            }
        }

class TranslationResponse(BaseModel):
    """
    翻译响应体模型
    """
    # 输出数据依然是一个map，key是原文，value是译文
    translated_map: Dict[str, str]

    class Config:
        json_schema_extra = {
            "example": {
                "translated_map": {
                    "你好世界": "Hello World",
                    "这是一个测试": "This is a test"
                }
            }
        }

class ErrorDetail(BaseModel):
    """
    标准错误响应体模型
    """
    code: int = Field(..., description="业务错误码或HTTP状态码")
    message: str = Field(..., description="错误的详细信息")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 500,
                "message": "内部服务器错误"
            }
        }

# Data schema mapping models
class FieldConfig(BaseModel):
    """
    字段配置模型
    """
    configId: Optional[int] = Field(None, description="配置ID，可选")
    fieldName: str = Field(..., description="字段名称")
    fieldLabel: str = Field(..., description="字段标签/显示名称")
    fieldType: str = Field(..., description="字段类型")
    fieldLength: Optional[int] = Field(None, description="字段长度，可选")
    sortOrder: Optional[int] = Field(None, description="排序顺序，可选")
    createTime: Optional[str] = Field(None, description="创建时间，可选")

    class Config:
        json_schema_extra = {
            "example": {
                "configId": 1,
                "fieldName": "user_id",
                "fieldLabel": "用户ID",
                "fieldType": "VARCHAR",
                "fieldLength": 50,
                "sortOrder": 1,
                "createTime": "2023-01-01T00:00:00Z"
            }
        }

class Table(BaseModel):
    """
    表格模型
    """
    tableName: str = Field(..., description="表格名称")
    fields: List[Dict[str, Any]] = Field(..., description="字段配置列表")
    detailData: List[Dict[str, Any]] = Field(..., description="详细数据列表")

    class Config:
        json_schema_extra = {
            "example": {
                "tableName": "users",
                "fields": [
                    {
                        "fieldName": "user_id",
                        "fieldType": "VARCHAR",
                        "fieldLength": 50
                    }
                ],
                "detailData": [
                    {
                        "user_id": "001",
                        "user_name": "张三"
                    }
                ]
            }
        }

class SourceData(BaseModel):
    """
    源数据模型
    """
    originalData: Dict[str, Any] = Field(..., description="原始数据字典")
    labelVersion: Dict[str, Any] = Field(..., description="标签版本信息")
    requestTime: Optional[str] = Field(None, description="请求时间，可选")
    requestType: Optional[str] = Field(None, description="请求类型，可选")

    class Config:
        json_schema_extra = {
            "example": {
                "originalData": {
                    "users": [
                        {"id": 1, "name": "张三"},
                        {"id": 2, "name": "李四"}
                    ]
                },
                "labelVersion": {
                    "versionId": "v1.0",
                    "versionName": "版本1.0"
                },
                "requestTime": "2023-01-01T12:00:00Z",
                "requestType": "schema_mapping"
            }
        }

class FieldMapping(BaseModel):
    """
    字段映射模型
    """
    config: FieldConfig = Field(..., description="字段配置信息")
    sampleValues: List[Any] = Field(..., description="样本值列表")
    valueCount: int = Field(..., description="值计数")

    class Config:
        json_schema_extra = {
            "example": {
                "config": {
                    "configId": 1,
                    "fieldName": "user_id",
                    "fieldLabel": "用户ID",
                    "fieldType": "VARCHAR"
                },
                "sampleValues": ["001", "002", "003"],
                "valueCount": 3
            }
        }

class FieldMappings(BaseModel):
    """
    字段映射集合模型
    """
    DOMAIN: FieldMapping = Field(..., description="域字段映射")
    VARIABLE: FieldMapping = Field(..., description="变量字段映射")
    LABEL: FieldMapping = Field(..., description="标签字段映射")
    TYPE: FieldMapping = Field(..., description="类型字段映射")

    class Config:
        json_schema_extra = {
            "example": {
                "DOMAIN": {
                    "config": {
                        "fieldName": "domain",
                        "fieldLabel": "域",
                        "fieldType": "VARCHAR"
                    },
                    "sampleValues": ["USER", "PRODUCT"],
                    "valueCount": 2
                },
                "VARIABLE": {
                    "config": {
                        "fieldName": "variable",
                        "fieldLabel": "变量",
                        "fieldType": "VARCHAR"
                    },
                    "sampleValues": ["ID", "NAME"],
                    "valueCount": 2
                },
                "LABEL": {
                    "config": {
                        "fieldName": "label",
                        "fieldLabel": "标签",
                        "fieldType": "VARCHAR"
                    },
                    "sampleValues": ["用户ID", "姓名"],
                    "valueCount": 2
                },
                "TYPE": {
                    "config": {
                        "fieldName": "type",
                        "fieldLabel": "类型",
                        "fieldType": "VARCHAR"
                    },
                    "sampleValues": ["STRING", "INTEGER"],
                    "valueCount": 2
                }
            }
        }

class LabelVersion(BaseModel):
    """
    标签版本模型
    """
    versionId: Optional[str] = Field(None, description="版本ID，可选")
    versionName: Optional[str] = Field(None, description="版本名称，可选")
    description: Optional[str] = Field(None, description="版本描述，可选")
    createTime: Optional[str] = Field(None, description="创建时间，可选")
    tableConfig: List[FieldConfig] = Field(..., description="表格配置列表")
    fieldMappings: FieldMappings = Field(..., description="字段映射集合")

    class Config:
        json_schema_extra = {
            "example": {
                "versionId": "v1.0",
                "versionName": "版本1.0",
                "description": "用户数据标签版本",
                "createTime": "2023-01-01T00:00:00Z",
                "tableConfig": [
                    {
                        "fieldName": "user_id",
                        "fieldLabel": "用户ID",
                        "fieldType": "VARCHAR",
                        "fieldLength": 50
                    }
                ],
                "fieldMappings": {
                    "DOMAIN": {
                        "config": {
                            "fieldName": "domain",
                            "fieldLabel": "域"
                        },
                        "sampleValues": ["USER"],
                        "valueCount": 1
                    },
                    "VARIABLE": {
                        "config": {
                            "fieldName": "variable",
                            "fieldLabel": "变量"
                        },
                        "sampleValues": ["ID"],
                        "valueCount": 1
                    },
                    "LABEL": {
                        "config": {
                            "fieldName": "label",
                            "fieldLabel": "标签"
                        },
                        "sampleValues": ["用户ID"],
                        "valueCount": 1
                    },
                    "TYPE": {
                        "config": {
                            "fieldName": "type",
                            "fieldLabel": "类型"
                        },
                        "sampleValues": ["STRING"],
                        "valueCount": 1
                    }
                }
            }
        }

class SchemaMappingRequest(BaseModel):
    """
    模式映射请求模型
    """
    source_data: SourceData = Field(..., description="源数据")
    target_schema: Dict[str, Any] = Field(..., description="目标模式字典")

    class Config:
        json_schema_extra = {
            "example": {
                "source_data": {
                    "originalData": {
                        "users": [
                            {"id": 1, "name": "张三"},
                            {"id": 2, "name": "李四"}
                        ]
                    },
                    "labelVersion": {
                        "versionId": "v1.0",
                        "versionName": "版本1.0"
                    },
                    "requestTime": "2023-01-01T12:00:00Z",
                    "requestType": "schema_mapping"
                },
                "target_schema": {
                    "users": {
                        "user_id": {"type": "string"},
                        "user_name": {"type": "string"}
                    }
                }
            }
        }

class TableMapping(BaseModel):
    """
    表格映射模型
    """
    sourceTable: Optional[str] = Field(None, description="源表格名称，可选")
    targetTable: str = Field(..., description="目标表格名称")
    mappings: Dict[str, str] = Field(..., description="字段映射字典")
    confidence: float = Field(..., description="映射置信度")
    description: str = Field(..., description="映射描述")

    class Config:
        json_schema_extra = {
            "example": {
                "sourceTable": "users",
                "targetTable": "user_info",
                "mappings": {
                    "id": "user_id",
                    "name": "user_name"
                },
                "confidence": 0.95,
                "description": "用户表到用户信息表的映射"
            }
        }

class SchemaMappingResponse(BaseModel):
    """
    模式映射响应模型
    """
    success: bool = Field(..., description="映射是否成功")
    errorMessage: Optional[str] = Field(None, description="错误信息，可选")
    standardVersion: Dict[str, Any] = Field(..., description="标准版本信息")
    tableMappings: List[TableMapping] = Field(..., description="表格映射列表")
    statistics: Dict[str, Any] = Field(..., description="统计信息字典")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "errorMessage": None,
                "standardVersion": {
                    "version": "1.0",
                    "name": "数据标准"
                },
                "tableMappings": [
                    {
                        "sourceTable": "users",
                        "targetTable": "user_info",
                        "mappings": {
                            "id": "user_id",
                            "name": "user_name"
                        },
                        "confidence": 0.95,
                        "description": "用户表到用户信息表的映射"
                    }
                ],
                "statistics": {
                    "totalTables": 1,
                    "totalFields": 2,
                    "averageConfidence": 0.95
                }
            }
        }