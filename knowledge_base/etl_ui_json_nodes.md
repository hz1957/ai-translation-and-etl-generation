# ETL JSON 节点说明文档

本文档详细说明了ETL配置JSON文件中各种节点类型的结构、参数和使用方法，帮助用户理解和解读ETL数据流配置。

## 1. 文档结构概览

JSON 配置文件是数据转换流程的完整描述，包含以下顶级属性：
- uId、dataFlowId、domId、name：流程标识信息
- meta：节点配置数组，是整个配置的核心
- inputs：输入数据源定义数组
- outputs：输出数据源定义数组
- platform：固定值"bi"

每个ETL JSON文件的基本结构如下：

```json
{
  "uId": null,
  "dataFlowId": "唯一标识符",
  "domId": "域标识",
  "name": "数据流名称",
  "description": "描述信息",
  "meta": [
    // 节点配置数组
  ]
}
```

## 2. 节点类型详解

### 2.1 INPUT_DATASET（输入数据集）
**功能**: 定义数据流的输入源，从其他数据表或外部系统读取数据

**主要参数**:
```json
{
  "type": "INPUT_DATASET",
  "name": "数据集名称",
  "displayType": "DATAFLOW",
  "inputDsId": "数据集ID",
  "cascadeUpdateEnabled": true/false,
  "relativeFieldAlias": {
    "原字段名": "别名"
  },
  "position": {"x": 100, "y": 200}
}
```

**使用场景**: 
- 从ODS层读取原始数据
- 从DWD层读取已处理的事实表数据
- 引用维度表进行关联

**示例**:
```json
{
  "type": "INPUT_DATASET",
  "name": "ODS_CALENDAR",
  "displayType": "DATAFLOW",
  "inputDsId": "j3bab2a350f624feeb7eeca3",
  "cascadeUpdateEnabled": true,
  "relativeFieldAlias": {
    "da47c1fd60a0c4fc1baa2cc8": "finance_year",
    "g8d8eac26f6cd46f0b7c534b": "month_EN"
  }
}
```

### 2.2 CALCULATOR（计算器）
**功能**: 通过表达式创建新字段（只允许单独使用一种运算，如排序函数，窗口函数，数学运算）

**主要参数**:
```json
{
  "type": "CALCULATOR",
  "name": "计算器名称",
  "formulas": [
    {
      "name": "新字段名",
      "type": "数据类型",
      "expr": "计算表达式",
      "key": "唯一标识"
    }
  ]
}
```

**计算表达式类型**:
- 简单赋值: `[原字段名]`
- 数学运算: `[字段1] + [字段2]`
- 条件判断: `case when [条件] then [值1] else [值2] end`
- 字符串操作: `concat([字段1], [字段2])`
- 日期函数: `now()`, `DATE_SUB(now(),7)`
- 窗口函数: `sum([字段]) OVER (PARTITION BY [分组字段])`
- 排序函数: `row_number() over(order by [字段] desc)`

**使用场景**:
- 排序场景：给用户、订单等记录生成排名（如销售额排名、活跃度排名）
- 日期计算（如计算近 7 天活跃数、账龄天数）
- 利用窗口函数计算累计值、排名、同比环比等分析指标
- 在事实表中增加派生指标（如利润 = 收入 - 成本）
- 按条件生成标识字段（如是否为活跃用户）
- 拼接字符串或生成唯一编码（如 concat([地区], [用户ID])）


**示例**:
```json
{
  "type": "CALCULATOR",
  "name": "DP",
  "formulas": [
    {
      "name": "DP_Rank",
      "type": "INT",
      "expr": "row_number() over(order by [Sell-in History CY Amt] desc)",
      "key": "ZcfeRyyfSi"
    },
    {
      "name": "GMV_Value",
      "type": "DOUBLE",
      "expr": "case when [Major_Inventory_Type]='Saleable' and [BT] in('90','88') and [Free Units]<[SI Units] then [Free Units]*[RSP] else 0 end",
      "key": "u3UXq7uVQOMFKrLlYjzTD9dS"
    }
  ]
}
```

### 2.3 SELECT_COLUMNS（选择列）
**功能**: 选择需要的字段并可重命名

**主要参数**:
```json
{
  "type": "SELECT_COLUMNS",
  "name": "选择列",
  "columns": [
    {
      "name": "字段名",
      "dsKey": "源节点ID",
      "newName": "新字段名（可选）",
      "isIgnored": false
    }
  ]
}
```

**使用场景**:
- 过滤不需要的字段
- 重命名字段以符合命名规范
- 调整字段顺序

**示例**:
```json
{
  "type": "SELECT_COLUMNS",
  "name": "选择列",
  "columns": [
    {
      "name": "Material",
      "dsKey": "id_1719288760266",
      "isIgnored": false
    },
    {
      "name": "ABCD",
      "dsKey": "id_1719288760266",
      "newName": "ABCD_Status",
      "isIgnored": false
    }
  ]
}
```

### 2.4 FILTER_ROWS（筛选数据行）
**功能**: 根据条件过滤数据行

**主要参数**:
```json
{
  "type": "FILTER_ROWS",
  "name": "筛选数据行",
  "conditions": [
    {
      "name": "字段名",
      "fdType": "字段类型",
      "filterType": "过滤类型",
      "filterValue": [{"v": "值", "type": "VALUE/COLUMN"}]
    }
  ],
  "combineType": "AND/OR"
}
```

**过滤类型**:
- `EQ`: 等于
- `NE`: 不等于
- `GT`: 大于
- `GE`: 大于等于
- `LT`: 小于
- `LE`: 小于等于
- `IN`: 包含于
- `NOT_IN`: 不包含于

**示例**:
```json
{
  "type": "FILTER_ROWS",
  "conditions": [
    {
      "name": "YYMM",
      "fdType": "DOUBLE",
      "filterType": "GE",
      "filterValue": [{"v": "2211", "type": "VALUE"}]
    }
  ],
  "combineType": "AND"
}
```

### 2.5 GROUP_BY（分组聚合）
**功能**: 对数据进行分组并计算聚合值

**主要参数**:
```json
{
  "type": "GROUP_BY",
  "name": "分组聚合",
  "zoneData": {
    "row": [
      {
        "name": "分组字段",
        "fdType": "字段类型",
        "metaType": "DIM",
        "key": "唯一标识"
      }
    ],
    "metric": [
      {
        "name": "聚合字段",
        "fdType": "字段类型",
        "metaType": "METRIC",
        "aggrType": "聚合类型",
        "key": "唯一标识"
      }
    ]
  }
}
```

**聚合类型**:
- `SUM`: 求和
- `CNT`: 计数
- `CNT_DISTINCT`: 去重计数
- `AVG`: 平均值
- `MAX`: 最大值
- `MIN`: 最小值
- `NUL`: 不聚合（维度字段）

### 2.6 APPEND_ROWS（合并行数据）
**功能**: 将多个相同结构的数据集合并

**主要参数**: 
```json 
{                                                                                          
  "type": "APPEND_ROWS",                                                                   
  "name": "追加行",                                                                        
  "sources": ["源节点ID1", "源节点ID2"]                                                   
}    
``` 
**使用场景**: 
- 合并结构相同的数据源
- 数据纵向拼接 
- 多个结果集合并


### 2.7 JOIN_DATA（数据关联）
**功能**: 执行数据表之间的关联操作

**主要参数**:   
```json
{
  "type": "JOIN_DATA",
  "name": "关联数据",
  "dataFusion": {
    "dataSources": [
      {"key": "源节点ID1"},
      {"key": "源节点ID2"}
    ],
    "fusionType": "COLUMN",
    "columnFuses": [
      {
        "leftKey": "左表节点ID",
        "rightKey": "右表节点ID",
        "joinType": "关联类型",
        "predicates": [
          {
            "leftColumn": "左表字段",
            "rightColumn": "右表字段"
          }
        ]
      }
    ],
    "selectedColumns": [
      {
        "name": "字段名",
        "dsKey": "源节点ID",
        "newName": "新字段名（可选）",
        "isIgnored": false
      }
    ]
  }
}
```
**关联类型**:
- `INNER`: 内连接  
- `LEFT_OUTER`: 左外连接   
- `RIGHT_OUTER`: 右外连接 
- `OUTER`: 全连接 

**适用场景**:
- 多表关联查询
- 数据整合
- 宽表构建
- 跨数据源数据合并

**示例**:
```json
{
  "type": "JOIN_DATA",
  "name": "关联数据",
  "dataFusion": {
    "dataSources": [
      {
        "key": "id_1513330739473"
      },
      {
        "key": "id_1513330756210"
      }
    ],
    "fusionType": "COLUMN",
    "columnFuses": [
      {
        "leftKey": "id_1513330739473",
        "rightKey": "id_1513330756210",
        "joinType": "INNER",
        "predicates": [
          {
            "leftColumn": "品牌",
            "rightColumn": "品牌"
          }
        ]
      }
    ],
    "selectedColumns": [
      {
        "name": "品牌",
        "dsKey": "id_1513330739473",
        "isIgnored": false
      },
      {
        "name": "优惠券领取量",
        "dsKey": "id_1513330756210",
        "isIgnored": false
      }
    ]
  }
}
```

### 2.8 OUTPUT_DATASET（输出数据集）
**功能**: 定义数据流的输出目标

**主要参数**:
```json
{
  "type": "OUTPUT_DATASET",
  "name": "输出数据集名称",
  "outputDsName": "目标表名",
  "parentDirId": "父目录ID",
  "dataSource": {
    "created": true,
    "dsId": "数据集ID",
    "name": "数据集名称",
    "dirPath": [{"dirId": "目录ID", "dirName": "目录名称"}]
  },
  "position": {"x": 100, "y": 200}     
}
```

### 2.9 实例展示
```json
{
  "uId": null,
  "dataFlowId": "corrected_flow_1722165600000",
  "domId": "guanbi",
  "name": "资源统计分析流程_完全修正版",
  "parentDirId": null,
  "triggerType": null,
  "cron": null,
  "executionCount": null,
  "executionSuccessCount": null,
  "lastExecution": null,
  "lastExecuteTime": null,
  "displayType": null,
  "status": null,
  "utime": null,
  "ctime": null,
  "version": null,
  "description": "完全修正版：对资源数据进行筛选、计算和按月份统计分析，生成资源类型的月度汇总报表（已修复所有字段引用问题）",
  "annotation": {"list": [], "hidden": false},
  "fuseConfig": null,
  "id": "corrected_flow_1722165600000",
  "meta": [
    {
      "type": "INPUT_DATASET",
      "name": "test123",
      "displayType": "DATAFLOW",
      "preview": {"scope": "ALL", "config": {}},
      "cascadeUpdateEnabled": false,
      "inputDsId": "n0be575c3edbf47c2b90a700",
      "id": "input_node_001",
      "relativeFieldAlias": {
        "lea8404a9a1074c8ba3a9c07": "创建者id",
        "x85bf7538c4af4d17b815c97": "域",
        "g75760eb10e314438bb388a3": "文件夹名称",
        "f0305256edf1d402a94595d6": "创建时间",
        "k1885293ab3204f99afcea2a": "父文件夹id",
        "wf63910974c9f4b578185b20": "测试",
        "lbdfe435113c04cd493f9c0d": "资源类型",
        "ndc8ecad73a954976b99c814": "最近修改时间",
        "ve4e9bf9c21f04afc8eada0e": "文件夹id"
      },
      "position": {"x": 100, "y": 100},
      "sources": []
    },
    {
      "type": "CALCULATOR",
      "name": "添加计算字段",
      "id": "calc_node_001",
      "formulas": [
        {
          "name": "创建月份",
          "type": "STRING",
          "expr": "substr([创建时间], 1, 7)",
          "key": "create_month_key"
        },
        {
          "name": "资源数量",
          "type": "INT",
          "expr": "1",
          "key": "resource_count_key"
        }
      ],
      "position": {"x": 300, "y": 100},
      "sources": ["input_node_001"]
    },
    {
      "type": "FILTER_ROWS",
      "name": "筛选有效资源",
      "id": "filter_node_001",
      "conditions": [
        {
          "name": "资源类型",
          "fdType": "STRING",
          "filterType": "NE",
          "filterValue": [{"v": "", "type": "VALUE"}]
        }
      ],
      "combineType": "AND",
      "position": {"x": 500, "y": 100},
      "sources": ["calc_node_001"]
    },
    {
      "type": "GROUP_BY",
      "name": "按月份和资源类型统计",
      "id": "group_node_001",
      "zoneData": {
        "row": [
          {
            "name": "创建月份",
            "fdType": "STRING",
            "metaType": "DIM",
            "key": "month_dim_key"
          },
          {
            "name": "资源类型",
            "fdType": "STRING",
            "metaType": "DIM",
            "key": "type_dim_key"
          },
          {
            "name": "域",
            "fdType": "STRING",
            "metaType": "DIM",
            "key": "domain_dim_key"
          }
        ],
        "metric": [
          {
            "name": "资源数量",
            "fdType": "INT",
            "metaType": "METRIC",
            "aggrType": "SUM",
            "key": "count_metric_key"
          }
        ]
      },
      "position": {"x": 700, "y": 100},
      "sources": ["filter_node_001"]
    },
    {
      "type": "SELECT_COLUMNS",
      "name": "选择输出字段",
      "id": "select_node_001",
      "columns": [
        {"name": "创建月份", "dsKey": "group_node_001", "isIgnored": false},
        {"name": "资源类型", "dsKey": "group_node_001", "isIgnored": false},
        {"name": "域", "dsKey": "group_node_001", "newName": "业务域", "isIgnored": false},
        {"name": "资源数量", "dsKey": "group_node_001", "isIgnored": false}
      ],
      "position": {"x": 900, "y": 100},
      "sources": ["group_node_001"]
    },
    {
      "type": "OUTPUT_DATASET",
      "name": "资源统计报表",
      "id": "output_node_001",
      "outputDsName": "资源统计月报_完全修正版",
      "parentDirId": "test_folder_id",
      "dataSource": {
        "created": true,
        "dsId": "corrected_output_ds_id",
        "name": "资源统计月报_完全修正版",
        "dirPath": ["根目录", "测试", "统计报表"]
      },
      "position": {"x": 1100, "y": 100},
      "sources": ["select_node_001"]
    }
  ],
  "inputs": [
    {
      "dsId": "n0be575c3edbf47c2b90a700",
      "name": "test123",
      "fields": [
        {"name": "文件夹id", "type": "STRING", "seqNo": 0},
        {"name": "文件夹名称", "type": "STRING", "seqNo": 1},
        {"name": "域", "type": "STRING", "seqNo": 2},
        {"name": "创建者id", "type": "STRING", "seqNo": 3},
        {"name": "父文件夹id", "type": "STRING", "seqNo": 4},
        {"name": "创建时间", "type": "TIMESTAMP", "seqNo": 5},
        {"name": "最近修改时间", "type": "TIMESTAMP", "seqNo": 6},
        {"name": "资源类型", "type": "STRING", "seqNo": 7},
        {"name": "测试", "type": "STRING", "seqNo": 8}
      ]
    }
  ],
  "outputs": [],
  "platform": "bi"
}
```

## 3. 数据类型说明

### 基础数据类型
- `STRING`: 字符串类型
- `DOUBLE`: 双精度浮点数
- `LONG`: 长整型
- `DATE`: 日期类型
- `TIMESTAMP`: 时间戳类型
- `INT`: 整型
- `DECIMAL`: 精确小数类型

## 4. 节点连接关系

### sources 参数
每个节点的 `sources` 数组定义了其输入来源，通过节点ID建立数据流向关系。

### position 参数
定义节点在可视化界面中的位置坐标：
```json
"position": {"x": 100, "y": 200}
```

## 5. 常见业务模式

### 5.1 数据清洗模式
INPUT_DATASET → FILTER_ROWS → SELECT_COLUMNS → OUTPUT_DATASET

### 5.2 数据计算模式
INPUT_DATASET → CALCULATOR → SQL_SCRIPT → OUTPUT_DATASET

### 5.3 数据关联模式
多个INPUT_DATASET → SQL_SCRIPT（含JOIN） → SELECT_COLUMNS → OUTPUT_DATASET

### 5.4 数据聚合模式
INPUT_DATASET → GROUP_BY → CALCULATOR → OUTPUT_DATASET

## 6. 最佳实践

1. **命名规范**: 使用有意义的节点名称，体现业务含义
2. **注释完整**: 在SQL脚本中添加中文注释说明业务逻辑
3. **字段别名**: 为复杂表达式设置清晰的字段别名
4. **数据类型**: 明确指定字段的数据类型
5. **性能优化**: 在必要的地方添加过滤条件减少数据量

## 7. 故障排查

### 常见问题
1. **sqlStatus为invalid**: 检查SQL语法和字段引用
2. **字段找不到**: 确认sources中的节点ID正确
3. **数据类型不匹配**: 检查计算表达式中的类型转换
4. **循环依赖**: 确保节点间的依赖关系是有向无环图

### 调试建议
1. 逐步验证每个节点的输出结果
2. 检查字段映射关系是否正确
3. 确认数据源表的字段结构
4. 验证业务逻辑的准确性

通过本文档，用户可以全面理解ETL JSON配置文件的结构和各节点的功能，从而更好地设计和维护数据处理流程。