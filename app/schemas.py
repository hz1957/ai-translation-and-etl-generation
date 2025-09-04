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
    字段配置模型 (内部使用)
    """
    configId: Optional[int] = Field(None, description="配置ID，用于唯一标识字段配置")
    fieldName: str = Field(..., description="字段名称，对应数据表中的列名")
    fieldLabel: str = Field(..., description="字段标签，字段的中文显示名称")
    fieldType: str = Field(..., description="字段类型，如String、Number、Date等")

class TableInfo(BaseModel):
    """
    表格信息模型 (内部使用)
    """
    tableName: str = Field(..., description="表格名称，用于标识数据表")
    fields: List[Dict[str, Any]] = Field(..., description="字段定义列表，包含字段名称、类型、标签等信息")
    detailData: List[Dict[str, Any]] = Field(..., description="表格详细数据，包含实际的数据记录")

class OriginalData(BaseModel):
    """
    原始数据模型 (内部使用)
    """
    tables: List[TableInfo] = Field(..., description="数据表列表，包含所有需要处理的数据表")
    totalTables: int = Field(..., description="数据表总数")

class StandardTable(BaseModel):
    """
    标准表格定义模型 (内部使用)
    """
    name: str = Field(..., description="标准表名称，如dm、ae等CDASH标准表名")
    description: str = Field(..., description="标准表描述，说明表格的用途和包含的数据类型")
    fields: List[Dict[str, Any]] = Field(..., description="标准字段定义列表，包含字段名、类型、描述等信息")

class LabelVersion(BaseModel):
    """
    标签版本信息模型 (内部使用)
    """
    versionId: str = Field(..., description="版本ID，用于唯一标识标签版本")
    versionName: str = Field(..., description="版本名称，版本的显示名称")
    description: str = Field(..., description="版本描述，说明版本的主要内容和更新")
    createTime: str = Field(..., description="创建时间，格式为ISO 8601")
    tables: List[StandardTable] = Field(..., description="标准表定义列表，包含该版本支持的所有标准表")
    requestTime: Optional[str] = Field(None, description="请求时间，格式为ISO 8601")
    requestType: Optional[str] = Field(None, description="请求类型，标识请求的类型如FIELD_LABEL_MAPPING")

# Request and response models
class SchemaMappingRequest(BaseModel):
    """
    模式映射请求体模型
    """
    originalData: OriginalData = Field(..., description="原始数据，包含需要映射的数据表信息")
    labelVersion: LabelVersion = Field(..., description="标签版本信息，包含标准表定义和版本信息")

    class Config:
        json_schema_extra = {
            "example": {
                "originalData": {
                    "tables": [
                        {
                            "tableName": "SUBJ",
                            "fields": [
                                {"fieldName": "SUBJID", "fieldType": "String", "fieldLabel": "受试者编号"},
                                {"fieldName": "AGE", "fieldType": "Number", "fieldLabel": "年龄"}
                            ],
                            "detailData": [
                                {"SUBJID": "001", "AGE": "25", "rowNumber": 1}
                            ]
                        }
                    ],
                    "totalTables": 1
                },
                "labelVersion": {
                    "versionId": "CDASH_V1_0",
                    "versionName": "CDASH标准标签库v1.0",
                    "description": "CDASH标准数据收集表格v1.0版本",
                    "createTime": "2024-01-01T00:00:00.000Z",
                    "tables": [
                        {
                            "name": "dm",
                            "description": "Demographics: contains information about the subjects",
                            "fields": [
                                {"name": "SUBJID", "type": "string", "description": "What is the subject identifier?"},
                                {"name": "AGE", "type": "integer", "description": "What is the subject's age?"}
                            ]
                        }
                    ]
                }
            }
        }

class TableMapping(BaseModel):
    """
    表格映射结果模型 (内部使用)
    """
    sourceTable: Optional[str] = Field(None, description="源表名称，可为空表示新表")
    targetTable: str = Field(..., description="目标标准表名称")
    mappings: Dict[str, str] = Field(..., description="字段映射关系，key为源字段，value为目标字段")
    confidence: float = Field(..., description="映射置信度，0-1之间的浮点数")
    description: str = Field(..., description="映射描述，说明映射的依据和理由")

class SchemaMappingResponse(BaseModel):
    """
    模式映射响应体模型
    """
    success: bool = Field(..., description="请求是否成功")
    errorMessage: Optional[str] = Field(None, description="错误信息，请求失败时提供详细错误描述")
    standardVersion: Dict[str, Any] = Field(..., description="标准版本信息，包含使用的CDASH标准版本详情")
    tableMappings: List[TableMapping] = Field(..., description="表格映射结果列表，包含所有表的映射关系")
    statistics: Dict[str, Any] = Field(..., description="映射统计信息，包含映射成功率等统计数据")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "errorMessage": None,
                "standardVersion": {
                    "versionId": "CDASH_V1_0",
                    "versionName": "CDASH标准标签库v1.0"
                },
                "tableMappings": [
                    {
                        "sourceTable": "SUBJ",
                        "targetTable": "dm",
                        "mappings": {"SUBJID": "SUBJID", "AGE": "AGE"},
                        "confidence": 0.95,
                        "description": "高置信度映射，字段名称和类型完全匹配"
                    }
                ],
                "statistics": {
                    "totalTables": 1,
                    "mappedTables": 1,
                    "successRate": 1.0
                }
            }
        }