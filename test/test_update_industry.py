#!/usr/bin/env python
# coding=utf-8

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from down2mongo import conn_mongo, update_industry

def test_update_industry():
    """Test the update_industry function"""
    print("Connecting to MongoDB...")
    db = conn_mongo()

    print("Executing update_industry function...")
    update_industry(db)

    print("\nChecking updated records...")

    # Check some sample records to verify data was updated
    code_collection = db["code"]

    # Get a few records that should have industry data
    sample_records = code_collection.find({
        "industry": {"$exists": True}
    }).limit(5)

    print("\nSample records with industry data:")
    for record in sample_records:
        print(f"Code: {record.get('code')}, Name: {record.get('name')}")
        print(f"  Industry: {record.get('industry')}")
        print(f"  PE: {record.get('PE')}")
        print(f"  PB: {record.get('PB')}")
        print("-" * 50)

    # Count total records with industry data
    count_with_industry = code_collection.count_documents({"industry": {"$exists": True}})
    print(f"\nTotal records with industry data: {count_with_industry}")

    # Count total records with PE data
    count_with_pe = code_collection.count_documents({"PE": {"$exists": True}})
    print(f"Total records with PE data: {count_with_pe}")

    # Count total records with PB data
    count_with_pb = code_collection.count_documents({"PB": {"$exists": True}})
    print(f"Total records with PB data: {count_with_pb}")

if __name__ == "__main__":
    test_update_industry()

