# app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Dict

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