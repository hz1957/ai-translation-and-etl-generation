#!/usr/bin/env python3
"""
ETL JSON Generation Service
"""
import asyncio
import sys
import os
import json
import re
import logging
from autogen_agentchat.messages import TextMessage
from typing import Any, Dict, Optional
import json
# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.etl_team import get_team, select_datasets
from app.config.logging import configure_logging

# 配置日志
configure_logging()
logger = logging.getLogger(__name__)

# 团队实例连接池
_team_pool = []
# 池中最大团队实例数
_MAX_POOL_SIZE = 3
# 用于团队实例池的锁
_pool_lock = asyncio.Lock()

def _extract_json_from_content(content) -> Optional[str]:
    """从消息内容中提取JSON字符串"""
    # 如果content是列表，尝试找到包含JSON的字符串
    if isinstance(content, list):
        for item in content:
            if isinstance(item, str):
                json_content = _extract_json_from_content(item)
                if json_content:
                    return json_content
        return None
    
    # 确保content是字符串
    if not isinstance(content, str):
        return None
    
    # 查找JSON代码块
    json_pattern = r'```json\s*(.*?)\s*```'
    matches = re.findall(json_pattern, content, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    # 如果没有代码块，尝试直接解析JSON
    try:
        json.loads(content)
        return content.strip()
    except json.JSONDecodeError:
        return None


async def _get_team():
    """获取ETL团队实例（连接池模式）"""
    global _team_pool
    async with _pool_lock:
        # 如果池中有可用实例，返回一个
        if _team_pool:
            team = _team_pool.pop()
            logger.info(f"从连接池获取团队实例，当前池大小: {len(_team_pool)}")
            return team
    
    # 创建新实例
    team = await get_team()
    logger.info(f"创建新的团队实例，当前池大小: {len(_team_pool)}")
    return team


async def _return_team(team):
    """将团队实例返回到连接池"""
    global _team_pool
    async with _pool_lock:
        if len(_team_pool) < _MAX_POOL_SIZE:
            _team_pool.append(team)
            logger.info(f"团队实例返回连接池，当前池大小: {len(_team_pool)}")
        else:
            logger.info("团队实例连接池已满，丢弃实例")


def _transform_request_to_ideal(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform request format to ideal format
    
    Args:
        request_data: Data in request format (with dataFlowId, etlLib, output, tableList)
        
    Returns:
        Data in ideal format (with meta, inputs, outputs)
    """
    import time
    
    # Extract basic information
    data_flow_id = request_data.get("dataFlowId", "")
    name = request_data.get("etlLib", {}).get("name", "")
    id_val = request_data.get("dataFlowId", "")  # Use dataFlowId as id
    
    # Create timestamp-based ID counter
    timestamp_id_counter = int(time.time() * 1000)
    
    # Create meta array
    meta = []
    
    # Add INPUT_DATASET entries from tableList
    input_positions = []
    for idx, table in enumerate(request_data.get("tableList", [])):
        timestamp_id_counter += 1
        # Generate y positions as: 0, 100, 200, 300, ...
        y_pos = idx * 100
        input_positions.append(y_pos)
        input_meta = {
            "type": "INPUT_DATASET",
            "name": table.get("tableNameEn", table.get("tableNameCn", "")),
            "displayType": "CSV",
            "preview": {"scope": "ALL", "config": {}},
            "cascadeUpdateEnabled": False,
            "inputDsId": table.get("dsId", ""),
            "id": f"id_{timestamp_id_counter}",
            "position": {"x": 300, "y": y_pos},
            "sources": []
        }
        meta.append(input_meta)
    
    # Add OUTPUT_DATASET from output section
    output_info = request_data.get("output", {})
    timestamp_id_counter += 1
    output_meta = {
        "type": "OUTPUT_DATASET",
        "parentDirId": output_info.get("parentDirId", ""),
        "dataSource": {
            "created": True,
            "dsId": output_info.get("outputDsId", ""),
            "name": output_info.get("name", ""),
            "dirPath": [{"dirId": output_info.get("parentDirId", ""), "dirName": "demo"}],
            "parentDirName": "demo",
            "parentDirId": output_info.get("parentDirId", "")
        },
        "id": f"id_{timestamp_id_counter}",
        "position": {"x": 800, "y": 300},
        "name": output_info.get("name", ""),
        "columnAnnotations": [],
        "outputDsName": output_info.get("outputDsName", ""),
        "sources": []
    }
    meta.append(output_meta)
    
    # Create inputs array from tableList
    inputs = []
    for table in request_data.get("tableList", []):
        input_item = {
            "dsId": table.get("dsId", ""),
            "name": table.get("tableNameEn", table.get("tableNameCn", "")),
            "fields": []
        }
        
        # Transform fieldList to fields format
        for idx, field in enumerate(table.get("fieldList", [])):
            field_item = {
                "name": field.get("fieldLabel", ""),
                "type": field.get("fieldType", ""),
                "seqNo": idx
            }
            input_item["fields"].append(field_item)
        
        inputs.append(input_item)
    
    # Create outputs array from output section
    outputs = [{
        "dsId": output_info.get("outputDsId", ""),
        "name": output_info.get("name", ""),
        "dirPath": [{"dirId": output_info.get("parentDirId", ""), "dirName": "demo"}],
        "created": True,
        "parentDirId": output_info.get("parentDirId", ""),
        "parentDirName": "demo"
    }]

    # Create ideal format structure with all fields
    ideal_data = {
        "uId": None,
        "dataFlowId": data_flow_id,
        "domId": "guanbi",
        "name": name,
        "parentDirId": None,
        "triggerType": None,
        "cron": None,
        "executionCount": None,
        "executionSuccessCount": None,
        "lastExecution": None,
        "lastExecuteTime": None,
        "displayType": None,
        "status": None,
        "utime": None,
        "ctime": None,
        "version": None,
        "description": "test",
        "annotation": {"list": []},
        "fuseConfig": None,
        "id": id_val,
        "meta": meta,
        "inputs": inputs,
        "outputs": outputs,
        "platform": "bi",
        "task_description": request_data.get("remark", "")
    }
    
    return ideal_data


async def generate_etl_json(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成ETL JSON配置的便捷函数
    
    Args:
        request_description: ETL任务描述，可以是字符串或Pydantic模型
        
    Returns:
        JSON配置字典
    """
    try:
        logger.info("开始生成ETL JSON配置")
        # Transform request_description to ideal format
        logger.info("检测到request格式，正在转换为ideal格式")

        request_dict = _transform_request_to_ideal(request_data)

        # 保存json_content到111111.json以便调试
        ######################################
        # 转换任务描述为JSON字符串
        request_str = json.dumps(request_dict, ensure_ascii=False)
        with open('111111.json', 'w', encoding='utf-8') as f:
            f.write(request_str if request_str  else "")
        ######################################

        # pass the prompt to select_datasets first and get message content before get_team
        # Convert request_dict to JSON string before passing to select_datasets
        shortened_request_str = await select_datasets(user_request=request_dict)
        # Extract JSON content from the response
        shortened_request_str = _extract_json_from_content(shortened_request_str) or shortened_request_str
        # 保存json_content到222222.json以便调试
        ######################################
        with open('222222.json', 'w', encoding='utf-8') as f:
            f.write(shortened_request_str if shortened_request_str else "")
        ######################################

        # 获取团队实例
        team = await _get_team()
        
        if not team:
            logger.error("ETL团队未正确初始化")
            return {"error": "ETL team not initialized"}
    

        # 使用直接运行模式
        try:
            result = await team.run(task=shortened_request_str)
        finally:
            # 无论成功或失败，都将团队实例返回连接池
            await _return_team(team)
        
        # 从结果中提取JSON
        if hasattr(result, 'messages'):
            for message in result.messages:
                # 只处理TextMessage类型的消息
                if isinstance(message, TextMessage):
                    content = message.content
                    # 检查是否为JSON_Validator的成功消息
                    if hasattr(message, 'source') and message.source == "JSON_Validator" and "JSON validation PASSED" in content:
                        # 使用统一的JSON提取函数
                        json_content = _extract_json_from_content(content)
                        if json_content:
                            try:
                                json_result = json.loads(json_content)
                                logger.info("成功提取JSON配置")
                                return json_result
                            except json.JSONDecodeError as e:
                                logger.error(f"JSON解析错误: {e}")
                    else:
                        # 尝试从任何消息中提取JSON
                        json_content = _extract_json_from_content(content)
                        if json_content:
                            try:
                                json_result = json.loads(json_content)
                                logger.info("从消息中提取到JSON配置")
                                return json_result
                            except json.JSONDecodeError as e:
                                logger.error(f"JSON解析错误: {e}")
        
        logger.warning("未生成有效的JSON配置")
        return {"error": "No valid JSON generated"}
            
    except Exception as e:
        logger.error(f"生成ETL JSON配置时发生错误: {e}")
        return {"error": str(e)}


# 示例用法
# async def example_usage():
#     """示例用法"""
#     task = """
#     请帮我生成一个 ETL 配置：
#     输入数据：CDASH_AE（不良事件数据）和CDASH_DM（受试者数据）
#     输出要求：找到受试者最新的一个不良事件，生成包含受试者、年龄和最新不良事件的输出
#     """
    
#     logger.info("=== 测试生成 ===")
#     json_result = await generate_etl_json(task)
#     logger.info("生成的JSON配置:")
#     logger.info(json.dumps(json_result, ensure_ascii=False, indent=2))


# if __name__ == "__main__":
#     asyncio.run(example_usage())
