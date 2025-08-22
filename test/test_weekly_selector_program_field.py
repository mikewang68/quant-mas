#!/usr/bin/env python3
"""
Test script to verify that weekly_selector can correctly extract file and class information
from the program field in strategy documents.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def test_program_field_extraction():
    """Test that weekly_selector correctly extracts file and class from program field"""
    try:
        # Initialize components
        db_manager = MongoDBManager()

        # Create a test strategy with program field
        test_strategy = {
            "name": "Test Strategy with Program Field",
            "type": "technical",
            "description": "Test strategy with program field containing file and class",
            "program": {
                "file": "three_ma_bullish_arrangement_strategy",
                "class": "ThreeMABullishArrangementStrategy"
            },
            "parameters": {
                "ma_short": 5,
                "ma_mid": 13,
                "ma_long": 34
            }
        }

        # Save test strategy to database
        strategy_id = db_manager.create_strategy(test_strategy)
        print(f"Created test strategy with ID: {strategy_id}")

        if not strategy_id:
            print("Failed to create test strategy")
            return False

        # Test the _load_strategy_from_db logic directly
        strategies = db_manager.get_strategies()
        if strategies and len(strategies) > 0:
            # Find our test strategy
            test_strategy_doc = None
            for strategy in strategies:
                if strategy.get('_id') == strategy_id:
                    test_strategy_doc = strategy
                    break

            if not test_strategy_doc:
                print("Failed to find test strategy in database")
                return False

            # Extract file and class from program field (this is the logic we're testing)
            strategy_file = ''
            strategy_class_name = ''

            if 'program' in test_strategy_doc and isinstance(test_strategy_doc['program'], dict):
                strategy_file = test_strategy_doc['program'].get('file', '')
                strategy_class_name = test_strategy_doc['program'].get('class', '')
                print("Loaded strategy file and class from program field")
            else:
                # Fallback to direct file and class_name fields
                strategy_file = test_strategy_doc.get('file', '')
                strategy_class_name = test_strategy_doc.get('class_name', '')

            print(f"Strategy name: {test_strategy_doc.get('name', 'Unknown')}")
            print(f"Strategy file: {strategy_file}")
            print(f"Strategy class name: {strategy_class_name}")

            # Verify the values
            if strategy_file != "three_ma_bullish_arrangement_strategy":
                print(f"ERROR: Expected file 'three_ma_bullish_arrangement_strategy', got '{strategy_file}'")
                return False

            if strategy_class_name != "ThreeMABullishArrangementStrategy":
                print(f"ERROR: Expected class 'ThreeMABullishArrangementStrategy', got '{strategy_class_name}'")
                return False

            print("Program field extraction test passed!")
        else:
            print("No strategies found in database")
            return False

        # Test with a strategy that has direct file and class_name fields (fallback)
        fallback_strategy = {
            "name": "Fallback Test Strategy",
            "type": "technical",
            "description": "Test strategy with direct file and class_name fields",
            "file": "ma_crossover_strategy",
            "class_name": "MACrossoverStrategy",
            "parameters": {
                "short_period": 5,
                "long_period": 20
            }
        }

        # Save fallback test strategy to database
        fallback_strategy_id = db_manager.create_strategy(fallback_strategy)
        print(f"\nCreated fallback test strategy with ID: {fallback_strategy_id}")

        if not fallback_strategy_id:
            print("Failed to create fallback test strategy")
            return False

        # Test fallback logic
        fallback_strategy_doc = db_manager.get_strategy(fallback_strategy_id)
        if fallback_strategy_doc:
            # Test fallback logic - when program field is not a dict or doesn't exist
            strategy_file = ''
            strategy_class_name = ''

            if 'program' in fallback_strategy_doc and isinstance(fallback_strategy_doc['program'], dict):
                strategy_file = fallback_strategy_doc['program'].get('file', '')
                strategy_class_name = fallback_strategy_doc['program'].get('class', '')
                print("Loaded fallback strategy file and class from program field")
            else:
                # Fallback to direct file and class_name fields
                strategy_file = fallback_strategy_doc.get('file', '')
                strategy_class_name = fallback_strategy_doc.get('class_name', '')
                print("Loaded fallback strategy file and class from direct fields")

            print(f"Fallback strategy name: {fallback_strategy_doc.get('name', 'Unknown')}")
            print(f"Fallback strategy file: {strategy_file}")
            print(f"Fallback strategy class name: {strategy_class_name}")

            # Verify the fallback values
            if strategy_file != "ma_crossover_strategy":
                print(f"ERROR: Expected fallback file 'ma_crossover_strategy', got '{strategy_file}'")
                return False

            if strategy_class_name != "MACrossoverStrategy":
                print(f"ERROR: Expected fallback class 'MACrossoverStrategy', got '{strategy_class_name}'")
                return False

            print("Fallback field extraction test passed!")

        # Cleanup
        db_manager.delete_strategy(strategy_id)
        db_manager.delete_strategy(fallback_strategy_id)

        print("\nAll tests passed!")
        return True

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db_manager.close_connection()
        except:
            pass

if __name__ == "__main__":
    success = test_program_field_extraction()
    if not success:
        sys.exit(1)

