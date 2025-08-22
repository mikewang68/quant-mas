#!/usr/bin/env python3
"""
Debug script to check parameter mapping in ThreeMABullishArrangementStrategy
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

def test_parameter_mapping():
    """Test the parameter mapping functionality"""
    print("Testing parameter mapping...")

    # Simulate database parameters
    db_params = {
        "ma_short": "5",
        "ma_mid": "13",
        "ma_long": "34"
    }

    print(f"Database parameters: {db_params}")

    # Test the parameter mapping logic from the strategy
    if db_params:
        # Map database parameter names to strategy parameter names
        mapped_params = db_params.copy()
        print(f"Copied parameters: {mapped_params}")

        # Handle different parameter naming conventions
        if "ma_short" in mapped_params and "short" not in mapped_params:
            mapped_params["short"] = int(mapped_params["ma_short"])
        if "ma_mid" in mapped_params and "mid" not in mapped_params:
            mapped_params["mid"] = int(mapped_params["ma_mid"])
        if "ma_long" in mapped_params and "long" not in mapped_params:
            mapped_params["long"] = int(mapped_params["ma_long"])

        # Ensure existing parameters are integers where needed
        if "short" in mapped_params:
            mapped_params["short"] = int(mapped_params["short"])
        if "mid" in mapped_params:
            mapped_params["mid"] = int(mapped_params["mid"])
        if "long" in mapped_params:
            mapped_params["long"] = int(mapped_params["long"])

        print(f"Mapped parameters: {mapped_params}")

        # Create strategy instance with mapped parameters
        strategy = ThreeMABullishArrangementStrategy(params=mapped_params)
        print(f"Strategy params: {strategy.params}")

        # Test accessing the parameters
        try:
            short_val = strategy.params["short"]
            mid_val = strategy.params["mid"]
            long_val = strategy.params["long"]
            print(f"Successfully accessed parameters: short={short_val}, mid={mid_val}, long={long_val}")
        except Exception as e:
            print(f"Error accessing parameters: {e}")

if __name__ == "__main__":
    test_parameter_mapping()

