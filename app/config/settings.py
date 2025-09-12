# app/config/settings.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import logging

# --- 新的多环境配置加载逻辑 ---
# 1. 首先，加载项目根目录下的 .env 文件（如果存在）。
#    这个文件可以用来在本地指定 APP_ENV，例如 APP_ENV=dev
#    并且这个 .env 文件通常不应提交到版本控制中。
load_dotenv(dotenv_path=".env")

# 2. 从环境变量中读取APP_ENV。
#    - 如果操作系统中设置了 APP_ENV，它将覆盖 .env 文件中的设置。
#    - 如果两者都未设置，则默认为 'dev'。
APP_ENV = os.getenv("APP_ENV", "dev")

# 3. 根据最终确定的 APP_ENV 的值，确定要加载的环境特定配置文件
#    例如 .env.dev 或 .env.prod
env_file = f".env.{APP_ENV}"

# 4. 使用 dotenv 加载对应的环境特定配置文件。
#    `override=True` 确保 .env.dev 或 .env.prod 中的设置
#    会覆盖可能在第一步 .env 文件中加载的同名变量。
load_dotenv(dotenv_path=env_file, override=True)

# 在配置加载时也使用日志记录
logging.getLogger(__name__).info(f"当前环境 (APP_ENV): {APP_ENV}")
logging.getLogger(__name__).info(f"加载的环境配置文件: {env_file}")

class Settings(BaseSettings):
    """
    应用配置类，使用Pydantic进行类型校验和管理
    """
    # 将 app_env 的默认值直接设为 APP_ENV
    app_env: str = APP_ENV
    llm_api_url: str
    llm_api_url_agent: str
    llm_api_key: str
    llm_model_name: str
    # 移除这里的默认值，让它完全从 .env.* 文件中读取，更符合预期
    chunk_size: int
    max_concurrency: int

    # --- 从 .env 加载提示词 ---
    # 移除默认值，强制要求这些配置必须在 .env.* 文件中提供。
    # 如果环境中缺少这些变量，Pydantic 在实例化 Settings 时会直接抛出校验错误。
    translation_user_prompt: str
    translation_system_prompt: str

    class Config:
        # Pydantic-settings会自动从环境变量中读取配置，
        # 由于我们已经用 load_dotenv 加载了 .env 文件，这里的配置会自动映射。
        pass

# 创建一个全局可用的配置实例
settings = Settings()