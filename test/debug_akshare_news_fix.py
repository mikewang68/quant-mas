#!/usr/bin/env python3
"""
Debug script to fix AkShare news collection issue
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import akshare as ak
    print("AkShare imported successfully")
except ImportError as e:
    print(f"Error importing AkShare: {e}")
    ak = None


def debug_akshare_news_collection():
    """Debug and fix AkShare news collection"""
    print("Debugging AkShare news collection")
    print("=" * 50)

    if not ak:
        print("AkShare not available")
        return

    stock_code = "300339"
    print(f"Testing AkShare news collection for stock {stock_code}")

    # Test raw AkShare news function
    print("\n1. Testing raw AkShare stock_news_em function...")
    try:
        # Try without pageSize parameter first
        print("   Calling ak.stock_news_em(stock_code)...")
        news_df = ak.stock_news_em(stock_code)

        print(f"   Success! Got DataFrame with shape: {news_df.shape}")
        print(f"   Columns: {list(news_df.columns)}")

        if not news_df.empty:
            print("   First row:")
            for col in news_df.columns:
                value = news_df.iloc[0][col]
                print(f"     {col}: {value} (type: {type(value)})")
        else:
            print("   Empty DataFrame returned")

    except Exception as e:
        print(f"   Error calling ak.stock_news_em: {e}")
        import traceback
        traceback.print_exc()

    # Test with different parameters
    print("\n2. Testing with different parameter combinations...")

    # Try with symbol parameter name
    try:
        print("   Calling ak.stock_news_em(symbol=stock_code)...")
        news_df = ak.stock_news_em(symbol=stock_code)

        print(f"   Success! Got DataFrame with shape: {news_df.shape}")
        print(f"   Columns: {list(news_df.columns)}")

    except Exception as e:
        print(f"   Error calling ak.stock_news_em(symbol=stock_code): {e}")

    # Check what parameters the function actually accepts
    print("\n3. Checking function signature...")
    try:
        import inspect
        sig = inspect.signature(ak.stock_news_em)
        print(f"   Function signature: {sig}")
        print(f"   Parameters: {list(sig.parameters.keys())}")
    except Exception as e:
        print(f"   Error checking function signature: {e}")

    # Test the current implementation from the strategy
    print("\n4. Testing current strategy implementation...")
    try:
        # This is the implementation from the strategy
        news_df = ak.stock_news_em(stock_code)

        if news_df.empty:
            print("   Empty DataFrame returned from ak.stock_news_em")
        else:
            print(f"   Got {len(news_df)} news items")

            # Check columns
            print(f"   Available columns: {list(news_df.columns)}")

            # Filter by time window (last 5 days)
            time_threshold = datetime.now() - timedelta(days=5)
            print(f"   Time threshold: {time_threshold}")

            if "publish_time" in news_df.columns:
                print("   Found publish_time column")
                # Handle datetime conversion properly
                news_df["publish_time"] = pd.to_datetime(
                    news_df["publish_time"], errors="coerce"
                )
                print("   Converted publish_time to datetime")
                filtered_df = news_df[news_df["publish_time"] >= time_threshold]
                print(f"   After time filtering: {len(filtered_df)} items")

                if len(filtered_df) > 0:
                    print("   First filtered item:")
                    for col in filtered_df.columns:
                        value = filtered_df.iloc[0][col]
                        print(f"     {col}: {value}")
            else:
                print("   publish_time column not found")
                # Check what time-related columns exist
                time_columns = [col for col in news_df.columns if 'time' in col.lower() or 'date' in col.lower()]
                print(f"   Time-related columns found: {time_columns}")

                if time_columns:
                    time_col = time_columns[0]
                    print(f"   Using '{time_col}' as time column")
                    news_df[time_col] = pd.to_datetime(
                        news_df[time_col], errors="coerce"
                    )
                    filtered_df = news_df[news_df[time_col] >= time_threshold]
                    print(f"   After time filtering: {len(filtered_df)} items")

            # Convert to list of dictionaries (as in the strategy)
            news_items = []
            for _, row in news_df.head(10).iterrows():
                # Handle publish_time properly
                publish_time = row.get("publish_time")
                publish_time_str = ""
                if pd.notnull(publish_time):
                    publish_time_str = (
                        publish_time.isoformat()
                        if hasattr(publish_time, "isoformat")
                        else str(publish_time)
                    )

                news_items.append(
                    {
                        "title": str(row.get("title", "")),
                        "content": str(row.get("content", ""))[:1000],  # Limit content length
                        "url": str(row.get("url", "")),
                        "publishedAt": publish_time_str,
                        "source": "AkShare",
                    }
                )

            print(f"   Converted to {len(news_items)} news items")
            if news_items:
                print("   First converted item:")
                for key, value in news_items[0].items():
                    print(f"     {key}: {value}")

    except Exception as e:
        print(f"   Error in strategy implementation: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("AkShare news debugging completed")


if __name__ == "__main__":
    debug_akshare_news_collection()

