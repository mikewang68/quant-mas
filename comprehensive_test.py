#!/usr/bin/env python3
"""
Comprehensive test to verify the weekly selector fix
"""

import sys
import os
import traceback

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Mock database manager to avoid connection issues
class MockDBManager:
    def get_strategies(self):
        return [{
            "_id": "68a6591d8dace06d7edd9582",
            "name": "三均线多头排列策略（基本型）",
            "type": "technical",
            "description": "使用斐波那契数列设置3均线，分别是5,13,34,均线多头排列",
            "parameters": {
                "ma_long": "34",
                "ma_mid": "13",
                "ma_short": "5"
            },
            "program": {
                "file": "three_ma_bullish_arrangement_strategy",
                "class": "ThreeMABullishArrangementStrategy"
            },
            "created_at": "2025-08-15",
            "class_name": "ThreeMABullishArrangementStrategy",
            "file": "three_ma_bullish_arrangement_strategy"
        }]

    def get_stock_codes(self):
        # Return a small list for testing
        return ["000001", "000002", "600000"]

    def save_selected_stocks(self, agent_name, stocks, date, strategy_params, additional_metadata=None):
        print(f"Mock save_selected_stocks called with {len(stocks)} stocks")
        return True

# Mock data fetcher
class MockDataFetcher:
    def get_stock_list(self):
        # Return a small list for testing
        return ["000001", "000002", "600000"]

    def get_k_data(self, code, period="week", count=50):
        # Create mock data
        import pandas as pd
        import numpy as np

        dates = pd.date_range('2024-01-01', periods=50, freq='W')
        data = pd.DataFrame({
            'date': dates,
            'open': np.random.rand(50) * 10 + 20,
            'high': np.random.rand(50) * 10 + 25,
            'low': np.random.rand(50) * 10 + 15,
            'close': np.linspace(20, 30, 50) + np.random.rand(50) * 0.5,  # Upward trend
            'volume': np.random.rand(50) * 1000000,
            'amount': np.random.rand(50) * 10000000
        })
        return data

def test_weekly_selector():
    """Test the weekly selector with the fix"""
    print("Testing weekly selector with unpacking fix...")

    try:
        # Import after setting up mocks
        from agents.weekly_selector import WeeklyStockSelector

        # Create instances
        db_manager = MockDBManager()
        data_fetcher = MockDataFetcher()

        # Create selector
        selector = WeeklyStockSelector(db_manager, data_fetcher)

        print(f"Strategy loaded: {selector.strategy_name}")
        print(f"Strategy params: {selector.strategy_params}")

        if selector.strategy_instance:
            print("Strategy instance created successfully")
            print(f"Strategy instance params: {selector.strategy_instance.params}")

            # Test _execute_strategy method
            print("\nTesting _execute_strategy method...")
            test_code = "000001"
            import pandas as pd
            import numpy as np

            # Create test data
            dates = pd.date_range('2024-01-01', periods=50, freq='W')
            test_data = pd.DataFrame({
                'date': dates,
                'open': np.random.rand(50) * 10 + 20,
                'high': np.random.rand(50) * 10 + 25,
                'low': np.random.rand(50) * 10 + 15,
                'close': np.linspace(20, 30, 50) + np.random.rand(50) * 0.5,
                'volume': np.random.rand(50) * 1000000,
                'amount': np.random.rand(50) * 10000000
            })

            result = selector._execute_strategy(test_code, test_data)
            print(f"_execute_strategy result: {result}")
            print(f"Result type: {type(result)}")
            print(f"Result length: {len(result)}")

            # Test unpacking the result
            print("\nTesting result unpacking...")
            if len(result) >= 4:
                meets_criteria, score, golden_cross, technical_analysis = result
                print("✓ Successfully unpacked 4 values:")
                print(f"  meets_criteria: {meets_criteria}")
                print(f"  score: {score}")
                print(f"  golden_cross: {golden_cross}")
                print(f"  technical_analysis type: {type(technical_analysis)}")
            else:
                print("✗ Result has unexpected length")

            # Test select_stocks method
            print("\nTesting select_stocks method...")
            selected_stocks, last_data_date, golden_cross_flags, selected_scores, technical_analysis_data = selector.select_stocks()
            print(f"Selected stocks: {selected_stocks}")

    except Exception as e:
        print(f"Error during testing: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_weekly_selector()

