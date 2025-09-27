#!/usr/bin/env python3
"""
Test script for VWAP Turnover Strategy
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from strategies.vmap_turnover_strategy import VMAPTurnoverStrategy

def create_test_data():
    """Create sample test data for the strategy"""
    # Create sample data with clear trend and turnover rate
    dates = pd.date_range('2023-01-01', periods=50, freq='D')

    # Create upward trending price data
    base_prices = np.linspace(10, 15, 50)  # Rising from 10 to 15
    noise = np.random.normal(0, 0.2, 50)  # Add some noise
    prices = base_prices + noise

    # Ensure the last few values show clear upward momentum
    prices[-5:] = np.linspace(14.5, 15.5, 5)  # Accelerating upward

    # Create sample data DataFrame
    data = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': prices + np.random.uniform(0, 0.3, 50),
        'low': prices - np.random.uniform(0, 0.3, 50),
        'close': prices,
        'volume': np.random.uniform(1000000, 2000000, 50),
        'turnover_rate': np.random.uniform(8, 15, 50)  # Within 5-25% range
    })

    # Set the last turnover rate to a specific value for testing
    data.loc[data.index[-1], 'turnover_rate'] = 12.5

    return data

def test_vwap_turnover_strategy():
    """Test the VWAP Turnover Strategy"""
    print("Testing VWAP Turnover Strategy...")

    try:
        # Create strategy instance
        strategy = VMAPTurnoverStrategy(
            name="Test VWAP Turnover Strategy",
            params={
                "short_period": 5,
                "mid_period": 13,
                "min_turnover": 5.0,
                "max_turnover": 25.0
            }
        )

        print(f"Strategy initialized: {strategy.name}")
        print(f"Parameters: short_period={strategy.short_period}, mid_period={strategy.mid_period}")
        print(f"Turnover range: {strategy.min_turnover}-{strategy.max_turnover}%")

        # Create test data
        test_data = create_test_data()
        print(f"\nTest data created with {len(test_data)} records")
        print(f"Last close price: {test_data['close'].iloc[-1]:.2f}")
        print(f"Last turnover rate: {test_data['turnover_rate'].iloc[-1]:.2f}%")

        # Test analyze method
        meets_criteria, reason, score = strategy.analyze(test_data)
        print(f"\nAnalysis results:")
        print(f"  Meets criteria: {meets_criteria}")
        print(f"  Reason: {reason}")
        print(f"  Score: {score}")

        # Test execute method with mock stock data
        stock_data = {"000001": test_data}
        # Mock database manager (we won't actually save to database in this test)
        class MockDBManager:
            def __init__(self):
                pass

            @property
            def strategies_collection(self):
                class MockCollection:
                    def find_one(self, query):
                        return None
                return MockCollection()

        mock_db = MockDBManager()

        selected_stocks = strategy.execute(stock_data, "TestAgent", mock_db)
        print(f"\nExecute results:")
        print(f"  Selected stocks: {len(selected_stocks)}")
        if selected_stocks:
            print(f"  First stock code: {selected_stocks[0]['code']}")
            print(f"  Selection reason: {selected_stocks[0]['selection_reason']}")
            print(f"  Score: {selected_stocks[0]['score']}")

        # Test generate_signals method
        signals = strategy.generate_signals(test_data)
        print(f"\nSignal generation:")
        print(f"  Total signals: {len(signals)}")
        if not signals.empty:
            last_signal = signals['signal'].iloc[-1]
            last_position = signals['position'].iloc[-1]
            print(f"  Last signal: {last_signal}")
            print(f"  Last position: {last_position}")

        print("\nTest completed successfully!")
        return True

    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vwap_turnover_strategy()
    if success:
        print("\n✓ VWAP Turnover Strategy test completed successfully")
        sys.exit(0)
    else:
        print("\n✗ VWAP Turnover Strategy test failed")
        sys.exit(1)

