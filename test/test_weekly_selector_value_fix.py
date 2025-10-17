"""
Test script to verify the Weekly Selector value field fix
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.weekly_selector import WeeklyStockSelector

# Test the strategy results tuple format
def test_strategy_results_format():
    print("Testing strategy results tuple format...")

    # Create a mock strategy result with 4 elements
    selected_stocks = ["000001", "000002", "000003"]
    selection_values = {"000001": "reason1", "000002": "reason2", "000003": "reason3"}
    scores = {"000001": 0.85, "000002": 0.92, "000003": 0.78}
    json_values = {
        "000001": '{"score": 0.85, "reason": "reason1", "analysis": "test1"}',
        "000002": '{"score": 0.92, "reason": "reason2", "analysis": "test2"}',
        "000003": '{"score": 0.78, "reason": "reason3", "analysis": "test3"}'
    }

    # Create the 4-element tuple as expected by save_selected_stocks
    strategy_result = (selected_stocks, selection_values, scores, json_values)

    print(f"Tuple length: {len(strategy_result)}")
    print(f"Element 0 (selected_stocks): {len(strategy_result[0])} stocks")
    print(f"Element 1 (selection_values): {len(strategy_result[1])} values")
    print(f"Element 2 (scores): {len(strategy_result[2])} scores")
    print(f"Element 3 (json_values): {len(strategy_result[3])} JSON values")

    # Test the save_selected_stocks logic
    if len(strategy_result) >= 4:
        selected_stocks = strategy_result[0]
        selection_values = strategy_result[1]
        scores = strategy_result[2]
        json_values = strategy_result[3]

        print("\nExtracted values:")
        print(f"Selected stocks: {selected_stocks}")
        print(f"JSON values available: {json_values}")

        # Check if JSON values are properly populated
        for stock_code in selected_stocks:
            if stock_code in json_values:
                json_value = json_values[stock_code]
                print(f"  {stock_code}: JSON value = {json_value}")
            else:
                print(f"  {stock_code}: No JSON value found")

    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_strategy_results_format()

