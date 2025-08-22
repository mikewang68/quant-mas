#!/usr/bin/env python3
"""
Test script to verify strategy import logic
"""

import sys
import os
import importlib

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_import_logic():
    """Test the import logic used in weekly_selector.py"""

    # Simulate the values from database
    strategy_file = "three_ma_bullish_arrangement_strategy"
    strategy_class_name = "ThreeMABullishArrangementStrategy"

    print(f"Testing import with:")
    print(f"  strategy_file: {strategy_file}")
    print(f"  strategy_class_name: {strategy_class_name}")

    try:
        # Replicate the logic from weekly_selector.py
        if '.' not in strategy_file and not strategy_file.startswith('strategies.'):
            # If it's just a filename without package prefix, add the strategies prefix
            module_name = f"strategies.{strategy_file}"
        else:
            module_name = strategy_file

        print(f"  module_name: {module_name}")

        # Try to import the module
        strategy_module = importlib.import_module(module_name)
        print(f"  SUCCESS: Module imported successfully")

        # Try to get the class
        strategy_class = getattr(strategy_module, strategy_class_name)
        print(f"  SUCCESS: Class found successfully")

        # Try to instantiate the class
        strategy_instance = strategy_class()
        print(f"  SUCCESS: Class instantiated successfully")

        return True

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_import_logic()
    if success:
        print("\nAll tests passed!")
    else:
        print("\nTest failed!")

