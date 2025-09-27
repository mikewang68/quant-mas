#!/usr/bin/env python3
"""
Check specific stock's fundamental scores in pool database
"""

import sys
import os
import json
import re

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_specific_stock_fundamental_scores(stock_code="603381"):
    """Check specific stock's fundamental scores in pool database"""
    print(f"Checking fundamental scores for stock {stock_code} in pool database...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        pool_collection = db_manager.db['pool']

        # Find recent records with fundamental analysis for the specific stock
        records = list(pool_collection.find({
            "stocks.code": stock_code,
            "agent_name": {"$regex": "基本面"}
        }).sort("selection_date", -1).limit(3))

        print(f"Found {len(records)} fundamental analysis records for stock {stock_code}:")

        for i, record in enumerate(records):
            print(f"\n--- Record {i+1} ---")
            print(f"Agent: {record.get('agent_name', 'N/A')}")
            print(f"Selection Date: {record.get('selection_date', 'N/A')}")
            print(f"Fund Analysis Time: {record.get('fund_at', 'N/A')}")

            # Find the specific stock in this record
            stock_data = None
            for stock in record.get('stocks', []):
                if stock.get('code') == stock_code:
                    stock_data = stock
                    break

            if stock_data and 'fund' in stock_data:
                print(f"  Stock {stock_code}:")
                fund_data = stock_data['fund']

                # Check LLM基本面分析策略 data
                for strategy_name, strategy_data in fund_data.items():
                    if 'LLM' in strategy_name or 'llm' in strategy_name or '基本面' in strategy_name:
                        score = strategy_data.get('score', 'N/A')
                        value = strategy_data.get('value', 'N/A')

                        print(f"    Strategy: {strategy_name}")
                        print(f"    Score: {score}")
                        print(f"    Value: {str(value)[:200]}...")  # First 200 chars

                        # Try to extract score from value if it's a string
                        if isinstance(value, str):
                            # Try to find score in the value string
                            score_matches = re.findall(r'(\d+\.?\d*)', value)
                            if score_matches:
                                # Look for scores that look like they might be the main score
                                for match in score_matches[:5]:  # Check first 5 matches
                                    try:
                                        extracted_score = float(match)
                                        # Check if it's in 0-1 range or 0-100 range
                                        if 0 <= extracted_score <= 1 or 0 <= extracted_score <= 100:
                                            print(f"    Extracted score from value: {extracted_score}")
                                            if isinstance(score, (int, float)):
                                                diff = abs(score - extracted_score)
                                                if diff > 0.01:  # More than 1% difference
                                                    print(f"    ⚠️  SCORE MISMATCH: DB score={score}, Value score={extracted_score}")
                                                elif diff > 0.0001:  # Check for 100x difference
                                                    if abs(score * 100 - extracted_score) < 0.01:
                                                        print(f"    ⚠️  POSSIBLE 100x DIFFERENCE: DB score={score}, Value score={extracted_score}")
                                                    elif abs(score - extracted_score * 100) < 0.01:
                                                        print(f"    ⚠️  POSSIBLE 100x DIFFERENCE (reverse): DB score={score}, Value score={extracted_score}")
                                            break
                                    except ValueError:
                                        continue
            elif stock_data:
                print(f"  Stock {stock_code} found but no fund data")
            else:
                print(f"  Stock {stock_code} not found in this record")

        # Close database connection
        db_manager.close_connection()
        print("\n✓ Specific stock fundamental score check completed successfully")

    except Exception as e:
        print(f"Error checking specific stock scores: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    stock_code = "603381"
    if len(sys.argv) > 1:
        stock_code = sys.argv[1]

    success = check_specific_stock_fundamental_scores(stock_code)
    if not success:
        sys.exit(1)

