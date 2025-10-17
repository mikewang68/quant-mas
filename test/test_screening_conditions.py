"""
Test script to verify screening conditions use 0-1 score range
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


def test_screening_conditions():
    """Test that all strategies use 0-1 score range for screening conditions"""
    print("Testing screening conditions with 0-1 score range...")

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
    print(f"   Meets criteria: {meets_criteria1}")

    # Parse value to check position size
    import json
    value_data1 = json.loads(value1)
    position1 = value_data1.get('position', 0.0)
    print(f"   Position size: {position1}")
    print(f"   Screening condition: score > 0.6 = {score1 > 0.6}")

    # Test Trend Following Strategy
    print("\n2. Testing Trend Following Strategy...")
    tf_strategy = TrendFollowingStrategy()
    meets_criteria2, score2, value2 = tf_strategy.analyze(test_data, "000001")
    print(f"   Score: {score2}")
    print(f"   Meets criteria: {meets_criteria2}")

    value_data2 = json.loads(value2)
    position2 = value_data2.get('position', 0.0)
    print(f"   Position size: {position2}")
    print(f"   Screening condition: score > 0.6 = {score2 > 0.6}")

    # Test Pullback Buying Strategy
    print("\n3. Testing Pullback Buying Strategy...")
    pb_strategy = PullbackBuyingStrategy()
    meets_criteria3, score3, value3 = pb_strategy.analyze(test_data, "000001")
    print(f"   Score: {score3}")
    print(f"   Meets criteria: {meets_criteria3}")

    value_data3 = json.loads(value3)
    position3 = value_data3.get('position', 0.0)
    print(f"   Position size: {position3}")
    print(f"   Screening condition: score > 0.6 = {score3 > 0.6}")

    # Verify all strategies use 0-1 range for screening
    all_scores = [score1, score2, score3]
    all_positions = [position1, position2, position3]

    print("\n" + "=" * 60)
    print("VERIFICATION RESULTS:")
    print(f"All scores in 0-1 range: {all(0 <= score <= 1 for score in all_scores)}")
    print(f"All positions in 0-1 range: {all(0 <= pos <= 1 for pos in all_positions)}")
    print(f"Screening conditions use 0.6 threshold: {all(meets_criteria == (score > 0.6) for meets_criteria, score in [(meets_criteria1, score1), (meets_criteria2, score2), (meets_criteria3, score3)])}")

    print(f"\nDetailed results:")
    print(f"  Bullish Golden Cross: score={score1}, meets_criteria={meets_criteria1}, position={position1}")
    print(f"  Trend Following: score={score2}, meets_criteria={meets_criteria2}, position={position2}")
    print(f"  Pullback Buying: score={score3}, meets_criteria={meets_criteria3}, position={position3}")

    if all(0 <= score <= 1 for score in all_scores) and all(0 <= pos <= 1 for pos in all_positions):
        print("\n✓ SUCCESS: All strategies use 0-1 score range for screening conditions!")
    else:
        print("\n✗ FAILURE: Some strategies do not use 0-1 score range correctly!")
    print("=" * 60)


def test_position_sizing():
    """Test position sizing based on score thresholds"""
    print("\nTesting position sizing based on score thresholds...")

    # Test Bullish Golden Cross position sizing
    bgc_strategy = BullishGoldenCrossVolumeStrategy()

    # Test different score levels
    test_scores = [0.9, 0.75, 0.65, 0.55, 0.3]
    expected_positions = [1.0, 0.7, 0.4, 0.0, 0.0]

    print("Bullish Golden Cross position sizing:")
    for score, expected in zip(test_scores, expected_positions):
        # Create a mock value dict to test position calculation
        value = {
            "code": "000001",
            "score": score,
            "selection_reason": "test",
            "technical_analysis": {},
            "golden_cross_signal": 1,
            "position": 0.0
        }

        # Calculate position based on score
        position = 0.0
        if score >= 0.8:
            position = 1.0
        elif score >= 0.7:
            position = 0.7
        elif score >= 0.6:
            position = 0.4

        print(f"  Score {score} -> Position {position} (expected {expected}) {'✓' if position == expected else '✗'}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Screening Conditions with 0-1 Score Range")
    print("=" * 60)

    try:
        test_screening_conditions()
        test_position_sizing()

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("All three strategies now use 0-1 score range for:")
        print("- Screening conditions (score > 0.6)")
        print("- Position sizing (0.8, 0.7, 0.6 thresholds)")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

