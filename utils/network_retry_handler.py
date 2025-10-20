#!/usr/bin/env python
# coding=utf-8

import time
import logging

# 设置日志
logger = logging.getLogger(__name__)


def handle_network_error_with_retry(
    error: Exception, max_retries: int = 10, retry_delay: int = 5
) -> bool:
    """
    处理网络错误的公共函数，包含重试机制

    Args:
        error (Exception): 捕获到的异常
        max_retries (int): 最大重试次数，默认10次
        retry_delay (int): 重试间隔（秒），默认5秒

    Returns:
        bool: 处理成功返回True，否则返回False
    """
    from utils.network_error_handler import handle_network_error

    error_str = str(error)
    print(f"网络错误: {error_str}")

    # 尝试处理网络错误，但限制重试次数
    retry_count = 0
    while retry_count < max_retries and not handle_network_error(error):
        retry_count += 1
        print(f"第{retry_count}次重试处理网络错误...")
        time.sleep(retry_delay)

    # 如果重试后仍然失败，返回False
    if retry_count >= max_retries:
        print(f"经过{max_retries}次重试后仍然失败")
        return False

    return True
