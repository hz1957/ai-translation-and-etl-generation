# app/monitoring/llm_monitoring.py
import threading
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any

# 使用线程锁来确保在多线程环境下的数据一致性
_lock = threading.Lock()

@dataclass
class LLMCallTrace:
    """
    用于存储单次LLM调用信息的结构体。
    """
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime = None
    duration: float = 0.0
    success: bool = False
    error_message: str = None
    
    def end(self, success: bool, error_message: str = None):
        """标记调用结束，并计算持续时间"""
        self.end_time = datetime.now(timezone.utc)
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.success = success
        self.error_message = error_message

# 创建一个双端队列来存储最近的100次调用记录
# deque在从两端添加或删除元素时具有O(1)的性能
traces: deque[LLMCallTrace] = deque(maxlen=100)

@contextmanager
def record_llm_call():
    """
    一个上下文管理器/装饰器，用于方便地记录LLM调用的信息。
    """
    trace = LLMCallTrace()
    try:
        yield trace
    except Exception as e:
        trace.end(success=False, error_message=str(e))
        with _lock:
            traces.append(trace)
        # 重新抛出异常，以确保不影响原始的异常处理流程
        raise
    else:
        trace.end(success=True)
        with _lock:
            traces.append(trace)

def get_llm_stats() -> Dict[str, Any]:
    """
    计算并返回关于LLM调用的统计数据。
    """
    with _lock:
        # 创建一个线程安全的副本进行计算
        current_traces: List[LLMCallTrace] = list(traces)

    if not current_traces:
        return {
            "total_calls": 0,
            "success_calls": 0,
            "failed_calls": 0,
            "success_rate": 0,
            "average_duration": 0,
            "recent_traces": []
        }

    total_calls = len(current_traces)
    success_calls = sum(1 for t in current_traces if t.success)
    failed_calls = total_calls - success_calls
    success_rate = (success_calls / total_calls) * 100 if total_calls > 0 else 0
    
    # 只计算成功的调用的平均耗时
    successful_durations = [t.duration for t in current_traces if t.success]
    average_duration = sum(successful_durations) / len(successful_durations) if successful_durations else 0

    # 格式化traces以便于JSON序列化
    formatted_traces = [
        {
            "start_time": t.start_time.isoformat(),
            "end_time": t.end_time.isoformat() if t.end_time else None,
            "duration": t.duration,
            "success": t.success,
            "error_message": t.error_message
        }
        for t in reversed(current_traces) # 返回最近的调用在前面
    ]

    return {
        "total_calls": total_calls,
        "success_calls": success_calls,
        "failed_calls": failed_calls,
        "success_rate": success_rate,
        "average_duration": average_duration,
        "recent_traces": formatted_traces
    }