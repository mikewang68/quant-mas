#!/usr/bin/env python3
"""
Script to insert test data into MongoDB accounts collection.
"""

import yaml
import os
from pymongo import MongoClient

def insert_test_data():
    # Load database configuration
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'database.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        db_config = yaml.safe_load(f)
    
    # Get MongoDB configuration
    mongo_config = db_config['mongodb']
    auth_db = mongo_config.get('auth_database', 'admin')
    
    # Create MongoDB connection string
    mongo_uri = f"mongodb://{mongo_config['username']}:{mongo_config['password']}@{mongo_config['host']}:{mongo_config['port']}/{mongo_config['database']}?authSource={auth_db}"
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB")
        
        # Get database and collection
        db = client[mongo_config['database']]
        collection = db['accounts']
        
        # Test data
        test_accounts = [
            {
                "name": "测试账户1",
                "type": "a_stock",
                "cash": 100000,
                "stocks": [
                    {"code": "000001", "name": "平安银行", "quantity": 1000, "cost": 15.20},
                    {"code": "000002", "name": "万科A", "quantity": 500, "cost": 25.50}
                ]
            },
            {
                "name": "测试账户2",
                "type": "crypto",
                "cash": 50000,
                "stocks": [
                    {"code": "BTCUSDT", "name": "比特币", "quantity": 0.5, "cost": 40000},
                    {"code": "ETHUSDT", "name": "以太坊", "quantity": 10, "cost": 3000}
                ]
            }
        ]
        
        # Insert test data
        result = collection.insert_many(test_accounts)
        print(f"Successfully inserted {len(result.inserted_ids)} accounts")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    insert_test_data()

