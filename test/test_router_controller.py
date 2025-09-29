#!/usr/bin/env python3
"""
Test script for TPLinkWAN2Controller
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.enhanced_router_control import TPLinkWAN2Controller
    print("✓ Successfully imported TPLinkWAN2Controller")

    # Test controller initialization
    controller = TPLinkWAN2Controller(
        router_ip="192.168.1.1",
        username="wangdg68",
        password="wap951020ZJL",
    )
    print("✓ Controller initialized successfully")
    print(f"  Router IP: {controller.config['router_ip']}")
    print(f"  Username: {controller.config['username']}")

    # Test setup_driver method
    print("Testing setup_driver...")
    if controller.setup_driver():
        print("✓ WebDriver setup successful")
        controller.close()
    else:
        print("✗ WebDriver setup failed")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

