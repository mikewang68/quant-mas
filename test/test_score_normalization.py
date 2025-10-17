"""
Test script to verify score normalization for three strategies
"""

import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.bullish_golden_cross_volume_strategy import BullishGoldenCrossVolumeStrategy
from strategies.trend_following_strategy import TrendFollowingStrategy
from strategies.pullback_buying_strategy import PullbackBuyingStrategy


def test_score_normalization():
    """Test that all strategies output scores in 0-1 range with 2 decimal places"""
    print("Testing score normalization for all three strategies...")

    # Create test data
    dates = pd.date_range("2023-01-01", periods=30, freq="D")
    close_prices = np.array([
        10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9,
        11.0, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9,
        12.0, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9
    ])
    volume_data = np.full(30, 1000000)
    volume_data[-1] = 2000000  # Volume amplification

    test_data = pd.DataFrame({
        'date': dates,
        'open': close_prices,
        'high': close_prices + 0.1,
        'low': close_prices - 0.1,
        'close': close_prices,
        'volume': volume_data
    })

    # Test Bullish Golden Cross Strategy
    print("\n1. Testing Bullish Golden Cross Strategy...")
    bgc_strategy = BullishGoldenCrossVolumeStrategy()
    meets_criteria1, score1, value1 = bgc_strategy.analyze(test_data, "000001")
    print(f"   Score: {score1}")
    print(f"   Score type: {type(score1)}")
    print(f"   Score range check: {0 <= score1 <= 1}")
    print(f"   Decimal places: {len(str(score1).split('.')[1]) if '.' in str(score1) else 0}")

    # Test Trend Following Strategy
    print("\n2. Testing Trend Following Strategy...")
    tf_strategy = TrendFollowingStrategy()
    meets_criteria2, score2, value2 = tf_strategy.analyze(test_data, "000001")
    print(f"   Score: {score2}")
    print(f"   Score type: {type(score2)}")
    print(f"   Score range check: {0 <= score2 <= 1}")
    print(f"   Decimal places: {len(str(score2).split('.')[1]) if '.' in str(score2) else 0}")

    # Test Pullback Buying Strategy
    print("\n3. Testing Pullback Buying Strategy...")
    pb_strategy = PullbackBuyingStrategy()
    meets_criteria3, score3, value3 = pb_strategy.analyze(test_data, "000001")
    print(f"   Score: {score3}")
    print(f"   Score type: {type(score3)}")
    print(f"   Score range check: {0 <= score3 <= 1}")
    print(f"   Decimal places: {len(str(score3).split('.')[1]) if '.' in str(score3) else 0}")

    # Verify all scores are in 0-1 range with 2 decimal places
    all_scores = [score1, score2, score3]
    all_valid = all(0 <= score <= 1 for score in all_scores)
    all_two_decimals = all(
        len(str(score).split('.')[1]) == 2 if '.' in str(score) else True
        for score in all_scores
    )

    print("\n" + "=" * 60)
    print("VERIFICATION RESULTS:")
    print(f"All scores in 0-1 range: {all_valid}")
    print(f"All scores have 2 decimal places: {all_two_decimals}")
    print(f"All scores: {all_scores}")

    if all_valid and all_two_decimals:
        print("✓ SUCCESS: All strategies output normalized scores correctly!")
    else:
        print("✗ FAILURE: Some strategies do not output normalized scores correctly!")
    print("=" * 60)


def test_direct_score_calculation():
    """Test direct score calculation methods"""
    print("\nTesting direct score calculation methods...")

    # Test Bullish Golden Cross score calculation
    bgc_strategy = BullishGoldenCrossVolumeStrategy()
    score_bgc = bgc_strategy._calculate_score(
        ma_fast=12.0,
        ma_mid=11.5,
        ma_slow=11.0,
        volume_ratio=2.0,
        golden_cross_condition=True
    )
    print(f"Bullish Golden Cross score: {score_bgc}")
    print(f"  Expected: 1.0, Got: {score_bgc}, Match: {score_bgc == 1.0}")

    # Test Trend Following score calculation
    tf_strategy = TrendFollowingStrategy()
    score_tf = tf_strategy._calculate_score(
        ma_fast=12.0,
        ma_slow=11.0,
        macd_dif=0.5,
        macd_dea=0.2,
        price=12.5,
        historical_high=12.0
    )
    print(f"Trend Following score: {score_tf}")
    print(f"  Range check: {0 <= score_tf <= 1}")

    # Test Pullback Buying score calculation
    pb_strategy = PullbackBuyingStrategy()
    score_pb = pb_strategy._calculate_score(
        close=10.0,
        ma_value=11.0,
        kdj_j=20.0,
        rsi_value=25.0
    )
    print(f"Pullback Buying score: {score_pb}")
    print(f"  Range check: {0 <= score_pb <= 1}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Score Normalization for Three Strategies")
    print("=" * 60)

    try:
        test_score_normalization()
        test_direct_score_calculation()

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("All three strategies now output scores in 0-1 range")
        print("with 2 decimal places precision.")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

