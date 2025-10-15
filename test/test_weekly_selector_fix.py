"""
Test script to verify weekly selector date fix
"""
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.weekly_selector import WeeklyStockSelector
from data.mongodb_manager import MongoDBManager

def test_date_logic():
    """Test the date logic in weekly selector"""

    print("Testing date logic:")
    print(f"Current date: {datetime.now()}")
    print(f"strftime('%Y-%W'): {datetime.now().strftime('%Y-%W')}")
    print(f"ISO calendar: {datetime.now().isocalendar()}")
    print(f"ISO year-week: {datetime.now().isocalendar()[0]}-{datetime.now().isocalendar()[1]:02d}")

    # Test the weekly selector
    db_manager = MongoDBManager()
    selector = WeeklyStockSelector(db_manager)

    # Test the selection
    print("\nTesting weekly selector...")
    try:
        result = selector.select_stocks()
        print(f"Selection completed, found {len(result)} strategies")

        # Test saving
        save_result = selector.save_selected_stocks(result)
        print(f"Save result: {save_result}")

    except Exception as e:
        print(f"Error during selection: {e}")

if __name__ == "__main__":
    test_date_logic()

