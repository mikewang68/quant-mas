#!/usr/bin/env python3
"""
Example script demonstrating how to use Qian Gu Qian Ping data in Enhanced Public Opinion Analysis Strategy V2
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def main():
    """Main example function"""
    print("Example: Using Qian Gu Qian Ping Data in Enhanced Public Opinion Analysis Strategy V2")
    print("=" * 80)

    # Initialize the strategy
    print("1. Initializing strategy...")
    strategy = EnhancedPublicOpinionAnalysisStrategyV2()
    print(f"   Strategy: {strategy.name}")
    print(f"   Qian Gu Qian Ping data loaded: {strategy.qian_gu_qian_ping_data is not None}")
    if strategy.qian_gu_qian_ping_data:
        print(f"   Number of stocks in Qian Gu Qian Ping data: {len(strategy.qian_gu_qian_ping_data)}")

    # Look up Qian Gu Qian Ping data for specific stocks
    print("\n2. Looking up Qian Gu Qian Ping data for specific stocks...")
    test_stocks = ["300339", "000001", "600000"]

    for stock_code in test_stocks:
        print(f"\n   Stock: {stock_code}")
        qgqp_data = strategy.get_qian_gu_qian_ping_data_for_stock(stock_code)
        if qgqp_data:
            print(f"     Name: {qgqp_data.get('名称', 'N/A')}")
            print(f"     Latest Price: {qgqp_data.get('最新价', 'N/A')}")
            print(f"     Composite Score: {qgqp_data.get('综合得分', 'N/A')}")
            print(f"     Focus Index: {qgqp_data.get('关注指数', 'N/A')}")
            print(f"     Institutional Participation: {qgqp_data.get('机构参与度', 'N/A')}")
        else:
            print(f"     No Qian Gu Qian Ping data found for {stock_code}")

    # Get detailed Guba data for a specific stock
    print("\n3. Getting detailed Guba data for a specific stock...")
    stock_code = "300339"
    print(f"   Stock: {stock_code}")

    detailed_data = strategy.get_detailed_guba_data(stock_code)

    # Display user focus data
    if detailed_data.get("user_focus"):
        print(f"   User Focus Data ({len(detailed_data['user_focus'])} records):")
        for item in detailed_data["user_focus"][:3]:  # Show first 3 records
            print(f"     Date: {item['date']}, Focus Index: {item['focus_index']}")

    # Display institutional participation data
    if detailed_data.get("institutional_participation"):
        print(f"   Institutional Participation Data ({len(detailed_data['institutional_participation'])} records):")
        for item in detailed_data["institutional_participation"][:3]:  # Show first 3 records
            print(f"     Date: {item['date']}, Participation: {item['participation']}")

    # Display historical rating data
    if detailed_data.get("historical_rating"):
        print(f"   Historical Rating Data ({len(detailed_data['historical_rating'])} records):")
        for item in detailed_data["historical_rating"][:3]:  # Show first 3 records
            print(f"     Date: {item['date']}, Rating: {item['rating']}")

    # Display daily participation data
    if detailed_data.get("daily_participation"):
        print(f"   Daily Participation Data ({len(detailed_data['daily_participation'])} records):")
        for item in detailed_data["daily_participation"][:3]:  # Show first 3 records
            print(f"     Date: {item['date']}, Daily Desire Rise: {item['daily_desire_rise']}, Avg Change: {item['avg_participation_change']}")

    # Demonstrate data integration in the collection process
    print("\n4. Demonstrating data integration in collection process...")

    # Create sample data for collection
    sample_data = strategy.collect_all_data(stock_code, "润和软件")

    print(f"   Collected data keys: {list(sample_data.keys())}")

    # Check if Qian Gu Qian Ping data is included
    if sample_data.get("qian_gu_qian_ping_data"):
        print("   ✓ Qian Gu Qian Ping data included in collection")
    else:
        print("   ✗ Qian Gu Qian Ping data missing from collection")

    # Check if detailed Guba data is included
    if sample_data.get("detailed_guba_data"):
        print("   ✓ Detailed Guba data included in collection")
        guba_data = sample_data["detailed_guba_data"]
        for key in guba_data:
            print(f"     {key}: {len(guba_data[key])} records")
    else:
        print("   ✗ Detailed Guba data missing from collection")

    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("\nKey features demonstrated:")
    print("  1. Strategy initialization with automatic Qian Gu Qian Ping data loading")
    print("  2. Lookup of Qian Gu Qian Ping data for specific stocks")
    print("  3. Collection of detailed Guba data for specific analysis")
    print("  4. Integration of all data in the collection process")
    print("  5. Data ready for LLM analysis (not shown in this example)")

if __name__ == "__main__":
    main()

