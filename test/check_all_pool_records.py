#!/usr/bin/env python3
"""
Check all records in the pool collection with detailed information
"""

import sys
import os
from datetime import datetime
from data.mongodb_manager import MongoDBManager

def check_pool_records():
    """Check all records in the pool collection"""
    print("Checking all records in pool collection...")
    
    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        print("✓ Database connection established")
        
        # Get pool collection
        pool_collection = db_manager.db['pool']
        
        # Get all records sorted by selection date (newest first)
        records = list(pool_collection.find().sort('selection_date', -1))
        
        print(f"\nFound {len(records)} total records in pool:")
        
        # Group records by type
        strategy_records = []
        combined_records = []
        weekly_records = []
        unknown_records = []
        
        for record in records:
            if record.get('type') == 'combined':
                combined_records.append(record)
            elif record.get('strategy_name'):
                strategy_records.append(record)
            elif record.get('week'):  # Weekly selector records have week field
                weekly_records.append(record)
            else:
                unknown_records.append(record)
        
        print(f"\nBreakdown:")
        print(f"  - Strategy records: {len(strategy_records)}")
        print(f"  - Combined records: {len(combined_records)}")
        print(f"  - Weekly records: {len(weekly_records)}")
        print(f"  - Unknown records: {len(unknown_records)}")
        
        # Show detailed information for each type
        if strategy_records:
            print(f"\n--- Strategy Records ({len(strategy_records)}) ---")
            for i, record in enumerate(strategy_records[:10]):  # Show first 10
                strategy_name = record.get('strategy_name', 'Unknown')
                agent_name = record.get('agent_name', 'Unknown')
                count = record.get('count', 0)
                selection_date = record.get('selection_date', 'N/A')
                selection_timestamp = record.get('selection_timestamp')
                timestamp_str = selection_timestamp.strftime('%Y-%m-%d %H:%M:%S') if selection_timestamp else 'N/A'
                
                print(f"  {i+1}. {strategy_name} by {agent_name} ({count} stocks) at {timestamp_str}")
                if selection_date != 'N/A':
                    print(f"     Selection date: {selection_date}")
        
        if combined_records:
            print(f"\n--- Combined Records ({len(combined_records)}) ---")
            for i, record in enumerate(combined_records[:5]):  # Show first 5
                agent_name = record.get('agent_name', 'Unknown')
                count = record.get('count', 0)
                selection_date = record.get('selection_date', 'N/A')
                selection_timestamp = record.get('selection_timestamp')
                timestamp_str = selection_timestamp.strftime('%Y-%m-%d %H:%M:%S') if selection_timestamp else 'N/A'
                
                print(f"  {i+1}. Combined results by {agent_name} ({count} stocks) at {timestamp_str}")
                if selection_date != 'N/A':
                    print(f"     Selection date: {selection_date}")
        
        if weekly_records:
            print(f"\n--- Weekly Records ({len(weekly_records)}) ---")
            for i, record in enumerate(weekly_records[:5]):  # Show first 5
                year = record.get('year', 'Unknown')
                week = record.get('week', 'Unknown')
                count = record.get('count', 0)
                selection_date = record.get('selection_date', 'N/A')
                
                print(f"  {i+1}. Weekly selection {year}-W{week:02d} ({count} stocks)")
                if selection_date != 'N/A':
                    print(f"     Selection date: {selection_date}")
        
        if unknown_records:
            print(f"\n--- Unknown Records ({len(unknown_records)}) ---")
            for i, record in enumerate(unknown_records):
                count = record.get('count', 0)
                selection_date = record.get('selection_date', 'N/A')
                print(f"  {i+1}. Unknown record ({count} stocks)")
                if selection_date != 'N/A':
                    print(f"     Selection date: {selection_date}")
        
        # Check for duplicate timestamps
        print(f"\n--- Timestamp Analysis ---")
        timestamps = {}
        for record in records:
            selection_timestamp = record.get('selection_timestamp')
            if selection_timestamp:
                timestamp_str = selection_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                if timestamp_str not in timestamps:
                    timestamps[timestamp_str] = []
                timestamps[timestamp_str].append(record)
        
        duplicate_timestamps = {k: v for k, v in timestamps.items() if len(v) > 1}
        if duplicate_timestamps:
            print(f"Found {len(duplicate_timestamps)} duplicate timestamps:")
            for timestamp, records_at_time in list(duplicate_timestamps.items())[:5]:
                print(f"  {timestamp}: {len(records_at_time)} records")
                for record in records_at_time:
                    if record.get('type') == 'combined':
                        print(f"    - Combined record by {record.get('agent_name', 'Unknown')}")
                    elif record.get('strategy_name'):
                        print(f"    - Strategy record: {record.get('strategy_name', 'Unknown')}")
                    else:
                        print(f"    - Unknown record")
        else:
            print("No duplicate timestamps found")
        
        db_manager.close_connection()
        print("\n✓ Pool records check completed successfully")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = check_pool_records()
    sys.exit(0 if success else 1)

