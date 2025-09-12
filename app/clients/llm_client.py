# app/clients/llm_client.py
import json
import logging
import re
import asyncio
import time
from typing import List, Dict

import httpx

from ..config.settings import settings
from ..schemas import TranslationItem

# 获取一个日志记录器实例
logger = logging.getLogger(__name__)


class LLMAPIError(Exception):
    """自定义异常，用于表示与大模型API相关的特定错误。"""
    pass


class LLMClient:
    """
    一个专门用于与大语言模型API交互的客户端。

    该类封装了API请求的构建、发送、响应解析和重试逻辑，
    使得上层服务可以更简单地调用大模型的能力，而无需关心底层的HTTP实现细节。
    """

    def __init__(self, client: httpx.AsyncClient):
        """
        初始化LLM客户端。

        Args:
            client: 一个httpx.AsyncClient实例，用于发送HTTP请求。
        """
        self._client = client

    async def translate(
        self,
        chunk: List[TranslationItem],
        chunk_id: int
    ) -> Dict[str, str]:
        """
        (异步) 调用大模型API翻译单个分片。

        Args:
            chunk: 需要翻译的TranslationItem对象列表。
            chunk_id: 当前分片的ID，主要用于日志记录。

        Returns:
            一个包含翻译结果的字典。

        Raises:
            LLMAPIError: 如果在多次重试后仍然无法获取有效响应。
        """
        if not chunk:
            return {}

        source_lang = chunk[0].source_lang
        target_lang = chunk[0].target_lang
        input_text = "\n".join([f"- {item.content}" for item in chunk])

        # 从配置中加载并格式化提示词
        prompt = settings.translation_user_prompt.format(
            source_lang=source_lang,
            target_lang=target_lang,
            input_text=input_text
        )
        system_prompt = settings.translation_system_prompt.format(
            source_lang=source_lang,
            target_lang=target_lang
        )

        headers = {
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": settings.llm_model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7,
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.debug("发送给大模型的Payload (分片 %d, 第 %d 次尝试): \n%s",
                             chunk_id, attempt + 1, json.dumps(payload, indent=2, ensure_ascii=False))

                start_time = time.time()
                response = await self._client.post(settings.llm_api_url, headers=headers, json=payload, timeout=60)
                end_time = time.time()
                logger.info(f"分片 {chunk_id}: 模型请求耗时: {end_time - start_time:.2f} 秒")

                response.raise_for_status()

                response_data = response.json()
                logger.debug("收到大模型的原始响应 (分片 %d): \n%s", chunk_id, json.dumps(response_data, indent=2, ensure_ascii=False))

                content_str = response_data['choices'][0]['message']['content']
                
                # 使用正则表达式从模型返回的文本中提取JSON部分
                match = re.search(r"{.*}", content_str, re.DOTALL)
                if not match:
                    raise ValueError("在模型响应中未找到有效的JSON对象")

                clean_json_str = match.group(0)
                translated_map = json.loads(clean_json_str)

                if not isinstance(translated_map, dict):
                    raise ValueError("模型返回的不是一个有效的map/dict")

                if len(translated_map) == len(chunk):
                    return translated_map
                else:
                    logger.warning(
                        "分片 %d - 第 %d 次尝试失败: 输入 %d 项, 输出 %d 项, 数量不匹配。正在重试...",
                        chunk_id, attempt + 1, len(chunk), len(translated_map)
                    )

            except httpx.RequestError as e:
                logger.error("分片 %d - 调用大模型API时发生网络错误 (第 %d 次尝试): %s", chunk_id, attempt + 1, e)
                if attempt == max_retries - 1:
                    raise LLMAPIError(f"分片 {chunk_id}: 无法连接到大模型服务: {e}") from e
            except (KeyError, IndexError, json.JSONDecodeError, ValueError) as e:
                logger.error("分片 %d - 解析大模型响应时出错 (第 %d 次尝试): %s", chunk_id, attempt + 1, e)
                if attempt == max_retries - 1:
                    raise LLMAPIError(f"分片 {chunk_id}: 无法解析模型的响应: {e}") from e
            
            if attempt < max_retries - 1:
                await asyncio.sleep(1)  # 在重试前稍作等待

        raise LLMAPIError(f"分片 {chunk_id}: 重试 {max_retries} 次后，翻译结果的数量仍与输入不匹配。")
