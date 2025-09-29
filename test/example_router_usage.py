#!/usr/bin/env python3
"""
TP-Link路由器WAN2控制示例脚本

这个脚本演示了如何使用增强版路由器控制功能
"""

import sys
import os

# Add the utils directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_router_control import TPLinkWAN2Controller

def example_with_config_file():
    """使用配置文件的示例"""
    print("示例1: 使用配置文件")
    print("-" * 30)

    # 确保配置文件存在
    config_file = "router_config.json"

    # 创建路由器控制器实例
    controller = TPLinkWAN2Controller(config_file=config_file)

    # 执行IP切换
    success = controller.switch_ip()

    if success:
        print("✓ IP切换成功")
    else:
        print("✗ IP切换失败")

def example_with_parameters():
    """使用参数的示例"""
    print("\n示例2: 使用参数")
    print("-" * 30)

    # 创建路由器控制器实例
    controller = TPLinkWAN2Controller(
        router_ip="192.168.1.1",
        username="wangdg68",
        password="wap951020ZJL"
    )

    # 执行IP切换，自定义等待时间
    success = controller.switch_ip(wait_time=3)

    if success:
        print("✓ IP切换成功")
    else:
        print("✗ IP切换失败")

def example_with_logging():
    """带详细日志的示例"""
    print("\n示例3: 带详细日志")
    print("-" * 30)

    # 创建路由器控制器实例（不使用headless模式，便于调试）
    controller = TPLinkWAN2Controller(
        router_ip="192.168.1.1",
        username="wangdg68",
        password="wap951020ZJL",
        headless=False  # 不使用headless模式，可以看到浏览器操作
    )

    # 执行IP切换
    success = controller.switch_ip(wait_time=2)

    if success:
        print("✓ IP切换成功")
    else:
        print("✗ IP切换失败")

def main():
    """主函数"""
    print("TP-Link路由器WAN2控制示例")
    print("=" * 50)

    # 运行示例
    example_with_config_file()
    example_with_parameters()

    # 注意：第三个示例会打开浏览器窗口，取消注释以运行
    # example_with_logging()

    print("\n" + "=" * 50)
    print("示例运行完成")

if __name__ == "__main__":
    main()

