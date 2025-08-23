#!/usr/bin/env python3
"""
Test script to verify that the modified trend following strategy can now select more stocks.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector

def test_modified_strategy():
    """Test that the modified trend following strategy can select more stocks"""
    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Get all strategies from database
        strategies = db_manager.get_strategies()
        print("=== All Strategies in Database ===")
        trend_following_strategy_id = None

        for strategy in strategies:
            name = strategy.get('name', '')
            strategy_id = strategy.get('_id')
            if "趋势跟踪策略（稳健型）" in name:
                trend_following_strategy_id = strategy_id
                print(f"Found Trend Following Strategy: {name} (ID: {strategy_id})")
                break

        if not trend_following_strategy_id:
            print("Trend Following Strategy not found!")
            return False

        print("\n=== Testing Modified Trend Following Strategy ===")

        # Create selector with trend following strategy
        selector = WeeklyStockSelector(db_manager, data_fetcher, trend_following_strategy_id)
        print(f"Loaded Strategy: {selector.strategy_name}")
        print(f"Strategy Parameters: {selector.strategy_params}")

        # Select stocks (this may take a while)
        print("Selecting stocks (this may take a moment)...")
        selected_stocks, last_date, golden_cross_flags, scores, tech_data = selector.select_stocks()

        print(f"\nResults:")
        print(f"Selected stocks: {len(selected_stocks)}")
        print(f"Last data date: {last_date}")

        # Show some statistics
        if scores:
            score_values = list(scores.values())
            if score_values:
                avg_score = sum(score_values) / len(score_values)
                min_score = min(score_values)
                max_score = max(score_values)
                print(f"Average score: {avg_score:.2f}")
                print(f"Min score: {min_score:.2f}")
                print(f"Max score: {max_score:.2f}")

        # Show first few selected stocks
        if selected_stocks:
            print(f"\nFirst 10 selected stocks:")
            for i, stock in enumerate(selected_stocks[:10]):
                score = scores.get(stock, 0) if scores else 0
                print(f"  {i+1}. {stock} (Score: {score:.2f})")

        # Check how many stocks have scores between 0 and 60
        low_score_stocks = [stock for stock, score in scores.items() if 0 < score < 60]
        print(f"\nStocks with scores between 0 and 60: {len(low_score_stocks)}")

        # Check how many stocks have scores >= 60
        high_score_stocks = [stock for stock, score in scores.items() if score >= 60]
        print(f"Stocks with scores >= 60: {len(high_score_stocks)}")

        return True

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db_manager.close_connection()
        except:
            pass

if __name__ == "__main__":
    success = test_modified_strategy()
    if not success:
        sys.exit(1)

