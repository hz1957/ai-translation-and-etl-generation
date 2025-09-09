#!/usr/bin/env python3
"""
ETL Team 测试脚本
"""
import asyncio
import sys
import os
import json
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import TextMessage

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Remove logging configuration - use print only

async def test_etl_service():
    """测试ETL JSON服务"""
    # Import team directly
    from app.agents.etl_team import get_team
    
    # Initialize team variable in outer scope
    team = None
    
    print("=== 开始测试ETL JSON服务 ===")
    
    # 从文件读取测试任务
    with open('etl_request_1.json', 'r', encoding='utf-8') as f:
        test_task = json.load(f)
    
    try:
        # 直接运行团队实例并获取流式输出
        team = await get_team()
        if team is None:
            print("无法获取团队实例")
            return
        
        # 转换任务描述为字符串
        task_str = str(test_task)
        
        # 使用流式模式处理团队响应
        result = None
        async for message in team.run_stream(task=task_str):
            # Output original stream message
            print(message)
            # Store the last message as result
            result = message
            
        # Print completion message
        print("=== ETL JSON服务测试完成 ===")
        return result
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        return None

def main():
    # 测试ETL JSON服务
    result = asyncio.run(test_etl_service())
    if result is None:
        print("测试失败或未完成")
    else:
        print("测试成功完成")

if __name__ == "__main__":
    main()