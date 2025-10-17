"""
Test script for Bullish Golden Cross Volume Strategy
"""

import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.bullish_golden_cross_volume_strategy import BullishGoldenCrossVolumeStrategy


def test_strategy_initialization():
    """Test strategy initialization"""
    print("Testing strategy initialization...")

    # Test with default parameters
    strategy = BullishGoldenCrossVolumeStrategy()
    assert strategy.name == "趋势-多头金叉放量策略"
    assert strategy.ma_fast == 5
    assert strategy.ma_mid == 10
    assert strategy.ma_slow == 20
    assert strategy.volume_ma_period == 5
    assert strategy.volume_multiplier == 1.5
    print("✓ Default parameters initialized correctly")

    # Test with custom parameters
    custom_params = {
        "ma_fast": 8,
        "ma_mid": 13,
        "ma_slow": 21,
        "volume_ma_period": 8,
        "volume_multiplier": 2.0
    }
    strategy2 = BullishGoldenCrossVolumeStrategy(params=custom_params)
    assert strategy2.ma_fast == 8
    assert strategy2.ma_mid == 13
    assert strategy2.ma_slow == 21
    assert strategy2.volume_ma_period == 8
    assert strategy2.volume_multiplier == 2.0
    print("✓ Custom parameters initialized correctly")


def test_golden_cross_detection():
    """Test golden cross detection logic"""
    print("\nTesting golden cross detection...")

    strategy = BullishGoldenCrossVolumeStrategy()

    # Create test data with golden cross pattern
    dates = pd.date_range("2023-01-01", periods=30, freq="D")

    # Create data where MA5 crosses above MA10 and MA10 crosses above MA20
    close_prices = np.array([
        10.0, 10.1, 10.2, 10.3, 10.4,  # MA5: 10.2
        10.5, 10.6, 10.7, 10.8, 10.9,  # MA5: 10.7
        11.0, 11.1, 11.2, 11.3, 11.4,  # MA5: 11.2
        11.5, 11.6, 11.7, 11.8, 11.9,  # MA5: 11.7
        12.0, 12.1, 12.2, 12.3, 12.4,  # MA5: 12.2
        12.5, 12.6, 12.7, 12.8, 12.9   # MA5: 12.7
    ])

    test_data = pd.DataFrame({
        'date': dates,
        'open': close_prices,
        'high': close_prices + 0.1,
        'low': close_prices - 0.1,
        'close': close_prices,
        'volume': np.full(30, 1000000)
    })

    # Test golden cross detection
    golden_cross = strategy._detect_golden_cross(test_data)
    print(f"Golden cross detected: {golden_cross}")

    # Test with insufficient data
    insufficient_data = test_data.iloc[:10]  # Not enough data for MA20
    golden_cross_insufficient = strategy._detect_golden_cross(insufficient_data)
    assert golden_cross_insufficient == False
    print("✓ Insufficient data handled correctly")


def test_score_calculation():
    """Test score calculation logic"""
    print("\nTesting score calculation...")

    strategy = BullishGoldenCrossVolumeStrategy()

    # Test with golden cross and high volume
    score1 = strategy._calculate_score(
        ma_fast=12.0,
        ma_mid=11.5,
        ma_slow=11.0,
        volume_ratio=2.0,  # 2x volume
        golden_cross_condition=True
    )
    print(f"Score with golden cross and 2x volume: {score1}")
    assert score1 > 80  # Should be high score

    # Test with golden cross and normal volume
    score2 = strategy._calculate_score(
        ma_fast=12.0,
        ma_mid=11.5,
        ma_slow=11.0,
        volume_ratio=1.2,  # 1.2x volume
        golden_cross_condition=True
    )
    print(f"Score with golden cross and 1.2x volume: {score2}")
    assert 60 <= score2 < 80  # Should be medium score

    # Test without golden cross
    score3 = strategy._calculate_score(
        ma_fast=12.0,
        ma_mid=11.5,
        ma_slow=11.0,
        volume_ratio=2.0,
        golden_cross_condition=False
    )
    print(f"Score without golden cross: {score3}")
    assert score3 == 0  # Should be 0 without golden cross

    print("✓ Score calculation working correctly")


def test_analyze_method():
    """Test the main analyze method"""
    print("\nTesting analyze method...")

    strategy = BullishGoldenCrossVolumeStrategy()

    # Create test data with golden cross and volume amplification
    dates = pd.date_range("2023-01-01", periods=25, freq="D")

    # Create price data that will generate golden cross
    close_prices = np.array([
        10.0, 10.1, 10.2, 10.3, 10.4,  # MA5: 10.2
        10.5, 10.6, 10.7, 10.8, 10.9,  # MA5: 10.7
        11.0, 11.1, 11.2, 11.3, 11.4,  # MA5: 11.2
        11.5, 11.6, 11.7, 11.8, 11.9,  # MA5: 11.7
        12.0, 12.1, 12.2, 12.3, 12.4   # MA5: 12.2
    ])

    # Create volume data with amplification at the end
    volume_data = np.full(25, 1000000)
    volume_data[-1] = 2000000  # 2x volume on last day

    test_data = pd.DataFrame({
        'date': dates,
        'open': close_prices,
        'high': close_prices + 0.1,
        'low': close_prices - 0.1,
        'close': close_prices,
        'volume': volume_data
    })

    # Test analysis
    meets_criteria, score, value = strategy.analyze(test_data, "000001")

    print(f"Meets criteria: {meets_criteria}")
    print(f"Score: {score}")

    # Parse value to check structure
    import json
    value_data = json.loads(value)
    print(f"Selection reason: {value_data.get('selection_reason', '')}")
    print(f"Golden cross signal: {value_data.get('golden_cross_signal', False)}")
    print(f"Position: {value_data.get('position', 0.0)}")

    # Should meet criteria if golden cross and volume conditions are met
    if meets_criteria:
        print("✓ Strategy correctly identified golden cross startup signal")
    else:
        print("✗ Strategy did not identify the signal (may need parameter tuning)")


def test_generate_signals():
    """Test signal generation"""
    print("\nTesting signal generation...")

    strategy = BullishGoldenCrossVolumeStrategy()

    # Create test data
    dates = pd.date_range("2023-01-01", periods=30, freq="D")

    # Create price data that will generate golden cross
    close_prices = np.array([
        10.0, 10.1, 10.2, 10.3, 10.4,  # MA5: 10.2
        10.5, 10.6, 10.7, 10.8, 10.9,  # MA5: 10.7
        11.0, 11.1, 11.2, 11.3, 11.4,  # MA5: 11.2
        11.5, 11.6, 11.7, 11.8, 11.9,  # MA5: 11.7
        12.0, 12.1, 12.2, 12.3, 12.4,  # MA5: 12.2
        12.5, 12.6, 12.7, 12.8, 12.9   # MA5: 12.7
    ])

    # Create volume data with amplification
    volume_data = np.full(30, 1000000)
    volume_data[20:25] = 2000000  # Volume amplification during golden cross period

    test_data = pd.DataFrame({
        'date': dates,
        'open': close_prices,
        'high': close_prices + 0.1,
        'low': close_prices - 0.1,
        'close': close_prices,
        'volume': volume_data
    })

    # Generate signals
    signals = strategy.generate_signals(test_data)

    print(f"Total signals generated: {len(signals)}")
    print(f"Buy signals: {len(signals[signals['signal'] == 'BUY'])}")

    # Check if any buy signals were generated
    buy_signals = signals[signals['signal'] == 'BUY']
    if len(buy_signals) > 0:
        print("✓ Buy signals generated successfully")
        print("Sample buy signals:")
        print(buy_signals.head())
    else:
        print("✗ No buy signals generated (may need parameter tuning)")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Bullish Golden Cross Volume Strategy")
    print("=" * 60)

    try:
        test_strategy_initialization()
        test_golden_cross_detection()
        test_score_calculation()
        test_analyze_method()
        test_generate_signals()

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("Strategy now focuses on detecting golden cross startup signals")
        print("with simplified conditions: only golden cross and volume amplification")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

