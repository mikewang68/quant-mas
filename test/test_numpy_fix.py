#!/usr/bin/env python3
"""
Test script to verify the numpy type conversion fix in TechnicalStockSelector
"""

import sys
import os
import numpy as np
from datetime import datetime
from typing import List, Dict

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from data.database_operations import DatabaseOperations


def create_test_data() -> List[Dict]:
    """Create test data with numpy types to simulate the issue"""
    test_stocks = [
        {
            'code': '300033',
            'selection_reason': '符合条件: 上涨角度(68.02°) > 阈值(30°), 加速中(当前68.02° > 之前59.32°)',
            'score': np.float64(0.85),  # This was causing the issue
            'position': np.float64(0.12),
            'technical_analysis': {
                'price': np.float64(15.6),
                'current_angle': np.float64(68.02),
                'previous_angle': np.float64(59.32)
            }
        },
        {
            'code': '000001',
            'selection_reason': '符合条件: 上涨角度(45.5°) > 阈值(30°)',
            'score': np.float64(0.72),
            'position': np.float64(0.08),
            'technical_analysis': {
                'price': np.float64(12.3),
                'current_angle': np.float64(45.5),
                'previous_angle': np.float64(38.2)
            }
        }
    ]
    return test_stocks


def test_numpy_conversion():
    """Test the numpy type conversion fix"""
    print("Testing numpy type conversion fix...")

    # Create test data with numpy types
    test_stocks = create_test_data()
    print(f"Original data types:")
    for stock in test_stocks:
        print(f"  Score type: {type(stock['score'])}")
        print(f"  Position type: {type(stock['position'])}")
        print(f"  Price type: {type(stock['technical_analysis']['price'])}")

    # Initialize database manager
    db_manager = MongoDBManager()

    try:
        # Test the conversion method
        db_ops = DatabaseOperations(db_manager)
        converted_stocks = db_ops._convert_numpy_types(test_stocks)

        print(f"\nConverted data types:")
        for stock in converted_stocks:
            print(f"  Score type: {type(stock['score'])}")
            print(f"  Position type: {type(stock['position'])}")
            print(f"  Price type: {type(stock['technical_analysis']['price'])}")

        # Verify all numpy types are converted
        all_converted = True
        for stock in converted_stocks:
            if isinstance(stock['score'], np.ndarray) or isinstance(stock['score'], np.floating):
                print(f"ERROR: Score still has numpy type: {type(stock['score'])}")
                all_converted = False
            if isinstance(stock['position'], np.ndarray) or isinstance(stock['position'], np.floating):
                print(f"ERROR: Position still has numpy type: {type(stock['position'])}")
                all_converted = False
            if isinstance(stock['technical_analysis']['price'], np.ndarray) or isinstance(stock['technical_analysis']['price'], np.floating):
                print(f"ERROR: Price still has numpy type: {type(stock['technical_analysis']['price'])}")
                all_converted = False

        if all_converted:
            print("\n✓ All numpy types successfully converted to native Python types!")
            return True
        else:
            print("\n✗ Some numpy types were not converted properly!")
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
    print("Running numpy type conversion test...")

    success = test_numpy_conversion()

    if success:
        print("\n✓ Test passed! The fix should resolve the MongoDB update issue.")
        return 0
    else:
        print("\n✗ Test failed! There may still be issues with numpy type handling.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

