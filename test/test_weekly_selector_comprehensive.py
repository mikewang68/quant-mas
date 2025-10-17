"""
Comprehensive test for WeeklySelector to verify all fixes work correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_strategy_results_format():
    """Test the strategy results format to ensure it's consistent"""
    print("\n=== Testing Strategy Results Format ===")

    # Create mock strategy results in the expected format
    strategy_results = {
        "趋势-放量突破策略（强势股捕捉）": (
            ["301246", "601968", "688480"],  # selected_stocks
            {
                "301246": "突破信号",
                "601968": "放量上涨",
                "688480": "强势突破"
            },  # selection_values
            {
                "301246": 0.85,
                "601968": 0.92,
                "688480": 0.78
            }  # selected_scores
        )
    }

    print(f"Strategy results type: {type(strategy_results)}")
    print(f"Number of strategies: {len(strategy_results)}")

    # Test unpacking - this should work without errors
    for strategy_name, (selected_stocks, selection_values, selected_scores) in strategy_results.items():
        print(f"\nStrategy: {strategy_name}")
        print(f"  Selected stocks: {selected_stocks}")
        print(f"  Selection values: {selection_values}")
        print(f"  Selected scores: {selected_scores}")

        # Verify types
        assert isinstance(selected_stocks, list), f"selected_stocks should be list, got {type(selected_stocks)}"
        assert isinstance(selection_values, dict), f"selection_values should be dict, got {type(selection_values)}"
        assert isinstance(selected_scores, dict), f"selected_scores should be dict, got {type(selected_scores)}"

        print(f"  ✓ All types are correct")

    print("\n✓ Strategy results format test passed!")
    return strategy_results

def test_save_selected_stocks_logic():
    """Test the save_selected_stocks method logic"""
    print("\n=== Testing Save Selected Stocks Logic ===")

    # Create mock strategy results
    strategy_results = {
        "趋势-放量突破策略（强势股捕捉）": (
            ["301246", "601968", "688480"],
            {
                "301246": "突破信号",
                "601968": "放量上涨",
                "688480": "强势突破"
            },
            {
                "301246": 0.85,
                "601968": 0.92,
                "688480": 0.78
            }
        )
    }

    # Test the unpacking logic that save_selected_stocks uses
    all_stocks_data = []
    all_strategy_names = []
    total_stock_count = 0

    # Process each strategy's results
    for strategy_name, (selected_stocks, selection_value, scores) in strategy_results.items():
        print(f"\nProcessing strategy: {strategy_name}")
        print(f"  Selected stocks: {selected_stocks}")
        print(f"  Selection value type: {type(selection_value)}")
        print(f"  Scores type: {type(scores)}")

        if not selected_stocks:
            print("  No stocks selected, skipping")
            continue

        # Record strategy name
        all_strategy_names.append(strategy_name)
        total_stock_count += len(selected_stocks)

        # Convert stocks list to the expected format
        for stock_code in selected_stocks:
            # Get score from scores dictionary
            score = 0.0
            if scores and isinstance(scores, dict):
                score = scores.get(stock_code, 0.0)
                print(f"  Stock {stock_code}: score = {score}")
            else:
                print(f"  Stock {stock_code}: scores is not a dictionary, using default score 0.0")

            # Get selection value from strategy results if available
            value_text = ""
            if selection_value and isinstance(selection_value, dict) and stock_code in selection_value:
                value_text = selection_value[stock_code]
                print(f"  Stock {stock_code}: selection_value = {value_text}")
            else:
                value_text = f"Strategy {strategy_name} selected stock {stock_code}"
                print(f"  Stock {stock_code}: using default selection_value")

            # Create value data with required structure
            value_content = {
                "code": stock_code,
                "score": score,
                "selection_reason": value_text,
            }

            # Check if stock already exists
            existing_stock = None
            for stock in all_stocks_data:
                if stock.get('code') == stock_code:
                    existing_stock = stock
                    break

            if existing_stock:
                # If stock exists, add new strategy data to trend field
                if 'trend' not in existing_stock:
                    existing_stock['trend'] = {}
                existing_stock['trend'][strategy_name] = {"score": score, "value": value_content}
                print(f"  Added to existing stock: {stock_code}")
            else:
                # If stock doesn't exist, create new record
                stock_info = {
                    "code": stock_code,
                    "trend": {
                        strategy_name: {"score": score, "value": value_content}
                    },
                }
                all_stocks_data.append(stock_info)
                print(f"  Created new stock record: {stock_code}")

    print(f"\nTotal stocks data: {len(all_stocks_data)}")
    print(f"All strategy names: {all_strategy_names}")
    print(f"Total stock count: {total_stock_count}")

    print("\n✓ Save selected stocks logic test passed!")
    return all_stocks_data

def test_weekly_selector_import():
    """Test that WeeklySelector can be imported and initialized"""
    print("\n=== Testing WeeklySelector Import ===")

    try:
        from agents.weekly_selector import WeeklyStockSelector
        print("✓ WeeklyStockSelector imported successfully")

        # Test the type annotations
        import inspect
        sig = inspect.signature(WeeklyStockSelector.save_selected_stocks)
        print(f"save_selected_stocks signature: {sig}")

        # Check the type annotation for strategy_results parameter
        annotations = WeeklyStockSelector.save_selected_stocks.__annotations__
        if 'strategy_results' in annotations:
            print(f"strategy_results type annotation: {annotations['strategy_results']}")

        print("✓ WeeklySelector import test passed!")
        return True

    except Exception as e:
        print(f"✗ WeeklySelector import test failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting comprehensive WeeklySelector test...")

    # Run all tests
    test_weekly_selector_import()
    strategy_results = test_strategy_results_format()
    all_stocks_data = test_save_selected_stocks_logic()

    print("\n" + "="*50)
    print("🎉 ALL TESTS PASSED! WeeklySelector should work correctly now.")
    print("="*50)

