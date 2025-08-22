#!/usr/bin/env python3
"""
Test script to verify the complete TechnicalStockSelector flow with numpy type conversion
"""

import sys
import os
import numpy as np
from datetime import datetime

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from data.database_operations import DatabaseOperations


def test_database_operations_numpy_conversion():
    """Test the database operations numpy type conversion"""
    print("Testing DatabaseOperations numpy type conversion...")

    # Initialize database manager
    db_manager = MongoDBManager()

    try:
        # Create test data with numpy types that would cause issues
        test_stocks = [
            {
                'code': 'TEST001',
                'selection_reason': 'Test stock with numpy types',
                'score': np.float64(0.85),
                'position': np.float64(0.12),
                'technical_analysis': {
                    'price': np.float64(15.6),
                    'current_angle': np.float64(68.02),
                    'previous_angle': np.float64(59.32),
                    'acceleration': np.float64(8.7)
                }
            }
        ]

        print("Original data types:")
        for stock in test_stocks:
            print(f"  Score: {type(stock['score'])}")
            print(f"  Position: {type(stock['position'])}")
            print(f"  Price: {type(stock['technical_analysis']['price'])}")

        # Test the conversion
        db_ops = DatabaseOperations(db_manager)
        converted_stocks = db_ops._convert_numpy_types(test_stocks)

        print("\nConverted data types:")
        for stock in converted_stocks:
            print(f"  Score: {type(stock['score'])}")
            print(f"  Position: {type(stock['position'])}")
            print(f"  Price: {type(stock['technical_analysis']['price'])}")

        # Verify all conversions
        all_converted = True
        for stock in converted_stocks:
            if isinstance(stock['score'], (np.ndarray, np.floating, np.integer)):
                print(f"ERROR: Score still has numpy type: {type(stock['score'])}")
                all_converted = False
            if isinstance(stock['position'], (np.ndarray, np.floating, np.integer)):
                print(f"ERROR: Position still has numpy type: {type(stock['position'])}")
                all_converted = False
            for key, value in stock['technical_analysis'].items():
                if isinstance(value, (np.ndarray, np.floating, np.integer)):
                    print(f"ERROR: {key} still has numpy type: {type(value)}")
                    all_converted = False

        if all_converted:
            print("\n✓ All numpy types successfully converted!")
            return True
        else:
            print("\n✗ Some numpy types were not converted!")
            return False

    except Exception as e:
        print(f"Error during conversion test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db_manager.close_connection()


def main():
    """Main test function"""
    print("Running complete TechnicalStockSelector numpy type conversion test...")

    success = test_database_operations_numpy_conversion()

    if success:
        print("\n✓ Database operations numpy conversion test passed!")
        print("The fixes should prevent MongoDB errors in the TechnicalStockSelector.")
        return 0
    else:
        print("\n✗ Database operations numpy conversion test failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

