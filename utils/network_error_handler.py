#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网络错误处理工具

此工具提供统一的网络错误处理机制，包括：
1. 错误类型识别和分类
2. IP切换决策和执行
3. 重试机制
4. 日志记录

该模块可以作为工具模块导入，提供handle_network_error()函数供其他程序调用。
"""

import time
import logging
import sys
from typing import List, Optional
from utils.enhanced_router_control import TPLinkWAN2Controller

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def is_rate_limit_error(error_str: str) -> bool:
    """
    判断是否为速率限制错误或网络连接错误

    Args:
        error_str (str): 错误信息字符串

    Returns:
        bool: 如果是速率限制错误或网络连接错误返回True，否则返回False
    """
    network_error_indicators = [
        # 速率限制错误
        "429",
        "403",
        "too many requests",
        "forbidden",
        # 服务器错误
        "502",
        "503",
        "504",
        "bad gateway",
        "service unavailable",
        "gateway timeout",
        # 网络连接错误
        "connection aborted",
        "remote disconnected",
        "remote end closed connection",
        "connection reset",
        "connection refused",
        "connection timeout",
        "network is unreachable",
        "no route to host",
        "name or service not known",
    ]

    error_lower = error_str.lower()
    return any(indicator in error_lower for indicator in network_error_indicators)


def handle_network_error(
    error: Exception, max_retries: int = 3, retry_delay: int = 2
) -> bool:
    """
    处理网络错误的公共函数

    Args:
        error (Exception): 捕获到的异常
        max_retries (int): 最大重试次数
        retry_delay (int): 重试间隔（秒）

    Returns:
        bool: 处理成功返回True，否则返回False
    """
    error_str = str(error)
    logger.error(f"网络错误: {error_str}")

    # 首先判断是否是速率限制错误
    if not is_rate_limit_error(error_str):
        logger.info(f"非速率限制错误，跳过路由器控制: {error_str}")
        return False

    logger.warning("检测到速率限制错误，尝试切换IP...")

    # 默认路由器配置
    router_config = {
        "router_ip": "192.168.1.1",
        "username": "wangdg68",
        "password": "wap951020ZJL",
    }

    # 初始化路由器控制器
    controller = TPLinkWAN2Controller(
        router_ip=router_config["router_ip"],
        username=router_config["username"],
        password=router_config["password"],
    )

    # 执行IP切换
    success_switch = controller.switch_ip()
    if success_switch:
        logger.info("IP切换成功")
        # 等待一段时间让网络稳定
        time.sleep(1)
        return True
    else:
        logger.error("IP切换失败")
        return False


def main():
    """
    主函数 - 测试网络错误处理功能
    """
    print("🔍 网络错误处理工具")
    print("此工具提供统一的网络错误处理机制")
    print()

    try:
        # 模拟一个速率限制错误
        raise Exception("429 Too Many Requests")
    except Exception as e:
        success = handle_network_error(e)
        if success:
            print("✅ 网络错误处理成功")
        else:
            print("❌ 网络错误处理失败")


if __name__ == "__main__":
    main()
