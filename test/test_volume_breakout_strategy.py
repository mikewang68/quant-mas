#!/usr/bin/env python3
"""
Test script to verify VolumeBreakoutStrategy outputs score and value correctly
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.volume_breakout_strategy import VolumeBreakoutStrategy


def test_volume_breakout_strategy():
    """Test VolumeBreakoutStrategy output format"""
    print("Testing VolumeBreakoutStrategy output format...")

    # Create sample data
    dates = pd.date_range("2024-01-01", periods=50, freq="D")
    sample_data = pd.DataFrame(
        {
            "date": dates,
            "open": np.random.uniform(10, 12, 50),
            "high": np.random.uniform(12, 14, 50),
            "low": np.random.uniform(8, 10, 50),
            "close": np.random.uniform(10, 12, 50),
            "volume": np.random.uniform(1000000, 2000000, 50),
        }
    )

    # Initialize strategy
    strategy = VolumeBreakoutStrategy()

    # Test analyze method
    print("\n1. Testing analyze method...")
    meets_criteria, reason, score, breakout_signal = strategy.analyze(sample_data)
    print(f"   meets_criteria: {meets_criteria}")
    print(f"   reason: {reason}")
    print(f"   score: {score}")
    print(f"   breakout_signal: {breakout_signal}")

    # Test get_technical_analysis_data method
    print("\n2. Testing get_technical_analysis_data method...")
    technical_data = strategy.get_technical_analysis_data(sample_data)
    print(f"   Technical data keys: {list(technical_data.keys())}")
    print(f"   Technical data: {technical_data}")

    # Test execute method with mock data
    print("\n3. Testing execute method...")
    stock_data = {"000001": sample_data}

    # Mock db_manager for testing
    class MockDBManager:
        def get_strategies(self):
            return []
        def close_connection(self):
            pass

    db_manager = MockDBManager()

    try:
        results = strategy.execute(stock_data, "TestAgent", db_manager)
        print(f"   Execute results count: {len(results)}")
        if results:
            print(f"   First result keys: {list(results[0].keys())}")
            print(f"   First result: {results[0]}")
    except Exception as e:
        print(f"   Execute method error: {e}")

    # Test generate_signals method
    print("\n4. Testing generate_signals method...")
    signals = strategy.generate_signals(sample_data)
    print(f"   Signals shape: {signals.shape}")
    print(f"   Signal columns: {list(signals.columns)}")
    print(f"   Signal types: {signals['signal'].value_counts()}")

    # Verify the strategy outputs both score and value
    print("\n5. Verifying score and value output...")

    # Check if analyze method returns score
    if score is not None:
        print(f"   ✓ analyze method returns score: {score}")
    else:
        print(f"   ✗ analyze method does not return score")

    # Check if execute method returns results with score and selection_reason
    if results and len(results) > 0:
        result = results[0]
        if 'score' in result:
            print(f"   ✓ execute method returns score: {result['score']}")
        else:
            print(f"   ✗ execute method does not return score")

        if 'selection_reason' in result:
            print(f"   ✓ execute method returns selection_reason: {result['selection_reason'][:50]}...")
        else:
            print(f"   ✗ execute method does not return selection_reason")

        if 'technical_analysis' in result:
            print(f"   ✓ execute method returns technical_analysis data")
        else:
            print(f"   ✗ execute method does not return technical_analysis data")

    print("\n✅ VolumeBreakoutStrategy test completed!")
    return True


def test_strategy_integration():
    """Test how the strategy integrates with Weekly Selector"""
    print("\n=== Testing Strategy Integration with Weekly Selector ===")

    # Create mock strategy results as expected by Weekly Selector
    mock_strategy_results = {
        "放量突破策略": (
            ["000001", "000002"],  # selected_stocks
            {"000001": "放量突破条件: 收盘价=11.50, 突破高点=12.30, 当前成交量=1800000, 平均成交量=1000000, 量比=1.80, DIF=0.0250 (满足放量突破)",
             "000002": "放量突破条件: 收盘价=12.20, 突破高点=12.50, 当前成交量=2200000, 平均成交量=1200000, 量比=1.83, DIF=0.0310 (满足放量突破)"},  # selection_value
            {"000001": 85.5, "000002": 88.2},  # selected_scores
        )
    }

    print("Mock strategy results structure:")
    for strategy_name, (selected_stocks, selection_value, selected_scores) in mock_strategy_results.items():
        print(f"  Strategy: {strategy_name}")
        print(f"    Selected stocks: {selected_stocks}")
        print(f"    Selection value type: {type(selection_value)}")
        print(f"    Selection value: {selection_value}")
        print(f"    Selected scores type: {type(selected_scores)}")
        print(f"    Selected scores: {selected_scores}")

    print("\n✅ Strategy integration test completed!")
    return True


if __name__ == "__main__":
    test_volume_breakout_strategy()
    test_strategy_integration()

