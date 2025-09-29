#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for down2mongo IP detection
"""

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the IP detection function
try:
    from utils.get_isp_ip import get_current_ip
    IP_DETECTION_AVAILABLE = True
    print("✅ IP detection module imported successfully")
except ImportError:
    IP_DETECTION_AVAILABLE = False
    print("❌ IP detection module not available")

def test_ip_detection():
    """Test IP detection functionality"""
    print("🔍 Testing IP detection...")

    if not IP_DETECTION_AVAILABLE:
        print("❌ IP detection module not available")
        return

    # Get the initial IP before starting data collection
    print("Getting current IP address...")
    initial_ip = get_current_ip()
    if initial_ip:
        print(f"✅ Success! Current IP: {initial_ip}")
    else:
        print("❌ Failed to get current IP")

if __name__ == "__main__":
    test_ip_detection()

