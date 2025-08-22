#!/usr/bin/env python3
"""
Investigate the actual source and calculation of position values in the database
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.mongodb_manager import MongoDBManager
import json
import numpy as np

def investigate_position_source():
    """Investigate where position values come from and how they're calculated"""
    print("Investigating the source and calculation of position values...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        print("✓ Database connection established")

        # Get pool collection
        pool_collection = db_manager.db['pool']

        # Get multiple records to understand the pattern
        records = list(pool_collection.find().sort('selection_date', -1).limit(5))

        print(f"\nFound {len(records)} recent pool records:")

        for i, record in enumerate(records):
            print(f"\n--- Record {i+1} ---")
            print(f"  ID: {record.get('_id', 'N/A')}")
            print(f"  Strategy Name: {record.get('strategy_name', 'N/A')}")
            print(f"  Selection Date: {record.get('selection_date', 'N/A')}")
            print(f"  Total Stocks: {record.get('count', 'N/A')}")

            # Check stocks structure
            stocks = record.get('stocks', [])
            if stocks:
                # Check for different position structures
                stocks_with_top_level_position = [s for s in stocks if 'position' in s]
                stocks_with_nested_position = []

                for stock in stocks:
                    tech_analysis = stock.get('tech_analysis', {})
                    acc_up_trend = tech_analysis.get('acc_up_trend', {})
                    if 'position' in acc_up_trend:
                        stocks_with_nested_position.append({
                            'stock': stock,
                            'position': acc_up_trend['position']
                        })

                print(f"  Stocks with top-level position: {len(stocks_with_top_level_position)}")
                print(f"  Stocks with nested position: {len(stocks_with_nested_position)}")

                if stocks_with_nested_position:
                    print("  Sample nested positions:")
                    for j, item in enumerate(stocks_with_nested_position[:3]):
                        stock = item['stock']
                        position = item['position']
                        print(f"    {stock.get('code', 'N/A')}: {position}")

        # Focus on the latest record with nested positions
        latest_record = records[0] if records else None
        if latest_record:
            print(f"\n--- Detailed Analysis of Latest Record ---")
            stocks = latest_record.get('stocks', [])

            # Find stocks with nested positions
            stocks_with_nested_position = []
            for stock in stocks:
                tech_analysis = stock.get('tech_analysis', {})
                acc_up_trend = tech_analysis.get('acc_up_trend', {})
                if 'position' in acc_up_trend:
                    stocks_with_nested_position.append({
                        'code': stock.get('code', 'N/A'),
                        'position': acc_up_trend['position'],
                        'technical_data': acc_up_trend
                    })

            if stocks_with_nested_position:
                print(f"Found {len(stocks_with_nested_position)} stocks with nested positions")

                # Analyze if there's a pattern with stock prices
                print("Analyzing position vs technical indicators:")

                # Take a sample for detailed analysis
                sample_stocks = stocks_with_nested_position[:10]
                for stock in sample_stocks:
                    code = stock['code']
                    position = stock['position']
                    tech_data = stock['technical_data']
                    price = tech_data.get('price', 0)
                    score = tech_data.get('score', 0)
                    angle = tech_data.get('current_angle', 0)

                    print(f"\n  Stock {code}:")
                    print(f"    Position: {position}")
                    print(f"    Price: {price}")
                    print(f"    Score: {score}")
                    print(f"    Angle: {angle}")

                    # Try to determine if position is based on a fixed investment amount
                    if price > 0:
                        investment_amount = position * price
                        print(f"    Implied investment: {investment_amount:.2f}")

                        # Check if this is consistent across stocks
                        # Let's assume a fixed investment amount and see if it matches
                        fixed_amounts = [1000, 5000, 10000, 20000, 50000]
                        for amount in fixed_amounts:
                            calculated_position = amount / price
                            error = abs(calculated_position - position) / position * 100
                            print(f"    If invested {amount}: position would be {calculated_position:.2f} (error: {error:.1f}%)")

        db_manager.close_connection()
        print("\n✓ Position source investigation completed successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = investigate_position_source()
    sys.exit(0 if success else 1)

