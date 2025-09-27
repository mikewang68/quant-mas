#!/usr/bin/env python3
"""
Test script to check if the accounts API endpoint is working correctly.
"""

import requests
import json

def test_accounts_api():
    """Test the accounts API endpoint"""
    try:
        # Test the GET endpoint
        print("Testing GET /api/accounts...")
        response = requests.get('http://localhost:5000/api/accounts')

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")

        if response.status_code == 200:
            try:
                accounts = response.json()
                print(f"Accounts Data: {json.dumps(accounts, indent=2, ensure_ascii=False)}")
                print(f"Number of accounts: {len(accounts)}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print(f"Response text: {response.text}")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response text: {response.text}")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the web app is running.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_accounts_api()

