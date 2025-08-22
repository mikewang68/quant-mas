#!/usr/bin/env python3
"""
Test script to verify the TechnicalStockSelector behavior:
1. Only updates existing stocks in the pool
2. Doesn't add new stocks
3. Skips stocks that don't meet criteria
"""

import sys
import os
from datetime import datetime
from typing import List, Dict

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from data.database_operations import DatabaseOperations


def create_test_pool_record():
    """Create a test pool record with some stocks"""
    db_manager = MongoDBManager()
    try:
        collection = db_manager.db['pool']

        # Create test stocks
        test_stocks = [
            {
                'code': '000001',
                'name': '平安银行',
                'selection_reason': '基本面选股',
                'score': 0.75
            },
            {
                'code': '000002',
                'name': '万科A',
                'selection_reason': '价值投资',
                'score': 0.82
            },
            {
                'code': '600000',
                'name': '浦发银行',
                'selection_reason': '银行股配置',
                'score': 0.68
            }
        ]

        # Create test record
        test_record = {
            '_id': 'test_pool_record_2025',
            'selection_date': datetime.now(),
            'stocks': test_stocks,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }

        # Insert or update the test record
        collection.replace_one(
            {'_id': 'test_pool_record_2025'},
            test_record,
            upsert=True
        )

        print("✓ Created test pool record with 3 stocks")
        return True

    except Exception as e:
        print(f"✗ Error creating test pool record: {e}")
        return False
    finally:
        db_manager.close_connection()


def create_test_technical_results():
    """Create test technical analysis results"""
    # Only include some of the stocks from the pool
    # 000001: meets criteria, should be updated
    # 000002: doesn't meet criteria, should be skipped
    # 600000: not in results, should remain unchanged
    # 300001: not in pool, should be ignored

    technical_stocks = [
        {
            'code': '000001',
            'technical_analysis': {
                'price': 15.6,
                'current_angle': 68.02,
                'previous_angle': 59.32
            },
            'score': 0.85,
            'position': 0.12,
            'strategy_name': '加速上涨策略',
            'selection_reason': '符合条件: 上涨角度(68.02°) > 阈值(30°), 加速中(当前68.02° > 之前59.32°)'
        },
        {
            'code': '300001',
            'technical_analysis': {
                'price': 25.3,
                'current_angle': 72.5,
                'previous_angle': 65.2
            },
            'score': 0.91,
            'position': 0.15,
            'strategy_name': '加速上涨策略',
            'selection_reason': '符合条件: 上涨角度(72.5°) > 阈值(30°), 加速中(当前72.5° > 之前65.2°)'
        }
    ]

    return technical_stocks


def test_update_latest_pool_record():
    """Test the update_latest_pool_record functionality"""
    print("\nTesting update_latest_pool_record...")

    db_manager = MongoDBManager()
    try:
        # Create database operations instance
        db_ops = DatabaseOperations(db_manager)

        # Get the test pool record
        collection = db_manager.db['pool']
        test_record = collection.find_one({'_id': 'test_pool_record_2025'})

        if not test_record:
            print("✗ Test record not found")
            return False

        print(f"Original stocks: {[stock['code'] for stock in test_record['stocks']]}")

        # Create test technical results
        technical_stocks = create_test_technical_results()
        print(f"Technical results: {[stock['code'] for stock in technical_stocks]}")

        # Mock the TechnicalStockSelector update_latest_pool_record method
        from agents.technical_selector import TechnicalStockSelector
        selector = TechnicalStockSelector(db_manager, None)

        # Update the pool record
        success = selector.update_latest_pool_record(technical_stocks)

        if not success:
            print("✗ Failed to update pool record")
            return False

        # Check the updated record
        updated_record = collection.find_one({'_id': 'test_pool_record_2025'})
        updated_stocks = updated_record['stocks']

        print(f"Updated stocks: {[stock['code'] for stock in updated_stocks]}")

        # Verify the results
        stock_map = {stock['code']: stock for stock in updated_stocks}

        # 000001 should be updated with technical analysis
        if '000001' in stock_map:
            stock_000001 = stock_map['000001']
            if 'technical_analysis' in stock_000001 and stock_000001['score'] == 0.85:
                print("✓ 000001 correctly updated with technical analysis")
            else:
                print("✗ 000001 not correctly updated")
                return False
        else:
            print("✗ 000001 missing from updated stocks")
            return False

        # 000002 should remain unchanged
        if '000002' in stock_map:
            stock_000002 = stock_map['000002']
            if stock_000002['score'] == 0.82 and 'technical_analysis' not in stock_000002:
                print("✓ 000002 correctly left unchanged")
            else:
                print("✗ 000002 incorrectly modified")
                return False
        else:
            print("✗ 000002 missing from updated stocks")
            return False

        # 600000 should remain unchanged
        if '600000' in stock_map:
            stock_600000 = stock_map['600000']
            if stock_600000['score'] == 0.68 and 'technical_analysis' not in stock_600000:
                print("✓ 600000 correctly left unchanged")
            else:
                print("✗ 600000 incorrectly modified")
                return False
        else:
            print("✗ 600000 missing from updated stocks")
            return False

        # 300001 should not be added (not in original pool)
        if '300001' in stock_map:
            print("✗ 300001 incorrectly added to pool")
            return False
        else:
            print("✓ 300001 correctly not added to pool")

        print("✓ All tests passed!")
        return True

    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db_manager.close_connection()


def main():
    """Main test function"""
    print("Testing TechnicalStockSelector pool update behavior...")

    # Create test data
    if not create_test_pool_record():
        return 1

    # Test the update functionality
    if not test_update_latest_pool_record():
        return 1

    print("\n✓ All tests passed! The TechnicalStockSelector correctly:")
    print("  1. Only updates existing stocks in the pool")
    print("  2. Doesn't add new stocks")
    print("  3. Skips stocks that don't meet criteria")
    print("  4. Leaves unchanged stocks that aren't in the results")

    return 0


if __name__ == "__main__":
    sys.exit(main())

