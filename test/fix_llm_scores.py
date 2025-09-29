#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fix existing incorrect LLM scores in the database
"""

import sys
import os
import json
import re

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def fix_llm_scores_in_database():
    """Fix LLM scores in the database where they don't match the value text"""

    print("Connecting to database...")
    db_manager = MongoDBManager()
    pool_collection = db_manager.db['pool']

    # Get the latest pool record
    latest_record = pool_collection.find_one(sort=[('selection_date', -1)])

    if not latest_record:
        print("No records found in pool collection")
        return False

    print(f"Processing pool record from {latest_record.get('selection_date', 'Unknown')}")

    # Get stocks from the latest record
    stocks = latest_record.get('stocks', [])
    print(f"Found {len(stocks)} stocks in latest pool record")

    # Track stocks that need to be updated
    stocks_to_update = []

    # Process each stock
    for stock in stocks:
        code = stock.get('code')
        if not code:
            continue

        # Check if this stock has fundamental analysis data
        fund_data = stock.get('fund', {})
        if not fund_data:
            continue

        # Process each strategy in the fund data
        for strategy_name, strategy_data in fund_data.items():
            current_score = strategy_data.get('score', 0.0)
            value_text = strategy_data.get('value', '')

            # Try to extract score from the value text
            extracted_score = extract_score_from_value(value_text)

            # Check if there's a mismatch
            if extracted_score is not None and abs(current_score - extracted_score) > 0.01:
                print(f"Stock {code}: Found score mismatch for strategy '{strategy_name}'")
                print(f"  Current score: {current_score}")
                print(f"  Extracted score: {extracted_score}")

                # Add to update list
                stocks_to_update.append({
                    'code': code,
                    'strategy_name': strategy_name,
                    'old_score': current_score,
                    'new_score': extracted_score
                })

                # Update the score in the stock data
                stock['fund'][strategy_name]['score'] = round(extracted_score, 2)

    # If we found stocks to update, update the database
    if stocks_to_update:
        print(f"\nFound {len(stocks_to_update)} stocks with score mismatches")

        # Prepare cleaned stocks for database update
        cleaned_stocks = []
        for stock in stocks:
            # Convert numpy types to native Python types for MongoDB compatibility
            clean_stock = stock.copy()

            # Ensure all scores are properly formatted
            if 'score' in clean_stock:
                try:
                    clean_stock['score'] = round(float(clean_stock['score']), 2)
                except (ValueError, TypeError):
                    clean_stock['score'] = 0.0

            # Ensure fund scores are properly formatted
            if 'fund' in clean_stock:
                for strategy_name, strategy_data in clean_stock['fund'].items():
                    if 'score' in strategy_data:
                        try:
                            strategy_data['score'] = round(float(strategy_data['score']), 2)
                        except (ValueError, TypeError):
                            strategy_data['score'] = 0.0

            cleaned_stocks.append(clean_stock)

        # Update the latest pool record
        result = pool_collection.update_one(
            {"_id": latest_record["_id"]},
            {
                "$set": {
                    "stocks": cleaned_stocks
                }
            }
        )

        if result.modified_count > 0:
            print(f"Successfully updated {result.modified_count} pool records")
            print("Fixed the following score mismatches:")
            for update in stocks_to_update:
                print(f"  Stock {update['code']}, Strategy '{update['strategy_name']}': {update['old_score']} -> {update['new_score']}")
            return True
        else:
            print("No changes were made to the database")
            return False
    else:
        print("No score mismatches found in the database")
        return True

def extract_score_from_value(value_text):
    """Extract score from value text using regex patterns"""
    if not isinstance(value_text, str):
        return None

    # Try multiple patterns to catch different formats
    patterns = [
        r'评分是(\d+\.?\d*)',      # "评分是0.65" format
        r'(?:评分|score)[:：]?\s*(\d+\.?\d*)',  # General pattern
        r'评分为?(\d+\.?\d*)',     # "评分为0.75" or "评分0.75" format
        r'得分为?(\d+\.?\d*)',     # "得分为85" format
        r'(\d+\.?\d*)分'           # "85分" format
    ]

    score_matches = []
    for pattern in patterns:
        matches = re.findall(pattern, value_text, re.IGNORECASE)
        if matches:
            score_matches = matches
            break

    if score_matches:
        try:
            extracted_score = float(score_matches[0])
            # If score is in 0-100 range, normalize to 0-1 range
            if 0 <= extracted_score <= 100:
                return max(0.0, min(1.0, extracted_score / 100.0))
            elif 0 <= extracted_score <= 1:
                return extracted_score
        except ValueError:
            pass  # If we can't parse the extracted score, return None

    return None

def main():
    """Main function"""
    print("Fixing LLM scores in database...")
    print("=" * 40)

    try:
        success = fix_llm_scores_in_database()

        if success:
            print("\n" + "=" * 40)
            print("✓ Database update completed successfully!")
            print("The LLM score mismatches should now be fixed.")
        else:
            print("\n" + "=" * 40)
            print("⚠ Database update completed, but no changes were needed.")

        return success

    except Exception as e:
        print(f"\n✗ Error updating database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

