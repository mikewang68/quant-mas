#!/usr/bin/env python3
"""
Check consistency between fundamental strategy scores and values in pool database
"""

import sys
import os
import json
import re

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_fundamental_score_consistency(stock_code=None):
    """Check consistency between fundamental strategy scores and values"""
    print("Checking fundamental score consistency in pool database...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        pool_collection = db_manager.db['pool']

        # Query conditions
        query = {"agent_name": {"$regex": "基本面"}}
        if stock_code:
            query["stocks.code"] = stock_code

        # Find recent records with fundamental analysis
        records = list(pool_collection.find(query).sort("selection_date", -1).limit(5))

        print(f"Found {len(records)} fundamental analysis records:")

        inconsistent_count = 0
        total_count = 0

        for i, record in enumerate(records):
            print(f"\n--- Record {i+1} ---")
            print(f"Agent: {record.get('agent_name', 'N/A')}")
            print(f"Selection Date: {record.get('selection_date', 'N/A')}")
            print(f"Fund Analysis Time: {record.get('fund_at', 'N/A')}")

            # Process stocks
            stocks = record.get('stocks', [])
            if stock_code:
                # Filter for specific stock if provided
                stocks = [stock for stock in stocks if stock.get('code') == stock_code]

            for j, stock in enumerate(stocks[:3]):  # Check first 3 stocks or all if less
                if 'fund' in stock:
                    print(f"  Stock {stock.get('code', 'N/A')}:")
                    fund_data = stock['fund']

                    # Check each fundamental strategy
                    for strategy_name, strategy_data in fund_data.items():
                        total_count += 1
                        score = strategy_data.get('score', 'N/A')
                        value = strategy_data.get('value', 'N/A')

                        print(f"    Strategy: {strategy_name}")
                        print(f"    DB Score: {score}")

                        # Try to extract score from value if it's a string
                        if isinstance(value, str):
                            # Look for patterns like "评分: 0.65" or "score: 0.65"
                            score_matches = re.findall(r'(?:评分|score)[:：]?\s*(\d+\.?\d*)', value, re.IGNORECASE)
                            if score_matches:
                                try:
                                    extracted_score = float(score_matches[0])
                                    print(f"    Value Score: {extracted_score}")

                                    # Check for consistency
                                    if isinstance(score, (int, float)):
                                        diff = abs(score - extracted_score)
                                        if diff > 0.01:  # More than 1% difference
                                            print(f"    ⚠️  INCONSISTENCY: DB score={score}, Value score={extracted_score}")
                                            inconsistent_count += 1
                                        elif diff > 0.0001:  # Check for 100x difference
                                            if abs(score * 100 - extracted_score) < 0.01:
                                                print(f"    ⚠️  100x DIFFERENCE: DB score={score}, Value score={extracted_score}")
                                                inconsistent_count += 1
                                            elif abs(score - extracted_score * 100) < 0.01:
                                                print(f"    ⚠️  100x DIFFERENCE (reverse): DB score={score}, Value score={extracted_score}")
                                                inconsistent_count += 1
                                    else:
                                        print(f"    ✓ CONSISTENT")
                                except ValueError:
                                    print(f"    Value Score: Could not parse '{score_matches[0]}'")
                            else:
                                print(f"    Value Score: No score found in value")
                        else:
                            print(f"    Value Score: Value is not a string")

        # Summary
        print(f"\n=== SUMMARY ===")
        print(f"Total strategy entries checked: {total_count}")
        print(f"Inconsistent entries: {inconsistent_count}")
        if total_count > 0:
            consistency_rate = (total_count - inconsistent_count) / total_count * 100
            print(f"Consistency rate: {consistency_rate:.1f}%")

        # Close database connection
        db_manager.close_connection()
        print("\n✓ Fundamental score consistency check completed successfully")

        return inconsistent_count == 0

    except Exception as e:
        print(f"Error checking fundamental score consistency: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    stock_code = None
    if len(sys.argv) > 1:
        stock_code = sys.argv[1]

    success = check_fundamental_score_consistency(stock_code)
    if not success:
        sys.exit(1)

