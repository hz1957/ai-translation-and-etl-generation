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
    # Import service directly
    from app.services.etl_json_service import generate_etl_json
    
    print("=== 开始测试ETL JSON服务 ===")
    
    # 从文件读取测试任务
    with open('etl_request_songbin.json', 'r', encoding='utf-8') as f:
        test_task = json.load(f)
    
    try:
        # 调用ETL JSON生成服务
        result = await generate_etl_json(request_data=test_task)
        
        # Print result
        if result and "error" not in result:
            print("服务生成结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # Save result as 333333.json
            with open('333333.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print("结果已保存为 333333.json")
            
            print("=== ETL JSON服务测试完成 ===")
            return result
        else:
            print(f"服务生成失败: {result}")
            print("=== ETL JSON服务测试完成（失败）===")
            return None
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        print("=== ETL JSON服务测试完成（错误）===")
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