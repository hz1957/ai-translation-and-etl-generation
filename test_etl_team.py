#!/usr/bin/env python3
"""
ETL Team 测试脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.etl_team import get_team

async def user_input(msg: str, cancellation_token=None) -> str:
    """模拟用户输入"""
    print(f"\n[系统收到消息]: {msg}")
    print("请输入您的回复 (输入 'APPROVE' 批准, '终止对话' 结束):")
    return input("> ")

async def main():
    print("=== ETL Team 测试 ===")
    print("这是一个用于生成 ETL JSON 配置的智能体团队")
    print("团队成员: JSON_Generator, QA_Agent, JSON_Validator, User_Proxy")
    print()
    
    # 获取团队实例
    team = await get_team(user_input_func=user_input)
    
    # 测试任务
    test_task = """
    请帮我生成一个 ETL 配置：
  "meta": [
    {
      "type": "INPUT_DATASET",
      "name": "CDASH_AE",
      "displayType": "CSV",
      "preview": { "scope": "ALL", "config": {} },
      "cascadeUpdateEnabled": false,
      "inputDsId": "facddcc2ccc8f4be4823c07b",
      "id": "id_1756272056325",
      "position": { "x": 667, "y": -82 },
      "sources": []
    },
    {
      "type": "INPUT_DATASET",
      "name": "CDASH_LB",
      "displayType": "CSV",
      "preview": { "scope": "ALL", "config": {} },
      "cascadeUpdateEnabled": false,
      "inputDsId": "v1e6db5955b28425c8da6f9a",
      "id": "id_1756272072199",
      "position": { "x": 670, "y": 50 },
      "sources": []
    },
    {
      "type": "INPUT_DATASET",
      "name": "CDASH_DM",
      "displayType": "CSV",
      "preview": { "scope": "ALL", "config": {} },
      "cascadeUpdateEnabled": false,
      "inputDsId": "d1eb397adbf35428eaa15793",
      "id": "id_1756272073121",
      "position": { "x": 669, "y": 182 },
      "sources": []
    }
  ],
  "inputs": [
    {
      "dsId": "facddcc2ccc8f4be4823c07b",
      "name": "CDASH_AE",
      "fields": [
        { "name": "研究中心", "type": "STRING", "seqNo": 0 },
        { "name": "中心编号", "type": "LONG", "seqNo": 1 },
        { "name": "受试者", "type": "STRING", "seqNo": 2 },
        { "name": "页面名称", "type": "STRING", "seqNo": 3 },
        { "name": "记录号", "type": "LONG", "seqNo": 4 },
        { "name": "不良事件名称", "type": "STRING", "seqNo": 5 },
        { "name": "开始日期", "type": "DATE", "seqNo": 6 },
        { "name": "开始时间", "type": "STRING", "seqNo": 7 },
        { "name": "结束日期", "type": "DATE", "seqNo": 8 },
        { "name": "结束时间", "type": "STRING", "seqNo": 9 },
        { "name": "AE分类", "type": "STRING", "seqNo": 10 },
        { "name": "是否为严重不良事件", "type": "STRING", "seqNo": 11 },
        { "name": "是否为限制性毒性事件", "type": "STRING", "seqNo": 12 },
        { "name": "严重程度（CTCAE）", "type": "STRING", "seqNo": 13 },
        { "name": "与研究用药的因果关系", "type": "STRING", "seqNo": 14 },
        { "name": "是否因严重不良事件退出试验", "type": "STRING", "seqNo": 15 },
        { "name": "IrAE", "type": "STRING", "seqNo": 16 },
        { "name": "是否导致药物暂停", "type": "STRING", "seqNo": 17 },
        { "name": "是否导致药物降低剂量", "type": "STRING", "seqNo": 18 },
        { "name": "是否导致永久停药", "type": "STRING", "seqNo": 19 }
      ]
    },
    {
      "dsId": "v1e6db5955b28425c8da6f9a",
      "name": "CDASH_LB",
      "fields": [
        { "name": "研究中心", "type": "STRING", "seqNo": 0 },
        { "name": "中心编号", "type": "LONG", "seqNo": 1 },
        { "name": "受试者", "type": "STRING", "seqNo": 2 },
        { "name": "访视名称", "type": "STRING", "seqNo": 3 },
        { "name": "访视OID", "type": "STRING", "seqNo": 4 },
        { "name": "页面名称", "type": "STRING", "seqNo": 5 },
        { "name": "记录号", "type": "LONG", "seqNo": 6 },
        { "name": "采样日期", "type": "DATE", "seqNo": 7 },
        { "name": "检查项目", "type": "STRING", "seqNo": 8 },
        { "name": "检查结果", "type": "STRING", "seqNo": 9 },
        { "name": "单位", "type": "STRING", "seqNo": 10 },
        { "name": "下限", "type": "DOUBLE", "seqNo": 11 },
        { "name": "上限", "type": "DOUBLE", "seqNo": 12 },
        { "name": "基线数据", "type": "DOUBLE", "seqNo": 13 }
      ]
    },
    {
      "dsId": "d1eb397adbf35428eaa15793",
      "name": "CDASH_DM",
      "fields": [
        { "name": "研究中心", "type": "STRING", "seqNo": 0 },
        { "name": "中心编号", "type": "LONG", "seqNo": 1 },
        { "name": "项目", "type": "STRING", "seqNo": 2 },
        { "name": "方案编号", "type": "STRING", "seqNo": 3 },
        { "name": "受试者", "type": "STRING", "seqNo": 4 },
        { "name": "受试者状态", "type": "STRING", "seqNo": 5 },
        { "name": "页面名称", "type": "STRING", "seqNo": 6 },
        { "name": "出生日期", "type": "DATE", "seqNo": 7 },
        { "name": "年龄", "type": "LONG", "seqNo": 8 },
        { "name": "年龄_UNIT", "type": "STRING", "seqNo": 9 },
        { "name": "性别", "type": "STRING", "seqNo": 10 },
        { "name": "民族", "type": "STRING", "seqNo": 11 },
        { "name": "身高", "type": "LONG", "seqNo": 12 },
        { "name": "身高_UNIT", "type": "STRING", "seqNo": 13 },
        { "name": "WEIGHT", "type": "DOUBLE", "seqNo": 14 },
        { "name": "WEIGHT_UNIT", "type": "STRING", "seqNo": 15 },
        { "name": "受试者情况", "type": "STRING", "seqNo": 16 },
        { "name": "年龄分组（n, %）", "type": "STRING", "seqNo": 17 },
        { "name": "AGE-N(Nmiss)", "type": "LONG", "seqNo": 18 },
        { "name": "AGE-Mean±Std", "type": "LONG", "seqNo": 19 },
        { "name": "AGE-M (Q1~Q3)", "type": "LONG", "seqNo": 20 },
        { "name": "AGE-Min~Max", "type": "LONG", "seqNo": 21 },
        { "name": "诊断", "type": "STRING", "seqNo": 22 },
        { "name": "现阶段分期", "type": "STRING", "seqNo": 23 },
        { "name": "ECOG评分", "type": "LONG", "seqNo": 24 },
        { "name": "转移器官数量", "type": "STRING", "seqNo": 25 },
        { "name": "PD-L1表达状态", "type": "STRING", "seqNo": 26 }
      ]
    }
  ],  
请选择合适的input_dataset, 请找到受试者最新的一个不良事件，生成一个output，包含受试者，年龄，和他的最新的一个不良事件

    """
    
    print(f"开始执行任务: {test_task}")
    print("=" * 50)
    
    try:
        # 运行团队
        result = await team.run(
            task=test_task
        )
        
        print("\n=== 任务完成 ===")
        print(f"结果: {result}")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())