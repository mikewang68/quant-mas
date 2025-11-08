#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版网络错误处理工具

此工具提供统一的网络错误处理机制，包括：
1. 错误类型识别和分类
2. IP切换决策和执行
3. 智能重试机制
4. 详细日志记录

该模块可以作为工具模块导入，提供handle_network_error()函数供其他程序调用。
"""

import time
import logging
import sys
import re
from typing import List, Optional, Dict, Any
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


class NetworkErrorClassifier:
    """网络错误分类器"""

    @staticmethod
    def classify_error(error_str: str) -> Dict[str, Any]:
        """
        分类网络错误类型

        Args:
            error_str (str): 错误信息字符串

        Returns:
            Dict[str, Any]: 错误分类结果
        """
        error_lower = error_str.lower()

        # 速率限制错误
        rate_limit_indicators = [
            "429", "too many requests", "rate limit", "rate exceeded",
            "403", "forbidden", "quota exceeded", "主动触发IP更换"
        ]

        # 服务器错误
        server_error_indicators = [
            "502", "503", "504", "bad gateway", "service unavailable",
            "gateway timeout", "internal server error"
        ]

        # 网络连接错误
        connection_error_indicators = [
            "connection aborted", "remote disconnected", "remote end closed connection",
            "connection reset", "connection refused", "connection timeout",
            "network is unreachable", "no route to host", "name or service not known",
            "could not reach host", "are you offline", "timeout", "timed out"
        ]

        # DNS错误
        dns_error_indicators = [
            "name resolution", "dns", "host not found", "temporary failure in name resolution"
        ]

        # SSL/TLS错误
        ssl_error_indicators = [
            "ssl", "tls", "certificate", "handshake failure"
        ]

        # 超时错误
        timeout_error_indicators = [
            "timeout", "timed out", "operation timed out"
        ]

        # 检查每种错误类型
        error_type = "unknown"
        severity = "medium"
        should_switch_ip = False

        # 速率限制错误 - 高优先级，需要切换IP
        for indicator in rate_limit_indicators:
            if any('一' <= char <= '鿿' for char in indicator):
                if indicator in error_str:
                    error_type = "rate_limit"
                    severity = "high"
                    should_switch_ip = True
                    break
            elif indicator.lower() in error_lower:
                error_type = "rate_limit"
                severity = "high"
                should_switch_ip = True
                break

        # 服务器错误 - 中等优先级，可能需要切换IP
        if error_type == "unknown":
            for indicator in server_error_indicators:
                if indicator.lower() in error_lower:
                    error_type = "server_error"
                    severity = "medium"
                    should_switch_ip = True
                    break

        # 连接错误 - 中等优先级，可能需要切换IP
        if error_type == "unknown":
            for indicator in connection_error_indicators:
                if indicator.lower() in error_lower:
                    error_type = "connection_error"
                    severity = "medium"
                    should_switch_ip = True
                    break

        # DNS错误 - 低优先级，可能不需要切换IP
        if error_type == "unknown":
            for indicator in dns_error_indicators:
                if indicator.lower() in error_lower:
                    error_type = "dns_error"
                    severity = "low"
                    should_switch_ip = False
                    break

        # SSL错误 - 低优先级，可能不需要切换IP
        if error_type == "unknown":
            for indicator in ssl_error_indicators:
                if indicator.lower() in error_lower:
                    error_type = "ssl_error"
                    severity = "low"
                    should_switch_ip = False
                    break

        # 超时错误 - 中等优先级，可能需要切换IP
        if error_type == "unknown":
            for indicator in timeout_error_indicators:
                if indicator.lower() in error_lower:
                    error_type = "timeout_error"
                    severity = "medium"
                    should_switch_ip = True
                    break

        return {
            "type": error_type,
            "severity": severity,
            "should_switch_ip": should_switch_ip,
            "original_error": error_str
        }


def is_rate_limit_error(error_str: str) -> bool:
    """
    判断是否为速率限制错误或网络连接错误

    Args:
        error_str (str): 错误信息字符串

    Returns:
        bool: 如果是速率限制错误或网络连接错误返回True，否则返回False
    """
    classification = NetworkErrorClassifier.classify_error(error_str)
    return classification["should_switch_ip"]


def handle_network_error(
    error: Exception,
    max_retries: int = 3,
    retry_delay: int = 2,
    router_config: Optional[Dict[str, Any]] = None
) -> bool:
    """
    处理网络错误的公共函数

    Args:
        error (Exception): 捕获到的异常
        max_retries (int): 最大重试次数
        retry_delay (int): 重试间隔（秒）
        router_config (Optional[Dict[str, Any]]): 路由器配置

    Returns:
        bool: 处理成功返回True，否则返回False
    """
    error_str = str(error)
    classification = NetworkErrorClassifier.classify_error(error_str)

    logger.error(f"网络错误检测: {classification['type']} (严重性: {classification['severity']})")
    logger.error(f"错误详情: {error_str}")

    # 首先判断是否需要切换IP
    if not classification["should_switch_ip"]:
        logger.info(f"非IP切换类错误，跳过路由器控制: {classification['type']}")
        return False

    logger.warning(f"检测到需要IP切换的错误类型: {classification['type']}")
    logger.warning("尝试使用IP轮换机制切换IP...")

    # 导入IP轮换机制
    try:
        from utils.down2mongo import switch_to_new_ip

        # 使用IP轮换机制
        success = switch_to_new_ip()

        if success:
            logger.info("✅ IP轮换成功完成")
            # 根据错误严重性决定等待时间
            wait_time = 5 if classification["severity"] == "high" else 3
            logger.info(f"等待{wait_time}秒让网络稳定...")
            time.sleep(wait_time)
            return True
        else:
            logger.error("❌ IP轮换失败")
            return False

    except ImportError as e:
        logger.error(f"无法导入IP轮换机制: {e}")
        logger.error("回退到直接路由器控制...")

        # 默认路由器配置
        if router_config is None:
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
            # 根据错误严重性决定等待时间
            wait_time = 5 if classification["severity"] == "high" else 3
            logger.info(f"等待{wait_time}秒让网络稳定...")
            time.sleep(wait_time)
            return True
        else:
            logger.error("IP切换失败")
            return False


def get_error_statistics() -> Dict[str, Any]:
    """
    获取错误统计信息

    Returns:
        Dict[str, Any]: 错误统计信息
    """
    # 这里可以扩展为从数据库或日志中获取历史错误统计
    return {
        "total_errors": 0,
        "rate_limit_errors": 0,
        "connection_errors": 0,
        "server_errors": 0,
        "last_error_time": None
    }


def main():
    """
    主函数 - 测试网络错误处理功能
    """
    print("🔍 增强版网络错误处理工具")
    print("此工具提供智能网络错误分类和处理机制")
    print()

    # 测试各种错误类型
    test_errors = [
        "429 Too Many Requests",
        "Connection aborted by remote host",
        "Could not reach host. Are you offline?",
        "SSL handshake failed",
        "DNS resolution failed",
        "502 Bad Gateway",
        "主动触发IP更换",
        "Unknown error type"
    ]

    for error_msg in test_errors:
        print(f"\n测试错误: {error_msg}")
        classification = NetworkErrorClassifier.classify_error(error_msg)
        print(f"  分类: {classification['type']}")
        print(f"  严重性: {classification['severity']}")
        print(f"  需要切换IP: {classification['should_switch_ip']}")

    print("\n✅ 错误分类测试完成")


if __name__ == "__main__":
    main()
