#!/usr/bin/env python3
"""
Debug AkShare Guba functionality to see if we can get real data
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

def test_akshare_guba():
    """Test if AkShare can get real Guba data"""
    if not ak:
        print("AkShare not available")
        return

    stock_code = "300339"
    print(f"Testing AkShare Guba data for stock {stock_code}")

    # Try different Guba functions
    functions_to_try = [
        "stock_guba_em",
        "stock_comments_em",
        "stock_news_em",
    ]

    for func_name in functions_to_try:
        if hasattr(ak, func_name):
            print(f"\nTrying function: {func_name}")
            try:
                func = getattr(ak, func_name)
                result = func(stock_code)
                print(f"  Success! Got {len(result)} items")
                if len(result) > 0:
                    print(f"  Columns: {list(result.columns)}")
                    print(f"  First item:")
                    for col in result.columns:
                        value = result.iloc[0][col]
                        print(f"    {col}: {value}")
            except Exception as e:
                print(f"  Error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"\nFunction {func_name} not found in AkShare")

    # Try specific Guba functions for different types of data
    print("\nTrying specific Guba comment functions...")

    # Try to get stock comments
    try:
        print("Getting stock comments...")
        comments = ak.stock_comments_em(stock_code)
        print(f"Comments: {len(comments)} items")
        if len(comments) > 0:
            print(f"Comments columns: {list(comments.columns)}")
            print("First comment:")
            for col in comments.columns:
                value = comments.iloc[0][col]
                print(f"  {col}: {value}")
    except Exception as e:
        print(f"Error getting comments: {e}")
        import traceback
        traceback.print_exc()

    # Try to get stock discussion
    try:
        print("\nGetting stock discussion...")
        discussion = ak.stock_discussion_em(stock_code)
        print(f"Discussion: {len(discussion)} items")
        if len(discussion) > 0:
            print(f"Discussion columns: {list(discussion.columns)}")
            print("First discussion item:")
            for col in discussion.columns:
                value = discussion.iloc[0][col]
                print(f"  {col}: {value}")
    except Exception as e:
        print(f"Error getting discussion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_akshare_guba()

