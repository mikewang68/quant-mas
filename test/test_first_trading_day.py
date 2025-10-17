#!/usr/bin/env python
# coding=utf-8

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from down2mongo import is_first_trading_day_of_month

def test_first_trading_day():
    """Test the first trading day detection function"""
    print("Testing first trading day detection...")

    is_first_day = is_first_trading_day_of_month()

    if is_first_day:
        print("✓ Today IS the first trading day of the month")
        print("  The update_industry function will be executed")
    else:
        print("✗ Today is NOT the first trading day of the month")
        print("  The update_industry function will be skipped")

    return is_first_day

if __name__ == "__main__":
    test_first_trading_day()

