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
from utils.get_isp_ip import get_current_ip

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
    判断是否为速率限制错误

    Args:
        error_str (str): 错误信息字符串

    Returns:
        bool: 如果是速率限制错误返回True，否则返回False
    """
    rate_limit_indicators = [
        "429", "403", "too many requests", "forbidden",
        "502", "503", "504", "bad gateway",
        "service unavailable", "gateway timeout"
    ]

    error_lower = error_str.lower()
    return any(indicator in error_lower for indicator in rate_limit_indicators)


def handle_network_error(
    error: Exception,
    used_ip: List[str],
    max_retries: int = 3,
    retry_delay: int = 2,
    router_config: Optional[dict] = None
) -> bool:
    """
    处理网络错误的公共函数

    Args:
        error (Exception): 捕获到的异常
        used_ip (List[str]): 已使用的IP地址列表
        max_retries (int): 最大重试次数
        retry_delay (int): 重试间隔（秒）
        router_config (dict, optional): 路由器配置信息

    Returns:
        bool: 处理成功返回True，否则返回False
    """
    error_str = str(error)
    logger.error(f"网络错误: {error_str}")

    # 检查是否为速率限制错误
    if is_rate_limit_error(error_str):
        logger.warning("检测到速率限制错误，尝试切换IP...")

        # 默认路由器配置
        if router_config is None:
            router_config = {
                "router_ip": "192.168.1.1",
                "username": "wangdg68",
                "password": "wap951020ZJL"
            }

        # 初始化路由器控制器
        controller = TPLinkWAN2Controller(
            router_ip=router_config["router_ip"],
            username=router_config["username"],
            password=router_config["password"]
        )

        # 执行IP切换
        success_switch = controller.switch_ip()
        if success_switch:
            logger.info("IP切换成功")

            # 如果IP检测可用，检查并管理IP地址
            try:
                current_ip = get_current_ip(max_retries=max_retries, retry_delay=retry_delay)
                if current_ip:
                    logger.info(f"当前IP: {current_ip}")

                    # 检查这个IP是否已被使用过
                    while current_ip in used_ip:
                        logger.info(f"IP {current_ip} 已被使用过，再次切换...")
                        controller = TPLinkWAN2Controller(
                            router_ip=router_config["router_ip"],
                            username=router_config["username"],
                            password=router_config["password"]
                        )
                        controller.switch_ip()
                        time.sleep(5)
                        current_ip = get_current_ip(max_retries=max_retries, retry_delay=retry_delay)
                        if current_ip:
                            logger.info(f"新IP: {current_ip}")
                        else:
                            logger.error("多次尝试后仍无法获取当前IP")
                            break

                    # 将新IP添加到已使用列表
                    if current_ip and current_ip not in used_ip:
                        used_ip.append(current_ip)
                        logger.info(f"已将 {current_ip} 添加到已使用IP列表")
                        logger.info(f"当前已使用IP列表: {used_ip}")
                else:
                    logger.error("切换IP后仍无法获取当前IP")
            except Exception as ip_error:
                logger.error(f"IP检测过程中出错: {ip_error}")

            # 等待一段时间让网络稳定
            time.sleep(1)
            return True
        else:
            logger.error("IP切换失败")
            return False
    else:
        # 对于其他类型的网络错误，简单记录并等待重试
        logger.warning(f"非速率限制错误，等待 {retry_delay} 秒后重试...")
        time.sleep(retry_delay)
        return True


def main():
    """
    主函数 - 测试网络错误处理功能
    """
    print("🔍 网络错误处理工具")
    print("此工具提供统一的网络错误处理机制")
    print()

    # 示例用法
    used_ips = []
    try:
        # 模拟一个速率限制错误
        raise Exception("429 Too Many Requests")
    except Exception as e:
        success = handle_network_error(e, used_ips)
        if success:
            print("✅ 网络错误处理成功")
        else:
            print("❌ 网络错误处理失败")


if __name__ == "__main__":
    main()

