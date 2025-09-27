#!/usr/bin/env python3
"""
Debug AkShare to find Guba-specific functions for a stock
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import akshare as ak
    print("AkShare imported successfully")
except ImportError as e:
    print(f"Error importing AkShare: {e}")
    ak = None

def test_all_guba_functions():
    """Test all Guba-related functions in AkShare"""
    if not ak:
        print("AkShare not available")
        return

    stock_code = "300339"
    print(f"Testing all Guba-related functions for stock {stock_code}")

    # Get all attributes of akshare
    all_attrs = dir(ak)

    # Filter for functions that might be related to Guba or stock discussions
    potential_functions = [attr for attr in all_attrs if any(keyword in attr.lower() for keyword in ['guba', 'comment', 'discuss', 'talk'])]

    print(f"Found {len(potential_functions)} potential Guba/comment functions:")
    for func_name in potential_functions:
        print(f"  {func_name}")

    # Test each function
    for func_name in potential_functions:
        if hasattr(ak, func_name):
            print(f"\n--- Testing {func_name} ---")
            try:
                func = getattr(ak, func_name)

                # Try calling with stock code
                try:
                    result = func(stock_code)
                    print(f"  Success with stock code! Got {len(result)} items")
                    if len(result) > 0 and hasattr(result, 'columns'):
                        print(f"  Columns: {list(result.columns)}")
                        print("  First item preview:")
                        for col in result.columns:
                            value = result.iloc[0][col]
                            # Limit output length
                            value_str = str(value)[:100] + ("..." if len(str(value)) > 100 else "")
                            print(f"    {col}: {value_str}")
                except Exception as e1:
                    print(f"  Error with stock code: {e1}")

                    # Try calling without arguments
                    try:
                        result = func()
                        print(f"  Success without arguments! Got {len(result)} items")
                        if len(result) > 0 and hasattr(result, 'columns'):
                            print(f"  Columns: {list(result.columns)}")
                            print("  First item preview:")
                            for col in result.columns:
                                value = result.iloc[0][col]
                                # Limit output length
                                value_str = str(value)[:100] + ("..." if len(str(value)) > 100 else "")
                                print(f"    {col}: {value_str}")
                    except Exception as e2:
                        print(f"  Error without arguments: {e2}")
            except Exception as e:
                print(f"  General error: {e}")

if __name__ == "__main__":
    test_all_guba_functions()

