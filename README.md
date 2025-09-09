# 数统模型服务

供数统服务调用的模型服务

## ✨ 功能特性

- **灵活的List到Map翻译**: 接收一个包含源语言、目标语言和内容的JSON对象数组，返回一个JSON对象（Map）。
- **多环境配置**: 支持 `dev` (开发) 和 `prod` (生产) 环境，使用不同的 `.env` 文件进行配置。
- **大模型驱动**: 核心翻译逻辑由可配置的大语言模型API驱动。
- **自动分片**: 自动将超过上下文长度的列表切分成小块进行处理。
- **Docker就绪**: 提供优化的 `Dockerfile`，支持一键容器化部署。
- **交互式文档**: 自动生成Swagger UI和ReDoc API文档。

## 🚀 环境配置与运行

### 1. 环境准备

- Python 3.8+
- Node.js 16+ (for Playwright)
- Docker (用于生产部署)
- make (用于运行构建命令)

### 2. 配置文件

本项目通过环境变量 `APP_ENV` 来区分加载不同的配置文件。

- `APP_ENV=dev` (默认): 加载 `.env.dev`
- `APP_ENV=prod`: 加载 `.env.prod`

**a. 开发环境配置**

复制 `.env.example` 文件到 `.env.dev`:
```bash
cp .env.example .env.dev
```
然后编辑 `.env.dev`，填入您的开发环境配置。

**b. 生产环境配置**

在生产服务器上，创建一个 `.env.prod` 文件，并填入生产环境的配置。
**注意**: 生产环境的密钥等敏感信息，推荐通过部署系统的环境变量或Secrets进行管理，而不是直接写入文件。

### 3. 本地开发

**a. 安装依赖**
```bash
pip install -r requirements.txt
```

**b. 启动服务**

使用我们提供的启动脚本，它会自动设置 `APP_ENV=dev`。
```bash
python run.py
```
服务将以开发模式启动在 `http://127.0.0.1:5432`，并开启代码自动重载。

### 2. 使用 Makefile 管理项目
本项目使用 Makefile 简化常用命令。安装 make 工具后，可以使用以下命令：

**a. 设置开发环境**
```bash
make setup
```

**b. 启动开发服务器**
```bash
make dev
```

**c. 运行测试**
```bash
make test
```

**d. 清理缓存**
```bash
make clean
```

**e. 构建 Docker 镜像**
```bash
make docker-build
```

**f. 查看所有可用命令**
```bash
make help
```

### 4. 生产部署 (使用 Docker 可选)

**a. 构建 Docker 镜像**

`Dockerfile` 内部已设置 `ENV APP_ENV=prod`，因此构建的镜像默认为生产环境。
```bash
docker build -t model-platform .
```

**b. 运行 Docker 容器**

在您的服务器上，确保 `.env.prod` 文件已准备好，然后运行容器：
```bash
docker run -d --name translate-service -p 5432:5432 --env-file .env.prod model-platform
```
- `--env-file .env.prod`: 将生产环境的配置文件加载到容器中。

## API 使用示例

您可以使用 `cURL` 或访问 `http://127.0.0.1:5432/docs` 来测试API。

### 1. 翻译 API

```bash
curl -X 'POST' \
  'http://127.0.0.1:5432/api/translate/translate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "from": "ZH",
    "to": "EN",
    "items": [
        "你好世界",
        "这是一个测试"
    ]
}'
```

**预期响应:**
```json
{
    "translated_map": {
        "你好世界": "Hello World",
        "这是一个测试": "This is a test"
    }
}
```

### 2. 数据标注 API

```bash
curl -X 'POST' \
  'http://127.0.0.1:5432/api/data-labeling/map-schemas' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
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
            {"name": "AGE", "type": "integer", "description": "What is the subject'"'"'s age?"}
          ]
        }
      ]
    }
  }'
```

**预期响应:**
```json
{
  "success": true,
  "errorMessage": null,
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
```

### 3. ETL JSON 生成 API

```bash
curl -X 'POST' \
  'http://127.0.0.1:5432/api/etl-json/generate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '请帮我生成一个 ETL 配置：输入数据：CDASH_AE（不良事件数据）和CDASH_DM（受试者数据），输出要求：找到受试者最新的一个不良事件，生成包含受试者、年龄和最新不良事件的输出'
```

**预期响应:**
```json
{
  "uId": null,
  "dataFlowId": "cdash_analysis_flow_1722166200000",
  "domId": "clinical",
  "name": "CDASH_受试者最新不良事件分析",
  "description": "整合CDASH_DM（人口学）和CDASH_AE（不良事件）数据，获取每位受试者的年龄及其最新的一个不良事件名称",
  "meta": [...],
  "inputs": [...],
  "outputs": [...],
  "platform": "bi"
}
```