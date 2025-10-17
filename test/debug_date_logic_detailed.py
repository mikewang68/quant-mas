"""
Detailed debug script to check pool date issue
"""
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def debug_date_logic():
    """Debug the date logic in detail"""
    db_manager = MongoDBManager()

    # Get pool collection
    collection = db_manager.db["pool"]

    # Find all pool records
    records = list(collection.find().sort("_id", -1).limit(10))

    print(f"Found {len(records)} pool records:")

    for i, record in enumerate(records):
        print(f"\nRecord {i+1}:")
        print(f"  _id: {record.get('_id')}")
        print(f"  _id type: {type(record.get('_id'))}")

        # Check if _id is ObjectId
        if hasattr(record.get('_id'), 'generation_time'):
            generation_time = record.get('_id').generation_time
            print(f"  Generation time: {generation_time}")
            year_week = generation_time.strftime("%Y-%W")
            iso_year_week = f"{generation_time.isocalendar()[0]}-{generation_time.isocalendar()[1]:02d}"
            print(f"  strftime Year-Week: {year_week}")
            print(f"  ISO Year-Week: {iso_year_week}")
        else:
            print(f"  _id is not ObjectId: {record.get('_id')}")

        print(f"  Stocks count: {len(record.get('stocks', []))}")
        print(f"  Strategy keys: {record.get('strategy_key', [])}")
        print(f"  Created at: {record.get('created_at')}")
        print(f"  Updated at: {record.get('updated_at')}")

    # Check current year-week
    current_strftime = datetime.now().strftime("%Y-%W")
    current_iso = f"{datetime.now().isocalendar()[0]}-{datetime.now().isocalendar()[1]:02d}"
    print(f"\nCurrent strftime year-week: {current_strftime}")
    print(f"Current ISO year-week: {current_iso}")

    # Test the date logic from weekly_selector
    if records:
        latest_record = records[0]

        # Handle both ObjectId and string _id formats
        if hasattr(latest_record["_id"], 'generation_time'):
            # _id is ObjectId
            generation_time = latest_record["_id"].generation_time
            latest_record_strftime = generation_time.strftime("%Y-%W")
            latest_record_iso = f"{generation_time.isocalendar()[0]}-{generation_time.isocalendar()[1]:02d}"
        else:
            # _id is string, try to extract year-week from the string
            id_str = latest_record["_id"]
            # Check if the string is in year-week format like "2025-41"
            if "-" in id_str and len(id_str) == 7:
                try:
                    # Extract year and week from string like "2025-41"
                    year, week = id_str.split("-")
                    latest_record_strftime = f"{year}-{week}"
                    latest_record_iso = f"{year}-{week}"
                except:
                    # Fallback to current week
                    latest_record_strftime = datetime.now().strftime("%Y-%W")
                    latest_record_iso = f"{datetime.now().isocalendar()[0]}-{datetime.now().isocalendar()[1]:02d}"
            else:
                # Not in expected format, use current week
                latest_record_strftime = datetime.now().strftime("%Y-%W")
                latest_record_iso = f"{datetime.now().isocalendar()[0]}-{datetime.now().isocalendar()[1]:02d}"

        print(f"\nLatest record strftime year-week: {latest_record_strftime}")
        print(f"Latest record ISO year-week: {latest_record_iso}")
        print(f"Current strftime year-week: {current_strftime}")
        print(f"Current ISO year-week: {current_iso}")
        print(f"Same week (strftime)? {latest_record_strftime == current_strftime}")
        print(f"Same week (ISO)? {latest_record_iso == current_iso}")

if __name__ == "__main__":
    debug_date_logic()

