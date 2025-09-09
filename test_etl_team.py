#!/usr/bin/env python3
"""
ETL Team 测试脚本
"""
import asyncio
import sys
import os
import json
import logging
from typing import Any, Dict, Optional
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import TextMessage

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_etl_team.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def test_etl_service():
    """测试ETL JSON服务"""
    from app.services.etl_json_service import generate_etl_json
    
    logger.info("=== 开始测试ETL JSON服务 ===")
    
    # 从文件读取测试任务
    with open('etl_request_1.json', 'r', encoding='utf-8') as f:
        test_task = json.load(f)
    
    try:
        # 使用服务生成JSON
        result = await generate_etl_json(test_task)
        
        # 处理结果
        if result and "error" not in result:
            logger.info("✅ ETL JSON服务测试成功")
            logger.info("\n=== 生成的JSON配置 ===")
            logger.info(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            logger.error("❌ ETL JSON服务测试失败")
            logger.error(f"错误: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.exception(f"测试过程中发生错误: {e}")


def main():
    # 测试ETL JSON服务
    asyncio.run(test_etl_service())

if __name__ == "__main__":
    main()