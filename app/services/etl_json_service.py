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

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.etl_team import get_team
from app.config.logging import configure_logging

# 配置日志
configure_logging()
logger = logging.getLogger(__name__)

# 全局团队实例
_team = None


async def _auto_approve(msg: str, cancellation_token=None) -> str:
    """自动批准函数，用于服务模式"""
    logger.info(f"Auto-approving message: {msg[:100]}...")
    return "APPROVE"


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
    """获取ETL团队实例（单例模式）"""
    global _team
    if _team is None:
        _team = await get_team(user_input_func=_auto_approve)
    return _team


async def generate_etl_json(task_description: Any) -> Dict[str, Any]:
    """
    生成ETL JSON配置的便捷函数
    
    Args:
        task_description: ETL任务描述，可以是字符串或Pydantic模型
        
    Returns:
        JSON配置字典
    """
    try:
        logger.info("开始生成ETL JSON配置")
        
        # 获取团队实例
        team = await _get_team()
        
        if not team:
            logger.error("ETL团队未正确初始化")
            return {"error": "ETL team not initialized"}
        
        # 转换任务描述为字符串
        task_str = (
            task_description.model_dump_json()
            if hasattr(task_description, 'model_dump_json')
            else str(task_description)
        )
        
        # 使用直接运行模式，避免流式处理的复杂性和错误
        result = await team.run(task=task_str)
        
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