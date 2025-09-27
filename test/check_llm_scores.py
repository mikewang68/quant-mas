#!/usr/bin/env python3
"""
Check LLM fundamental strategy scores in database
"""

import sys
import os
import json
import re

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_llm_fundamental_scores():
    """Check LLM fundamental strategy scores in database"""
    print("Checking LLM fundamental strategy scores in database...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        pool_collection = db_manager.db['pool']

        # Find recent records with fundamental analysis
        records = list(pool_collection.find({
            "agent_name": {"$regex": "基本面"}
        }).sort("selection_date", -1).limit(5))

        print(f"Found {len(records)} fundamental analysis records:")

        for i, record in enumerate(records):
            print(f"\n--- Record {i+1} ---")
            print(f"Agent: {record.get('agent_name', 'N/A')}")
            print(f"Selection Date: {record.get('selection_date', 'N/A')}")

            # Check stocks
            if 'stocks' in record and record['stocks']:
                print(f"Number of stocks: {len(record['stocks'])}")

                # Look for LLM fundamental strategy results
                for j, stock in enumerate(record['stocks'][:3]):  # Check first 3 stocks
                    if 'fund' in stock and 'LLM基本面分析' in stock['fund']:
                        llm_data = stock['fund']['LLM基本面分析']
                        score = llm_data.get('score', 'N/A')
                        value = llm_data.get('value', 'N/A')

                        print(f"  Stock {j+1} ({stock.get('code', 'N/A')}):")
                        print(f"    Score: {score}")
                        print(f"    Value: {str(value)[:100]}...")  # First 100 chars

                        # Try to extract score from value if it's a string
                        if isinstance(value, str) and '评分' in value:
                            # Try to find score in the value string
                            score_match = re.search(r'评分[:：]?\s*(\d+\.?\d*)', value)
                            if score_match:
                                value_score = float(score_match.group(1))
                                print(f"    Score extracted from value: {value_score}")
                                if isinstance(score, (int, float)):
                                    diff = abs(score - value_score)
                                    if diff > 0.01:  # More than 1% difference
                                        print(f"    ⚠️  SCORE MISMATCH: DB score={score}, Value score={value_score}")
                                    elif diff > 0.0001:  # Check for 100x difference
                                        if abs(score * 100 - value_score) < 0.01:
                                            print(f"    ⚠️  POSSIBLE 100x DIFFERENCE: DB score={score}, Value score={value_score}")
                                        elif abs(score - value_score * 100) < 0.01:
                                            print(f"    ⚠️  POSSIBLE 100x DIFFERENCE (reverse): DB score={score}, Value score={value_score}")

        # Close database connection
        db_manager.close_connection()
        print("\n✓ LLM score check completed successfully")

    except Exception as e:
        print(f"Error checking LLM scores: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = check_llm_fundamental_scores()
    if not success:
        sys.exit(1)

