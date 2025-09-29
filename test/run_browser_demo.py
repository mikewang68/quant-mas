#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
演示脚本：运行TP-Link路由器WAN2 IP切换程序并显示浏览器界面
"""

import sys
import os
import argparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.switch_ip_selenium import RouterControllerSelenium

def main():
    """主函数"""
    print("=" * 60)
    print("TP-Link路由器WAN2 IP切换演示程序")
    print("=" * 60)
    print("此程序将启动浏览器并显示操作过程")
    print("请确保路由器可以访问且凭据正确")
    print()

    # 获取用户输入的路由器配置
    router_ip = input("请输入路由器IP地址 (默认: 192.168.1.1): ").strip() or "192.168.1.1"
    username = input("请输入用户名 (默认: wangdg68): ").strip() or "wangdg68"
    password = input("请输入密码: ").strip()

    if not password:
        print("错误: 密码不能为空")
        return 1

    print(f"\n配置信息:")
    print(f"  路由器IP: {router_ip}")
    print(f"  用户名: {username}")
    print(f"  密码: {'*' * len(password)}")
    print()

    # 确认是否继续
    confirm = input("是否继续执行? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("操作已取消")
        return 0

    print("\n启动浏览器并执行操作...")
    print("注意: 请观察浏览器窗口中的操作过程")
    print()

    # 创建路由器控制器实例（非headless模式）
    router = RouterControllerSelenium(
        router_ip=router_ip,
        username=username,
        password=password,
        headless=False  # 显示浏览器界面
    )

    # 执行IP切换
    try:
        success = router.switch_ip(wait_time=3)

        if success:
            print("\n" + "=" * 50)
            print("恭喜! IP切换操作成功完成。")
            print("=" * 50)
            return 0
        else:
            print("\n" + "=" * 50)
            print("抱歉，IP切换操作失败。")
            print("=" * 50)
            return 1
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        return 1
    except Exception as e:
        print(f"\n执行过程中发生错误: {e}")
        return 1
    finally:
        # 等待用户查看结果
        input("\n按Enter键关闭浏览器并退出...")

if __name__ == "__main__":
    sys.exit(main())

