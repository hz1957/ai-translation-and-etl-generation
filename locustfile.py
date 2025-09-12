import random
from locust import HttpUser, task, between

class TranslatorUser(HttpUser):
    """
    模拟翻译API用户的压测类
    """
    # 定义用户在执行任务之间等待的时间范围（秒）
    # wait_time 模拟了真实用户行为的思考时间
    wait_time = between(1, 3)

    @task
    def translate_text(self):
        """
        定义一个压测任务：调用 /translate API
        """
        # 构造一个符合 app.schemas.TranslationRequest 结构的请求体
        # 你可以增加或修改这个列表来测试不同的负载大小
        test_items = [
            { "from": "ZH", "to": "EN", "content": "你好世界。" },
            { "from": "ZH", "to": "EN", "content": "早上好。" },
            { "from": "ZH", "to": "EN", "content": "今天天气真不错。" },
            { "from": "ZH", "to": "EN", "content": "请问现在几点了？" },
            { "from": "ZH", "to": "EN", "content": "谢谢你的帮助。" },
            { "from": "ZH", "to": "EN", "content": "我不明白你的意思。" },
            { "from": "ZH", "to": "EN", "content": "这个多少钱？" },
            { "from": "ZH", "to": "EN", "content": "洗手间在哪里？" },
            { "from": "ZH", "to": "EN", "content": "我想预订一个双人房间。" },
            { "from": "ZH", "to": "EN", "content": "服务员，买单。" },
            { "from": "ZH", "to": "EN", "content": "我爱学习编程。" },
            { "from": "ZH", "to": "EN", "content": "这本书非常有趣。" },
            { "from": "ZH", "to": "EN", "content": "祝你生日快乐！" },
            { "from": "ZH", "to": "EN", "content": "我要去机场赶飞机。" }
        ]
        
        payload = {"items": test_items}

        # 发送 POST 请求到 /translate 端点
        # 使用 name 参数可以在 Locust 的统计报告中为这类请求分组
        self.client.post(
            "http://127.0.0.1:5432/translate",
            json=payload,
            name="/translate"
        )

# 使用方法:
# 1. 确保你的 FastAPI 应用正在运行。
#
# 2. 安装 locust:
#    pip install locust
#
# 3. 在项目根目录下（与 locustfile.py 同级）运行 locust 命令:
#    locust -f locustfile.py --host=http://127.0.0.1:8000
#    请将 --host 参数替换成你实际的应用地址。
#
# 4. 打开浏览器，访问 http://localhost:8089。
#
# 5. 在 Locust 的 Web 界面中:
#    - Number of users: 设置你想要模拟的并发用户总数。
#    - Spawn rate: 设置每秒启动多少个用户，直到达到总用户数。
#    - Host: 确认你的应用地址。
#
# 6. 点击 "Start swarming" 开始压测，你将能实时看到 RPS、响应时间、失败率等统计数据。