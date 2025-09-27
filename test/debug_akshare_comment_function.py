#!/usr/bin/env python3
"""
Debug AkShare stock_comment_em function signature
"""

import sys
import os
import inspect

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import akshare as ak
    print("AkShare imported successfully")
except ImportError as e:
    print(f"Error importing AkShare: {e}")
    ak = None

def inspect_stock_comment_em():
    """Inspect the stock_comment_em function signature"""
    if not ak:
        print("AkShare not available")
        return

    if hasattr(ak, 'stock_comment_em'):
        func = getattr(ak, 'stock_comment_em')
        print(f"stock_comment_em function:")
        print(f"  Signature: {inspect.signature(func)}")
        print(f"  Docstring: {func.__doc__}")

        # Try calling without arguments
        try:
            print("Calling stock_comment_em() without arguments...")
            result = func()
            print(f"  Result type: {type(result)}")
            print(f"  Result shape: {result.shape if hasattr(result, 'shape') else 'N/A'}")
            if hasattr(result, 'columns'):
                print(f"  Columns: {list(result.columns)}")
                if len(result) > 0:
                    print("  First row:")
                    for col in result.columns:
                        print(f"    {col}: {result.iloc[0][col]}")
        except Exception as e:
            print(f"  Error calling function: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("stock_comment_em function not found")

if __name__ == "__main__":
    inspect_stock_comment_em()

