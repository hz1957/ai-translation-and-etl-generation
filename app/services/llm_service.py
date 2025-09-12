# app/services/llm_service.py
import httpx
import logging
import time
import asyncio
from typing import List, Dict
from cachetools import TTLCache
from ..config.settings import settings
from ..schemas import TranslationItem
from ..clients.llm_client import LLMClient, LLMAPIError
from ..monitoring.llm_monitoring import record_llm_call

# 获取一个日志记录器实例
logger = logging.getLogger(__name__)

# 创建一个内存缓存
translation_cache = TTLCache(maxsize=5000, ttl=600)

async def _translate_chunk(
    llm_client: LLMClient,
    chunk: List[TranslationItem],
    semaphore: asyncio.Semaphore,
    chunk_id: int
) -> Dict[str, str]:
    """
    (异步) 使用LLMClient翻译单个分片，并将结果逐项存入缓存。
    使用Semaphore来限制并发。
    """
    logger.info(f"分片 {chunk_id}: 开始处理 (包含 {len(chunk)} 项)...")
    async with semaphore:
        if not chunk:
            return {}

        # 调用LLMClient执行翻译
        # 使用我们新的监控上下文管理器来包裹LLM调用
        with record_llm_call() as trace:
            try:
                translated_map = await llm_client.translate(chunk, chunk_id)
                # 如果调用成功，手动标记trace为成功
                trace.end(success=True)
            except LLMAPIError as e:
                # 如果发生特定的LLM API错误，记录错误信息并重新抛出
                trace.end(success=False, error_message=str(e))
                raise  # 确保异常继续向上传播
            except Exception as e:
                # 捕获任何其他意外错误
                trace.end(success=False, error_message=f"An unexpected error occurred: {e}")
                raise

        # --- 缓存逻辑 ---
        # 将成功的结果逐项存入缓存，并根据每项的实际语言对生成缓存键
        content_to_item_map = {item.content: item for item in chunk}

        for original_text, translated_text in translated_map.items():
            item = content_to_item_map.get(original_text)
            if item:
                cache_key = f"{item.source_lang}:{item.target_lang}:{original_text}"
                translation_cache[cache_key] = translated_text
            else:
                # 这种情况理论上不应发生，因为返回的map的key应该来自于输入的chunk
                logger.warning(
                    f"翻译结果中的原文 '{original_text}' 在原始分片数据中未找到，无法为其生成缓存。"
                )
        
        return translated_map

async def translate_list_to_map(
    source_lang: str, target_lang: str, items: List[str], client: httpx.AsyncClient
) -> Dict[str, str]:
    """
    (异步) 将一个字符串列表翻译成一个map，并支持自动分片和并发处理。
    如果任何分片处理失败，将抛出异常。
    此函数会处理输入列表中的重复项，并优先从缓存中获取结果。
    """
    if not items:
        return {}

    # --- 内部数据结构转换 & 去重 ---
    # 将输入的字符串列表转换为内部使用的 TranslationItem 对象列表，同时去重
    unique_items_map = {
        content: TranslationItem(**{"from": source_lang, "to": target_lang, "content": content})
        for content in items
    }
    unique_items = list(unique_items_map.values())
    
    logger.info(f"收到了 {len(items)} 个翻译请求，其中包含 {len(unique_items)} 个独立内容。")

    # --- 缓存查找逻辑 ---
    final_map = {}
    items_to_translate = []
    for item in unique_items:
        cache_key = f"{item.source_lang}:{item.target_lang}:{item.content}"
        cached_result = translation_cache.get(cache_key)
        if cached_result:
            final_map[item.content] = cached_result
        else:
            items_to_translate.append(item)
    
    cached_count = len(final_map)
    if cached_count > 0:
        logger.info(f"缓存命中: {cached_count} / {len(unique_items)} 项。")

    # 如果所有内容都在缓存中，则直接返回
    if not items_to_translate:
        logger.info("所有翻译结果均从缓存中获取。")
        return final_map

    logger.info(f"需要通过API翻译 {len(items_to_translate)} 项。")
    
    # --- 分片和并发翻译 ---
    chunk_size = settings.chunk_size
    chunks = [items_to_translate[i:i + chunk_size] for i in range(0, len(items_to_translate), chunk_size)]

    semaphore = asyncio.Semaphore(settings.max_concurrency)
    
    # 实例化我们新的LLMClient
    llm_client = LLMClient(client)

    start_time = time.time()

    tasks = [
        _translate_chunk(llm_client, chunk, semaphore, i + 1) for i, chunk in enumerate(chunks)
    ]

    # 使用 asyncio.gather 并行执行所有分片的翻译任务
    # return_exceptions=True 使得gather会等待所有任务完成，即使其中一些任务抛出异常
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful_chunks = 0
    for i, result in enumerate(results):
        if isinstance(result, BaseException):
            # 如果任务返回的是一个异常，记录错误并重新抛出，中断整个流程
            # 这里我们选择立即失败的策略。也可以修改为收集错误，继续处理。
            logger.error(f"处理分片 {i + 1} 时发生致命错误: {result}")
            # 将底层的LLMAPIError包装或直接抛出
            if isinstance(result, LLMAPIError):
                raise ConnectionError(f"分片 {i + 1} 翻译失败: {result}") from result
            else:
                raise result # 抛出其他意外异常
        else:
            # 如果任务成功，更新最终的结果map
            final_map.update(result)
            successful_chunks += 1

    end_time = time.time()
    total_duration = end_time - start_time
    logger.info(f"所有 {successful_chunks} 个分片处理成功。总耗时: {total_duration:.2f} 秒。")

    # --- 数量一致性检查 ---
    # 检查翻译后的结果数量是否与去重后的输入数量一致
    if len(final_map) != len(unique_items):
        logger.error(
            f"翻译结果数量 ({len(final_map)}) 与唯一的输入项数量 ({len(unique_items)}) 不匹配。"
            "翻译过程中可能丢失了项目。"
        )
        # 抛出异常以表示这是一个严重错误
        raise ValueError("翻译结果与输入不一致，处理中断。")

    return final_map