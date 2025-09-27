#!/usr/bin/env python3
"""
Test script to verify the signal generator fix
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from agents.signal_generator import SignalGenerator
from utils.akshare_client import AkshareClient


def test_signal_generator_fix():
    """Test that the signal generator uses the correct strategy name"""
    print("Testing signal generator fix...")

    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Create signal generator instance
        signal_generator = SignalGenerator(db_manager, data_fetcher)

        # Check that strategies were loaded correctly
        print(f"Loaded {len(signal_generator.strategy_names)} strategies:")
        for i, name in enumerate(signal_generator.strategy_names):
            print(f"  {i+1}. {name}")

        # Check that the strategy name is "信号生成V1" and not "SignalGenerator"
        if signal_generator.strategy_names:
            first_strategy_name = signal_generator.strategy_names[0]
            if first_strategy_name == "信号生成V1":
                print("✓ PASS: Strategy name is correctly set to '信号生成V1'")
                return True
            else:
                print(f"✗ FAIL: Expected '信号生成V1', got '{first_strategy_name}'")
                return False
        else:
            print("✗ FAIL: No strategies loaded")
            return False

    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


if __name__ == "__main__":
    success = test_signal_generator_fix()
    if success:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed!")
        sys.exit(1)

