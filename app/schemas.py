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
    targetTable: str = Field(..., description="目标标准表名称")
    sourceTable: Optional[str] = Field(None, description="源表名称，可为空表示新表")
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
                        "targetTable": "dm",
                        "sourceTable": "SUBJ",
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

# class ETLRequest(BaseModel):
#     """
#     ETL JSON生成请求体模型
#     """
#     etlLib: Dict[str, Any] = Field(..., description="输入数据源信息")
#     tableList: List[Dict[str, Any]] = Field(..., description="源表结构列表")
#     recordList: List[Dict[str, Any]] = Field(..., description="记录列表，可为空")
#     dataFlowId: str = Field(..., description="数据流ID")
#     inputParentDirId: str = Field(..., description="输入父目录ID")
#     output: Dict[str, Any] = Field(..., description="输出表配置")
#     task_description: str = Field(..., description="ETL任务描述")

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "etlLib": {
#                     "name": "CDASH 输入数据",
#                     "remark": "CDASH AE, LB, DM, MH 数据集",
#                     "type": "INPUT",
#                     "etlNum": 1
#                 },
#                 "tableList": [
#                     {
#                         "tableNameEn": "CDASH_AE",
#                         "tableNameCn": "不良事件",
#                         "FieldList": [
#                             {"fieldName": "研究中心", "fieldType": "STRING", "fieldLabel": "研究中心"},
#                             {"fieldName": "中心编号", "fieldType": "LONG", "fieldLabel": "中心编号"},
#                             {"fieldName": "受试者", "fieldType": "STRING", "fieldLabel": "受试者"},
#                             {"fieldName": "页面名称", "fieldType": "STRING", "fieldLabel": "页面名称"},
#                             {"fieldName": "记录号", "fieldType": "LONG", "fieldLabel": "记录号"},
#                             {"fieldName": "不良事件名称", "fieldType": "STRING", "fieldLabel": "不良事件名称"},
#                             {"fieldName": "开始日期", "fieldType": "DATE", "fieldLabel": "开始日期"},
#                             {"fieldName": "开始时间", "fieldType": "STRING", "fieldLabel": "开始时间"},
#                             {"fieldName": "结束日期", "fieldType": "DATE", "fieldLabel": "结束日期"},
#                             {"fieldName": "结束时间", "fieldType": "STRING", "fieldLabel": "结束时间"},
#                             {"fieldName": "AE分类", "fieldType": "STRING", "fieldLabel": "AE分类"},
#                             {"fieldName": "是否为严重不良事件", "fieldType": "STRING", "fieldLabel": "是否为严重不良事件"},
#                             {"fieldName": "是否为限制性毒性事件", "fieldType": "STRING", "fieldLabel": "是否为限制性毒性事件"},
#                             {"fieldName": "严重程度（CTCAE）", "fieldType": "STRING", "fieldLabel": "严重程度（CTCAE）"},
#                             {"fieldName": "与研究用药的因果关系", "fieldType": "STRING", "fieldLabel": "与研究用药的因果关系"},
#                             {"fieldName": "是否因严重不良事件退出试验", "fieldType": "STRING", "fieldLabel": "是否因严重不良事件退出试验"},
#                             {"fieldName": "IrAE", "fieldType": "STRING", "fieldLabel": "IrAE"},
#                             {"fieldName": "是否导致药物暂停", "fieldType": "STRING", "fieldLabel": "是否导致药物暂停"},
#                             {"fieldName": "是否导致药物降低剂量", "fieldType": "STRING", "fieldLabel": "是否导致药物降低剂量"},
#                             {"fieldName": "是否导致永久停药", "fieldType": "STRING", "fieldLabel": "是否导致永久停药"}
#                         ]
#                     },
#                     {
#                         "tableNameEn": "CDASH_LB",
#                         "tableNameCn": "实验室检查",
#                         "FieldList": [
#                             {"fieldName": "研究中心", "fieldType": "STRING", "fieldLabel": "研究中心"},
#                             {"fieldName": "中心编号", "fieldType": "LONG", "fieldLabel": "中心编号"},
#                             {"fieldName": "受试者", "fieldType": "STRING", "fieldLabel": "受试者"},
#                             {"fieldName": "访视名称", "fieldType": "STRING", "fieldLabel": "访视名称"},
#                             {"fieldName": "访视OID", "fieldType": "STRING", "fieldLabel": "访视OID"},
#                             {"fieldName": "页面名称", "fieldType": "STRING", "fieldLabel": "页面名称"},
#                             {"fieldName": "记录号", "fieldType": "LONG", "fieldLabel": "记录号"},
#                             {"fieldName": "采样日期", "fieldType": "DATE", "fieldLabel": "采样日期"},
#                             {"fieldName": "检查项目", "fieldType": "STRING", "fieldLabel": "检查项目"},
#                             {"fieldName": "检查结果", "fieldType": "STRING", "fieldLabel": "检查结果"},
#                             {"fieldName": "单位", "fieldType": "STRING", "fieldLabel": "单位"},
#                             {"fieldName": "下限", "fieldType": "DOUBLE", "fieldLabel": "下限"},
#                             {"fieldName": "上限", "fieldType": "DOUBLE", "fieldLabel": "上限"},
#                             {"fieldName": "基线数据", "fieldType": "DOUBLE", "fieldLabel": "基线数据"}
#                         ]
#                     },
#                     {
#                         "tableNameEn": "CDASH_DM",
#                         "tableNameCn": "人口学",
#                         "FieldList": [
#                             {"fieldName": "研究中心", "fieldType": "STRING", "fieldLabel": "研究中心"},
#                             {"fieldName": "中心编号", "fieldType": "LONG", "fieldLabel": "中心编号"},
#                             {"fieldName": "项目", "fieldType": "STRING", "fieldLabel": "项目"},
#                             {"fieldName": "方案编号", "fieldType": "STRING", "fieldLabel": "方案编号"},
#                             {"fieldName": "受试者", "fieldType": "STRING", "fieldLabel": "受试者"},
#                             {"fieldName": "受试者状态", "fieldType": "STRING", "fieldLabel": "受试者状态"},
#                             {"fieldName": "页面名称", "fieldType": "STRING", "fieldLabel": "页面名称"},
#                             {"fieldName": "出生日期", "fieldType": "DATE", "fieldLabel": "出生日期"},
#                             {"fieldName": "年龄", "fieldType": "LONG", "fieldLabel": "年龄"},
#                             {"fieldName": "年龄_UNIT", "fieldType": "STRING", "fieldLabel": "年龄_UNIT"},
#                             {"fieldName": "性别", "fieldType": "STRING", "fieldLabel": "性别"},
#                             {"fieldName": "民族", "fieldType": "STRING", "fieldLabel": "民族"},
#                             {"fieldName": "身高", "fieldType": "LONG", "fieldLabel": "身高"},
#                             {"fieldName": "身高_UNIT", "fieldType": "STRING", "fieldLabel": "身高_UNIT"},
#                             {"fieldName": "WEIGHT", "fieldType": "DOUBLE", "fieldLabel": "WEIGHT"},
#                             {"fieldName": "WEIGHT_UNIT", "fieldType": "STRING", "fieldLabel": "WEIGHT_UNIT"},
#                             {"fieldName": "受试者情况", "fieldType": "STRING", "fieldLabel": "受试者情况"},
#                             {"fieldName": "年龄分组（n, %）", "fieldType": "STRING", "fieldLabel": "年龄分组（n, %）"},
#                             {"fieldName": "AGE-N(Nmiss)", "fieldType": "LONG", "fieldLabel": "AGE-N(Nmiss)"},
#                             {"fieldName": "AGE-Mean±Std", "fieldType": "LONG", "fieldLabel": "AGE-Mean±Std"},
#                             {"fieldName": "AGE-M (Q1~Q3)", "fieldType": "LONG", "fieldLabel": "AGE-M (Q1~Q3)"},
#                             {"fieldName": "AGE-Min~Max", "fieldType": "LONG", "fieldLabel": "AGE-Min~Max"},
#                             {"fieldName": "诊断", "fieldType": "STRING", "fieldLabel": "诊断"},
#                             {"fieldName": "现阶段分期", "fieldType": "STRING", "fieldLabel": "现阶段分期"},
#                             {"fieldName": "ECOG评分", "fieldType": "LONG", "fieldLabel": "ECOG评分"},
#                             {"fieldName": "转移器官数量", "fieldType": "STRING", "fieldLabel": "转移器官数量"},
#                             {"fieldName": "PD-L1表达状态", "fieldType": "STRING", "fieldLabel": "PD-L1表达状态"}
#                         ]
#                     },
#                     {
#                         "tableNameEn": "CDASH_MH",
#                         "tableNameCn": "病史",
#                         "FieldList": [
#                             {"fieldName": "研究中心", "fieldType": "STRING", "fieldLabel": "研究中心"},
#                             {"fieldName": "中心编号", "fieldType": "LONG", "fieldLabel": "中心编号"},
#                             {"fieldName": "受试者", "fieldType": "STRING", "fieldLabel": "受试者"},
#                             {"fieldName": "页面名称", "fieldType": "STRING", "fieldLabel": "页面名称"},
#                             {"fieldName": "记录号", "fieldType": "LONG", "fieldLabel": "记录号"},
#                             {"fieldName": "疾病名称", "fieldType": "STRING", "fieldLabel": "疾病名称"},
#                             {"fieldName": "开始日期", "fieldType": "STRING", "fieldLabel": "开始日期"},
#                             {"fieldName": "结束日期", "fieldType": "DATE", "fieldLabel": "结束日期"},
#                             {"fieldName": "是否持续", "fieldType": "STRING", "fieldLabel": "是否持续"}
#                         ]
#                     }
#                 ],
#                 "recordList": [],
#                 "dataFlowId": "",
#                 "inputParentDirId": "",
#                 "output": {
#                     "id": "",
#                     "name": "CDASH_Standardized",
#                     "type": "TABLE",
#                     "outputDsName": "CDASH_Output",
#                     "outputDsDesc": "AE, LB, DM, MH 整合输出",
#                     "parentDirId": ""
#                 },
#                 "task_description": "请选择合适的input_dataset(table), 生成一个output, 包含受试者, 年龄, 和他的最新的一个不良事件."
#             }
#         }

class ETLResponse(BaseModel):
    """
    ETL JSON生成响应体模型
    """
    uId: Optional[str] = Field(None, description="唯一标识符")
    dataFlowId: str = Field(..., description="数据流ID")
    domId: str = Field(..., description="领域模型ID")
    name: str = Field(..., description="分析名称")
    description: str = Field(..., description="分析描述")
    meta: List[Dict[str, Any]] = Field(..., description="元数据节点列表")
    inputs: List[Dict[str, Any]] = Field(..., description="输入数据源列表")
    outputs: List[Dict[str, Any]] = Field(..., description="输出数据源列表")
    platform: str = Field(..., description="目标平台")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uId": None,
                "dataFlowId": "cdash_analysis_flow_1722166200000",
                "domId": "clinical",
                "name": "CDASH_受试者最新不良事件分析",
                "description": "整合CDASH_DM（人口学）和CDASH_AE（不良事件）数据，获取每位受试者的年龄及其最新的一个不良事件名称",
                "meta": [
                    {
                        "type": "INPUT_DATASET",
                        "name": "CDASH_DM",
                        "id": "input_node_dm",
                        "position": {"x": 100, "y": 100},
                        "sources": [],
                        "inputDsId": "CDASH_DM",
                        "relativeFieldAlias": {
                            "研究中心": "研究中心",
                            "中心编号": "中心编号",
                            "项目": "项目",
                            "方案编号": "方案编号",
                            "受试者": "受试者",
                            "受试者状态": "受试者状态",
                            "页面名称": "页面名称",
                            "出生日期": "出生日期",
                            "年龄": "年龄",
                            "年龄_UNIT": "年龄_UNIT",
                            "性别": "性别",
                            "民族": "民族",
                            "身高": "身高",
                            "身高_UNIT": "身高_UNIT",
                            "WEIGHT": "WEIGHT",
                            "WEIGHT_UNIT": "WEIGHT_UNIT",
                            "受试者情况": "受试者情况",
                            "年龄分组（n, %）": "年龄分组（n, %）",
                            "AGE-N(Nmiss)": "AGE-N(Nmiss)",
                            "AGE-Mean±Std": "AGE-Mean±Std",
                            "AGE-M (Q1~Q3)": "AGE-M (Q1~Q3)",
                            "AGE-Min~Max": "AGE-Min~Max",
                            "诊断": "诊断",
                            "现阶段分期": "现阶段分期",
                            "ECOG评分": "ECOG评分",
                            "转移器官数量": "转移器官数量",
                            "PD-L1表达状态": "PD-L1表达状态"
                        }
                    },
                    {
                        "type": "INPUT_DATASET",
                        "name": "CDASH_AE",
                        "id": "input_node_ae",
                        "position": {"x": 100, "y": 300},
                        "sources": [],
                        "inputDsId": "CDASH_AE",
                        "relativeFieldAlias": {
                            "研究中心": "研究中心",
                            "中心编号": "中心编号",
                            "受试者": "受试者",
                            "页面名称": "页面名称",
                            "记录号": "记录号",
                            "不良事件名称": "不良事件名称",
                            "开始日期": "开始日期",
                            "开始时间": "开始时间",
                            "结束日期": "结束日期",
                            "结束时间": "结束时间",
                            "AE分类": "AE分类",
                            "是否为严重不良事件": "是否为严重不良事件",
                            "是否为限制性毒性事件": "是否为限制性毒性事件",
                            "严重程度（CTCAE）": "严重程度（CTCAE）",
                            "与研究用药的因果关系": "与研究用药的因果关系",
                            "是否因严重不良事件退出试验": "是否因严重不良事件退出试验",
                            "IrAE": "IrAE",
                            "是否导致药物暂停": "是否导致药物暂停",
                            "是否导致药物降低剂量": "是否导致药物降低剂量",
                            "是否导致永久停药": "是否导致永久停药"
                        }
                    },
                    {
                        "type": "CALCULATOR",
                        "name": "添加AE日期排序键",
                        "id": "calc_ae_date_key",
                        "position": {"x": 300, "y": 300},
                        "sources": ["input_node_ae"],
                        "formulas": [
                            {
                                "name": "AE开始时间戳",
                                "type": "TIMESTAMP",
                                "expr": "[开始日期]",
                                "key": "ae_start_timestamp"
                            }
                        ]
                    },
                    {
                        "type": "GROUP_BY",
                        "name": "按受试者分组取最新AE",
                        "id": "group_latest_ae",
                        "position": {"x": 500, "y": 300},
                        "sources": ["calc_ae_date_key"],
                        "zoneData": {
                            "row": [
                                {"name": "受试者", "fdType": "STRING", "metaType": "DIM", "key": "subject_key"}
                            ],
                            "metric": [
                                {"name": "AE开始时间戳", "fdType": "TIMESTAMP", "metaType": "METRIC", "aggrType": "MAX", "key": "max_ae_timestamp"}
                            ]
                        }
                    },
                    {
                        "type": "JOIN_DATA",
                        "name": "关联最新AE记录",
                        "id": "join_latest_ae",
                        "position": {"x": 700, "y": 200},
                        "sources": ["input_node_ae", "group_latest_ae"],
                        "dataFusion": {
                            "fusionType": "COLUMN",
                            "dataSources": [
                                {"key": "input_node_ae"},
                                {"key": "group_latest_ae"}
                            ],
                            "columnFuses": [
                                {
                                    "leftKey": "input_node_ae",
                                    "rightKey": "group_latest_ae",
                                    "joinType": "INNER",
                                    "predicates": [
                                        {"leftColumn": "受试者", "rightColumn": "受试者"},
                                        {"leftColumn": "AE开始时间戳", "rightColumn": "AE开始时间戳"}
                                    ]
                                }
                            ],
                            "selectedColumns": [
                                {"name": "受试者", "dsKey": "input_node_ae", "isIgnored": False},
                                {"name": "不良事件名称", "dsKey": "input_node_ae", "isIgnored": False}
                            ]
                        }
                    },
                    {
                        "type": "SELECT_COLUMNS",
                        "name": "选择受试者年龄",
                        "id": "select_columns_dm",
                        "position": {"x": 300, "y": 100},
                        "sources": ["input_node_dm"],
                        "columns": [
                            {"name": "受试者", "dsKey": "input_node_dm", "isIgnored": False},
                            {"name": "年龄", "dsKey": "input_node_dm", "isIgnored": False}
                        ]
                    },
                    {
                        "type": "JOIN_DATA",
                        "name": "合并年龄与最新AE",
                        "id": "final_join",
                        "position": {"x": 900, "y": 200},
                        "sources": ["select_columns_dm", "join_latest_ae"],
                        "dataFusion": {
                            "fusionType": "COLUMN",
                            "dataSources": [
                                {"key": "select_columns_dm"},
                                {"key": "join_latest_ae"}
                            ],
                            "columnFuses": [
                                {
                                    "leftKey": "select_columns_dm",
                                    "rightKey": "join_latest_ae",
                                    "joinType": "INNER",
                                    "predicates": [
                                        {"leftColumn": "受试者", "rightColumn": "受试者"}
                                    ]
                                }
                            ],
                            "selectedColumns": [
                                {"name": "受试者", "dsKey": "select_columns_dm", "isIgnored": False},
                                {"name": "年龄", "dsKey": "select_columns_dm", "isIgnored": False},
                                {"name": "不良事件名称", "dsKey": "join_latest_ae", "isIgnored": False}
                            ]
                        }
                    },
                    {
                        "type": "OUTPUT_DATASET",
                        "name": "CDASH_Standardized",
                        "id": "output_node_001",
                        "position": {"x": 1100, "y": 200},
                        "sources": ["final_join"],
                        "outputDsName": "CDASH_Output",
                        "dataSource": {
                            "dsId": "CDASH_Output",
                            "name": "CDASH_Standardized",
                            "created": True,
                            "parentDirId": "dir_clinical_output",
                            "parentDirName": "临床分析输出"
                        }
                    }
                ],
                "inputs": [
                    {
                        "dsId": "CDASH_DM",
                        "name": "CDASH_DM",
                        "fields": [
                            {"name": "研究中心", "type": "STRING", "seqNo": 0},
                            {"name": "中心编号", "type": "LONG", "seqNo": 1},
                            {"name": "项目", "type": "STRING", "seqNo": 2},
                            {"name": "方案编号", "type": "STRING", "seqNo": 3},
                            {"name": "受试者", "type": "STRING", "seqNo": 4},
                            {"name": "受试者状态", "type": "STRING", "seqNo": 5},
                            {"name": "页面名称", "type": "STRING", "seqNo": 6},
                            {"name": "出生日期", "type": "DATE", "seqNo": 7},
                            {"name": "年龄", "type": "LONG", "seqNo": 8},
                            {"name": "年龄_UNIT", "type": "STRING", "seqNo": 9},
                            {"name": "性别", "type": "STRING", "seqNo": 10},
                            {"name": "民族", "type": "STRING", "seqNo": 11},
                            {"name": "身高", "type": "LONG", "seqNo": 12},
                            {"name": "身高_UNIT", "type": "STRING", "seqNo": 13},
                            {"name": "WEIGHT", "type": "DOUBLE", "seqNo": 14},
                            {"name": "WEIGHT_UNIT", "type": "STRING", "seqNo": 15},
                            {"name": "受试者情况", "type": "STRING", "seqNo": 16},
                            {"name": "年龄分组（n, %）", "type": "STRING", "seqNo": 17},
                            {"name": "AGE-N(Nmiss)", "type": "LONG", "seqNo": 18},
                            {"name": "AGE-Mean±Std", "type": "LONG", "seqNo": 19},
                            {"name": "AGE-M (Q1~Q3)", "type": "LONG", "seqNo": 20},
                            {"name": "AGE-Min~Max", "type": "LONG", "seqNo": 21},
                            {"name": "诊断", "type": "STRING", "seqNo": 22},
                            {"name": "现阶段分期", "type": "STRING", "seqNo": 23},
                            {"name": "ECOG评分", "type": "LONG", "seqNo": 24},
                            {"name": "转移器官数量", "type": "STRING", "seqNo": 25},
                            {"name": "PD-L1表达状态", "type": "STRING", "seqNo": 26}
                        ]
                    },
                    {
                        "dsId": "CDASH_AE",
                        "name": "CDASH_AE",
                        "fields": [
                            {"name": "研究中心", "type": "STRING", "seqNo": 0},
                            {"name": "中心编号", "type": "LONG", "seqNo": 1},
                            {"name": "受试者", "type": "STRING", "seqNo": 2},
                            {"name": "页面名称", "type": "STRING", "seqNo": 3},
                            {"name": "记录号", "type": "LONG", "seqNo": 4},
                            {"name": "不良事件名称", "type": "STRING", "seqNo": 5},
                            {"name": "开始日期", "type": "DATE", "seqNo": 6},
                            {"name": "开始时间", "type": "STRING", "seqNo": 7},
                            {"name": "结束日期", "type": "DATE", "seqNo": 8},
                            {"name": "结束时间", "type": "STRING", "seqNo": 9},
                            {"name": "AE分类", "type": "STRING", "seqNo": 10},
                            {"name": "是否为严重不良事件", "type": "STRING", "seqNo": 11},
                            {"name": "是否为限制性毒性事件", "type": "STRING", "seqNo": 12},
                            {"name": "严重程度（CTCAE）", "type": "STRING", "seqNo": 13},
                            {"name": "与研究用药的因果关系", "type": "STRING", "seqNo": 14},
                            {"name": "是否因严重不良事件退出试验", "type": "STRING", "seqNo": 15},
                            {"name": "IrAE", "type": "STRING", "seqNo": 16},
                            {"name": "是否导致药物暂停", "type": "STRING", "seqNo": 17},
                            {"name": "是否导致药物降低剂量", "type": "STRING", "seqNo": 18},
                            {"name": "是否导致永久停药", "type": "STRING", "seqNo": 19}
                        ]
                    }
                ],
                "outputs": [
                    {
                        "dsId": "CDASH_Output",
                        "name": "CDASH_Standardized",
                        "created": True,
                        "parentDirId": "dir_clinical_output",
                        "parentDirName": "临床分析输出"
                    }
                ],
                "platform": "bi"
            }
        }