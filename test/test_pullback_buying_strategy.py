"""
Test script for Pullback Buying Strategy
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.pullback_buying_strategy import PullbackBuyingStrategy

def test_pullback_buying_strategy():
    """Test the Pullback Buying Strategy"""
    print("Testing Pullback Buying Strategy...")

    # Initialize strategy
    strategy = PullbackBuyingStrategy()
    print(f"Strategy initialized: {strategy.name}")

    # Create sample data
    dates = pd.date_range('2023-01-01', periods=50, freq='D')
    sample_data = pd.DataFrame({
        'date': dates,
        'open': np.random.uniform(100, 110, 50),
        'high': np.random.uniform(110, 120, 50),
        'low': np.random.uniform(90, 100, 50),
        'close': np.random.uniform(100, 110, 50),
        'volume': np.random.uniform(1000000, 2000000, 50)
    })

    print(f"Sample data created with {len(sample_data)} rows")

    # Test analyze method
    print("\nTesting analyze method...")
    meets_criteria, score, value = strategy.analyze(sample_data, "000001")

    print(f"Meets criteria: {meets_criteria}")
    print(f"Score: {score}")
    print(f"Value (JSON): {value}")

    # Parse JSON value
    import json
    try:
        value_data = json.loads(value)
        print(f"Parsed value: {value_data}")
        print(f"Code: {value_data.get('code')}")
        print(f"Selection reason: {value_data.get('selection_reason')}")
        print(f"Technical analysis: {value_data.get('technical_analysis')}")
        print(f"Pullback signal: {value_data.get('pullback_signal')}")
        print(f"Position: {value_data.get('position')}")
    except Exception as e:
        print(f"Error parsing JSON: {e}")

    # Test get_technical_analysis_data method
    print("\nTesting get_technical_analysis_data method...")
    tech_data = strategy.get_technical_analysis_data(sample_data)
    print(f"Technical analysis data: {tech_data}")

    # Test generate_signals method
    print("\nTesting generate_signals method...")
    signals = strategy.generate_signals(sample_data)
    print(f"Generated {len(signals[signals['signal'] != 'HOLD'])} trading signals")
    print(signals.tail(10))

    print("\nPullback Buying Strategy test completed successfully!")

if __name__ == "__main__":
    test_pullback_buying_strategy()

