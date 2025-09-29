#!/usr/bin/env python3
"""
检查TP-Link设备是否可以通过python-kasa库发现和控制
"""

import asyncio
from kasa import Discover

async def main():
    print("正在发现TP-Link设备...")

    try:
        # 发现网络中的TP-Link设备
        devices = await Discover.discover()

        if not devices:
            print("未发现任何TP-Link设备")
            return

        print(f"发现 {len(devices)} 个设备:")

        for ip, device in devices.items():
            print(f"\n设备IP: {ip}")

            try:
                # 更新设备信息
                await device.update()

                print(f"  设备名称: {device.alias}")
                print(f"  设备型号: {device.model}")
                print(f"  设备类型: {type(device).__name__}")

                # 如果是智能插排或插座，显示更多详细信息
                if hasattr(device, 'is_on'):
                    print(f"  开关状态: {'开启' if device.is_on else '关闭'}")

                # 显示支持的功能
                print(f"  支持的功能: {device.features}")

            except Exception as e:
                print(f"  获取设备信息时出错: {e}")

    except Exception as e:
        print(f"发现设备时出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())

