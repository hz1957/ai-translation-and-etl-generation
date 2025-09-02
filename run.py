# run.py
import uvicorn
import os

if __name__ == "__main__":
    """
    这是推荐的本地开发启动脚本。
    
    执行 `python run.py` 即可启动服务。
    
    此脚本会显式设置 APP_ENV='dev'，确保加载 .env.dev 配置文件。
    uvicorn.run 会将 "app.main:app" 作为一个模块进行加载，
    这可以确保应用内部的所有相对导入都能正确工作。
    `--reload` 参数会监控代码变化并自动重启服务，非常适合开发环境。
    """
    # 设置环境变量，指定为开发环境
    os.environ["APP_ENV"] = "dev"
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=5432, reload=True)