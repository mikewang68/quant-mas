#!/usr/bin/env python3
"""
Debug AkShare news functionality to see if we can get real data
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

def test_akshare_news():
    """Test if AkShare can get real stock news data"""
    if not ak:
        print("AkShare not available")
        return

    stock_code = "300339"
    print(f"Testing AkShare news data for stock {stock_code}")

    try:
        # Get recent news for the stock
        print("Calling ak.stock_news_em...")
        news_df = ak.stock_news_em(stock_code)

        print(f"Result type: {type(news_df)}")
        print(f"Result shape: {news_df.shape}")

        if news_df.empty:
            print("No news data returned")
            return

        print("News data columns:", list(news_df.columns))
        print(f"Number of news items: {len(news_df)}")

        if len(news_df) > 0:
            print("\nFirst few news items:")
            for i in range(min(3, len(news_df))):
                print(f"\nItem {i+1}:")
                for col in news_df.columns:
                    value = news_df.iloc[i][col]
                    print(f"  {col}: {value} (type: {type(value)})")

    except Exception as e:
        print(f"Error getting AkShare news: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_akshare_news()

