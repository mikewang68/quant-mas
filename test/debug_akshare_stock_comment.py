#!/usr/bin/env python3
"""
Debug AkShare stock comment functionality to see if we can get real Guba data
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


def test_stock_comment_functions():
    """Test various AkShare stock comment functions to see which ones work for getting Guba data"""
    if not ak:
        print("AkShare not available")
        return

    stock_code = "300339"
    print(f"Testing AkShare stock comment functions for stock {stock_code}")

    # Test the main stock_comment_em function (no parameters)
    try:
        print("\n1. Testing ak.stock_comment_em() - Overall market comment data")
        comments_df = ak.stock_comment_em()

        print(f"Result type: {type(comments_df)}")
        print(f"Result shape: {comments_df.shape}")

        if comments_df.empty:
            print("No comment data returned")
        else:
            print("Comments data columns:", list(comments_df.columns))
            print(f"Number of comment items: {len(comments_df)}")

            # Show first row if data exists
            if len(comments_df) > 0:
                print("\nFirst item:")
                print(comments_df.iloc[0])

    except Exception as e:
        print(f"Error getting AkShare overall comments: {e}")
        import traceback

        traceback.print_exc()

    # Test specific stock comment functions
    comment_functions = [
        ("stock_comment_detail_scrd_focus_em", ak.stock_comment_detail_scrd_focus_em),
        ("stock_comment_detail_zlkp_jgcyd_em", ak.stock_comment_detail_zlkp_jgcyd_em),
        ("stock_comment_detail_zhpj_lspf_em", ak.stock_comment_detail_zhpj_lspf_em),
        ("stock_comment_detail_scrd_desire_em", ak.stock_comment_detail_scrd_desire_em),
        (
            "stock_comment_detail_scrd_desire_daily_em",
            ak.stock_comment_detail_scrd_desire_daily_em,
        ),
    ]

    for func_name, func in comment_functions:
        try:
            print(f"\n2. Testing {func_name} for stock {stock_code}")
            result_df = func(symbol=stock_code)

            print(f"Result type: {type(result_df)}")
            print(f"Result shape: {result_df.shape}")

            if result_df.empty:
                print("No data returned")
            else:
                print("Data columns:", list(result_df.columns))
                print(f"Number of items: {len(result_df)}")

                # Show first row if data exists
                if len(result_df) > 0:
                    print("\nFirst item:")
                    print(result_df.iloc[0])

        except Exception as e:
            print(f"Error calling {func_name}: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_stock_comment_functions()
