#!/usr/bin/env python3
"""
Debug script to understand the difference between analyze and generate_signals methods
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

def debug_strategy_logic():
    """Debug the difference between analyze and generate_signals methods"""
    print("Debugging strategy logic difference...")

    # Create strategy instance
    strategy_params = {
        'short': 5,
        'mid': 13,
        'long': 34
    }
    strategy = ThreeMABullishArrangementStrategy(params=strategy_params)

    # Create data with clear bullish arrangement but no golden cross
    dates = pd.date_range('2024-01-01', periods=100, freq='W')  # Weekly data
    # Create upward trending prices with consistent pattern (no crossover)
    close_prices = np.linspace(100, 150, 100)  # Strong upward trend

    data = pd.DataFrame({
        'date': dates,
        'open': close_prices * 0.99,
        'high': close_prices * 1.01,
        'low': close_prices * 0.99,
        'close': close_prices,
        'volume': np.full(100, 1500000),
        'amount': close_prices * 1500000
    })

    print(f"Data shape: {data.shape}")
    print(f"Last few close prices: {data['close'].tail().tolist()}")

    # Test analyze method
    print(f"\n--- Analyze method ---")
    meets_criteria, reason, score, golden_cross = strategy.analyze(data)
    print(f"Meets criteria: {meets_criteria}")
    print(f"Reason: {reason}")
    print(f"Score: {score}")
    print(f"Golden cross detected: {golden_cross}")

    # Test generate_signals method
    print(f"\n--- Generate signals method ---")
    signals = strategy.generate_signals(data)
    print(f"Signals shape: {signals.shape}")
    if len(signals) > 0:
        print(f"Last signal: {signals.iloc[-1]['signal']}")
        print(f"Last position: {signals.iloc[-1]['position']}")

    # Let's manually check for golden cross in this data
    print(f"\n--- Manual golden cross check ---")
    close_prices_array = np.array(data['close'].values, dtype=np.float64)
    ma_short = pd.Series(close_prices_array).rolling(window=5).mean().values
    ma_mid = pd.Series(close_prices_array).rolling(window=13).mean().values

    print(f"MA5 last few values: {ma_short[-5:]}")
    print(f"MA13 last few values: {ma_mid[-5:]}")

    # Check for golden cross
    if len(ma_short) >= 2 and len(ma_mid) >= 2:
        current_short_above_mid = ma_short[-1] > ma_mid[-1]
        previous_short_below_mid = ma_short[-2] <= ma_mid[-2]
        golden_cross_detected = current_short_above_mid and previous_short_below_mid
        print(f"Current MA5 > MA13: {current_short_above_mid}")
        print(f"Previous MA5 <= MA13: {previous_short_below_mid}")
        print(f"Golden cross detected: {golden_cross_detected}")

    # Now create data that should have a golden cross
    print(f"\n--- Creating data with golden cross ---")
    # Create data where short MA crosses above mid MA
    cross_data = data.copy()
    # Modify the last few prices to create a cross
    cross_prices = cross_data['close'].values
    # Make the last few prices higher to ensure short MA crosses above mid MA
    cross_prices[-3:] = np.linspace(145, 155, 3)  # Sharp upward movement at the end

    cross_data['close'] = cross_prices

    print(f"Cross data last few close prices: {cross_data['close'].tail().tolist()}")

    # Test with cross data
    cross_meets_criteria, cross_reason, cross_score, cross_golden_cross = strategy.analyze(cross_data)
    print(f"\nCross data analyze - Meets criteria: {cross_meets_criteria}")
    print(f"Cross data analyze - Reason: {cross_reason}")

    cross_signals = strategy.generate_signals(cross_data)
    if len(cross_signals) > 0:
        print(f"Cross data last signal: {cross_signals.iloc[-1]['signal']}")

    # Manual check for golden cross in cross data
    cross_close_array = np.array(cross_data['close'].values, dtype=np.float64)
    cross_ma_short = pd.Series(cross_close_array).rolling(window=5).mean().values
    cross_ma_mid = pd.Series(cross_close_array).rolling(window=13).mean().values

    print(f"Cross data MA5 last few values: {cross_ma_short[-5:]}")
    print(f"Cross data MA13 last few values: {cross_ma_mid[-5:]}")

    if len(cross_ma_short) >= 2 and len(cross_ma_mid) >= 2:
        cross_current_short_above_mid = cross_ma_short[-1] > cross_ma_mid[-1]
        cross_previous_short_below_mid = cross_ma_short[-2] <= cross_ma_mid[-2]
        cross_golden_cross_detected = cross_current_short_above_mid and cross_previous_short_below_mid
        print(f"Cross data - Current MA5 > MA13: {cross_current_short_above_mid}")
        print(f"Cross data - Previous MA5 <= MA13: {cross_previous_short_below_mid}")
        print(f"Cross data - Golden cross detected: {cross_golden_cross_detected}")

if __name__ == "__main__":
    try:
        debug_strategy_logic()
    except Exception as e:
        print(f"Debug failed with error: {e}")
        import traceback
        traceback.print_exc()

