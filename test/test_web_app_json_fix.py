"""
Test script to verify Web app JSON value handling for trend selection
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector

def test_web_app_json_handling():
    """Test Web app JSON value handling for trend selection"""

    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Simulate Web app logic
        selected_stocks = ["000001", "000002", "600036"]  # Test stocks
        all_selected_scores = {
            "000001": 0.85,
            "000002": 0.72,
            "600036": 0.91
        }

        # Build proper json_values dictionary as in the fixed Web app code
        strategy_results = {}
        strategy_name = "测试趋势策略"

        json_values = {}
        for stock_code in selected_stocks:
            # Create proper JSON value structure for each stock
            json_value = {
                "code": stock_code,
                "score": all_selected_scores.get(stock_code, 0.0),
                "selection_reason": f"趋势选股策略 {strategy_name} 选中",
                "technical_analysis": {},
                "breakout_signal": 0,
                "position": 0.0
            }
            json_values[stock_code] = json.dumps(json_value)

        strategy_results[strategy_name] = (
            selected_stocks,
            {},  # Empty selection_values dictionary
            all_selected_scores,
            json_values,  # Proper json_values dictionary with actual JSON data
        )

        print("✅ Web app JSON value handling test:")
        print(f"  - Strategy name: {strategy_name}")
        print(f"  - Selected stocks: {selected_stocks}")
        print(f"  - Scores: {all_selected_scores}")
        print(f"  - JSON values type: {type(json_values)}")
        print(f"  - JSON values count: {len(json_values)}")

        # Verify JSON values
        for stock_code, json_str in json_values.items():
            parsed_json = json.loads(json_str)
            print(f"\n  Stock {stock_code}:")
            print(f"    - Score in JSON: {parsed_json.get('score')}")
            print(f"    - Selection reason: {parsed_json.get('selection_reason')}")
            print(f"    - JSON keys: {list(parsed_json.keys())}")

        # Test Weekly Selector save method
        selector = WeeklyStockSelector(db_manager, data_fetcher)

        print("\n✅ Testing Weekly Selector save method...")
        save_result = selector.save_selected_stocks(strategy_results)
        print(f"  - Save result: {save_result}")

        # Verify data was saved to database
        pool_data = db_manager.get_pool_data()
        if pool_data:
            latest_record = pool_data[-1]  # Get the latest record
            print(f"\n✅ Latest pool record:")
            print(f"  - Strategy key: {latest_record.get('strategy_key')}")
            print(f"  - Stocks count: {len(latest_record.get('stocks', []))}")

            # Check if value fields are populated
            for stock in latest_record.get('stocks', [])[:2]:  # Check first 2 stocks
                code = stock.get('code')
                trend_data = stock.get('trend', {})
                if trend_data:
                    for strategy_name, strategy_data in trend_data.items():
                        print(f"\n  Stock {code} - {strategy_name}:")
                        print(f"    - Score: {strategy_data.get('score')}")
                        print(f"    - Value type: {type(strategy_data.get('value'))}")
                        print(f"    - Value length: {len(strategy_data.get('value', ''))}")

                        # Try to parse value as JSON
                        value_str = strategy_data.get('value', '')
                        if value_str:
                            try:
                                parsed_value = json.loads(value_str)
                                print(f"    - Value parsed successfully")
                                print(f"    - Value keys: {list(parsed_value.keys())}")
                            except:
                                print(f"    - Value is not valid JSON")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_web_app_json_handling()
    if success:
        print("\n✅ Web app JSON value handling test PASSED")
    else:
        print("\n❌ Web app JSON value handling test FAILED")

