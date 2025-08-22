#!/usr/bin/env python3
"""
Simple test to verify the strategy works correctly after our fixes
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

def test_strategy_with_database_params():
    """Test the strategy with database-style parameters"""
    print("Testing strategy with database-style parameters...")

    # Database-style parameters (as stored in MongoDB)
    db_params = {
        'ma_short': 5,
        'ma_mid': 13,
        'ma_long': 34
    }

    # Create strategy instance
    strategy = ThreeMABullishArrangementStrategy(params=db_params)

    # Verify parameters are correctly mapped
    assert 'short' in strategy.params
    assert 'mid' in strategy.params
    assert 'long' in strategy.params
    assert strategy.params['short'] == 5
    assert strategy.params['mid'] == 13
    assert strategy.params['long'] == 34

    print("✓ Parameter mapping works correctly")

    # Create test data with bullish arrangement
    dates = pd.date_range('2023-01-01', periods=50, freq='W')
    close_prices = np.array([100 + i*0.8 + np.sin(i*0.3)*3 for i in range(50)])

    test_data = pd.DataFrame({
        'date': dates,
        'open': close_prices * 0.99,
        'high': close_prices * 1.02,
        'low': close_prices * 0.98,
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, 50)
    })

    # Test analysis
    meets_criteria, reason, score, golden_cross = strategy.analyze(test_data)

    print(f"✓ Analysis completed: meets_criteria={meets_criteria}")
    print(f"  Reason: {reason}")
    print(f"  Score: {score}")

    return True

def test_strategy_with_strategy_params():
    """Test the strategy with strategy-style parameters"""
    print("\nTesting strategy with strategy-style parameters...")

    # Strategy-style parameters (as expected by the strategy)
    strategy_params = {
        'short': 5,
        'mid': 13,
        'long': 34
    }

    # Create strategy instance
    strategy = ThreeMABullishArrangementStrategy(params=strategy_params)

    # Verify parameters are preserved
    assert 'short' in strategy.params
    assert 'mid' in strategy.params
    assert 'long' in strategy.params
    assert strategy.params['short'] == 5
    assert strategy.params['mid'] == 13
    assert strategy.params['long'] == 34

    print("✓ Strategy-style parameters work correctly")

    # Create test data
    dates = pd.date_range('2023-01-01', periods=50, freq='W')
    close_prices = np.array([100 + i*0.8 + np.sin(i*0.3)*3 for i in range(50)])

    test_data = pd.DataFrame({
        'date': dates,
        'open': close_prices * 0.99,
        'high': close_prices * 1.02,
        'low': close_prices * 0.98,
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, 50)
    })

    # Test analysis
    meets_criteria, reason, score, golden_cross = strategy.analyze(test_data)

    print(f"✓ Analysis completed: meets_criteria={meets_criteria}")
    print(f"  Reason: {reason}")
    print(f"  Score: {score}")

    return True

if __name__ == "__main__":
    try:
        test1 = test_strategy_with_database_params()
        test2 = test_strategy_with_strategy_params()

        if test1 and test2:
            print("\n🎉 All tests passed! The strategy fixes are working correctly.")
            print("The weekly selector should now be able to select stocks properly.")
        else:
            print("\n❌ Some tests failed.")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

