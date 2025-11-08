#!/usr/bin/env python
# coding=utf-8

"""
简单登录测试脚本
用于直接测试路由器登录功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.enhanced_router_control import TPLinkWAN2Controller

def test_simple_login():
    """简单登录测试"""
    print("\n🔍 简单登录测试...")

    try:
        # 创建路由器控制器
        controller = TPLinkWAN2Controller(
            router_ip="192.168.1.1",
            username="wangdg68",
            password="wap951020ZJL",
            headless=False  # 使用非headless模式以便观察
        )

        print("✅ 路由器控制器初始化成功")

        # 测试WebDriver设置
        if controller.setup_driver():
            print("✅ WebDriver设置成功")
        else:
            print("❌ WebDriver设置失败")
            return False

        # 测试登录
        print("\n🔄 开始登录测试...")
        if controller.login():
            print("✅ 登录成功")

            # 测试IP切换
            print("\n🔄 开始IP切换测试...")
            if controller.switch_ip():
                print("✅ IP切换成功")
            else:
                print("❌ IP切换失败")

            controller.close()
            return True
        else:
            print("❌ 登录失败")
            controller.close()
            return False

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("简单登录测试工具")
    print("=" * 60)

    # 运行简单登录测试
    success = test_simple_login()

    if success:
        print("\n✅ 所有测试通过")
    else:
        print("\n❌ 测试失败")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

