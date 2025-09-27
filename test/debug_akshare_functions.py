#!/usr/bin/env python3
"""
Debug AkShare functions to see what Guba-related functions are available
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import akshare as ak
    print("AkShare imported successfully")
except ImportError as e:
    print(f"Error importing AkShare: {e}")
    ak = None

def find_guba_functions():
    """Find all Guba-related functions in AkShare"""
    if not ak:
        print("AkShare not available")
        return

    # Get all attributes of akshare
    all_attrs = dir(ak)

    # Filter for Guba-related functions
    guba_functions = [attr for attr in all_attrs if 'guba' in attr.lower()]

    print("Guba-related functions in AkShare:")
    for func in guba_functions:
        print(f"  {func}")

    # Also check for stock-related functions
    stock_functions = [attr for attr in all_attrs if 'stock' in attr.lower() and ('comment' in attr.lower() or 'discuss' in attr.lower() or 'guba' in attr.lower())]

    print("\nStock-related functions that might be Guba-related:")
    for func in stock_functions:
        print(f"  {func}")

    # Try to get help on some functions
    print("\nTrying to get function details...")
    functions_to_check = ['stock_news_em'] + guba_functions[:3]  # Check stock_news_em and first few guba functions

    for func_name in functions_to_check:
        if hasattr(ak, func_name):
            func = getattr(ak, func_name)
            print(f"\n{func_name}:")
            if hasattr(func, '__doc__') and func.__doc__:
                print(f"  Doc: {func.__doc__[:200]}...")
            else:
                print("  No documentation available")

if __name__ == "__main__":
    find_guba_functions()

