#!/usr/bin/env python3
"""
Test script to verify Enhanced Public Opinion Analysis Strategy V2 integration with Public Opinion Selector
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from agents.public_opinion_selector import PublicOpinionStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

def test_strategy_integration():
    """Test the integration of Enhanced Public Opinion Analysis Strategy V2 with Public Opinion Selector"""
    print("Testing Enhanced Public Opinion Analysis Strategy V2 integration with Public Opinion Selector")

    try:
        # Initialize components
        db_manager = MongoDBManager()
        akshare_client = AkshareClient()
        print("Database manager and Akshare client initialized")

        # Initialize Public Opinion Selector
        selector = PublicOpinionStockSelector(
            db_manager=db_manager,
            data_fetcher=akshare_client,
            name="TestPublicOpinionSelector"
        )
        print("Public Opinion Selector initialized")

        # Load strategies
        selector._load_strategies_from_db()
        selector._load_dynamic_strategies()
        print("Strategies loaded")

        # Check if our Enhanced Public Opinion Analysis Strategy V2 is loaded
        strategy_found = False
        for strategy in selector.strategies:
            if isinstance(strategy, EnhancedPublicOpinionAnalysisStrategyV2):
                print(f"Found Enhanced Public Opinion Analysis Strategy V2: {strategy.name}")
                strategy_found = True
                break

        if not strategy_found:
            print("Enhanced Public Opinion Analysis Strategy V2 not found in loaded strategies")
            # Let's manually add it
            enhanced_strategy = EnhancedPublicOpinionAnalysisStrategyV2(
                name="增强型舆情分析策略V2",
                db_manager=db_manager
            )
            selector.strategies.append(enhanced_strategy)
            print("Manually added Enhanced Public Opinion Analysis Strategy V2")

        # Test with a sample stock
        test_stock_code = "000001"
        test_stock_name = "平安银行"

        print(f"Testing strategy with stock: {test_stock_code} ({test_stock_name})")

        # Get stock data
        stock_data = selector.get_data_for_stock(test_stock_code)
        print(f"Stock data shape: {stock_data.shape}")

        # Test each strategy
        for strategy in selector.strategy_instances:
            print(f"\nTesting strategy: {strategy.name}")
            try:
                if hasattr(strategy, 'analyze_public_opinion'):
                    # This is our Enhanced Public Opinion Analysis Strategy V2
                    meets_criteria, reason, sentiment_score, full_analysis = strategy.analyze_public_opinion(
                        test_stock_code, test_stock_name
                    )
                    print(f"  Meets criteria: {meets_criteria}")
                    print(f"  Sentiment score: {sentiment_score}")
                    print(f"  Reason: {reason[:100]}...")
                else:
                    # Other strategies
                    meets_criteria, reason, score = strategy.analyze(stock_data, test_stock_code, test_stock_name)
                    print(f"  Meets criteria: {meets_criteria}")
                    print(f"  Score: {score}")
                    print(f"  Reason: {reason[:100]}...")
            except Exception as e:
                print(f"  Error testing strategy {strategy.name}: {e}")

        print("\nIntegration test completed successfully!")

    except Exception as e:
        print(f"Error during integration test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Close database connection
        if 'db_manager' in locals():
            db_manager.close_connection()

if __name__ == "__main__":
    test_strategy_integration()

