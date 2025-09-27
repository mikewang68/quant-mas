"""
Test script to check if API endpoints are working
"""

import requests
import json

def test_api_endpoints():
    """Test API endpoints"""
    base_url = "http://localhost:5000"  # Assuming the app runs on localhost:5000

    print("Testing API endpoints...")

    # Test accounts endpoint
    try:
        print("\n1. Testing /api/accounts endpoint...")
        response = requests.get(f"{base_url}/api/accounts")
        print(f"   Status code: {response.status_code}")
        if response.status_code == 200:
            accounts = response.json()
            print(f"   Accounts found: {len(accounts)}")
            if accounts:
                print(f"   First account: {accounts[0]}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

    # Test a specific account performance endpoint (if we have accounts)
    try:
        print("\n2. Testing /api/account-performance endpoint...")
        # First get accounts
        response = requests.get(f"{base_url}/api/accounts")
        if response.status_code == 200:
            accounts = response.json()
            if accounts:
                account_id = accounts[0]['_id']
                performance_response = requests.get(f"{base_url}/api/account-performance/{account_id}")
                print(f"   Status code: {performance_response.status_code}")
                if performance_response.status_code == 200:
                    performance_data = performance_response.json()
                    print(f"   Performance data keys: {list(performance_data.keys())}")
                else:
                    print(f"   Error: {performance_response.text}")
            else:
                print("   No accounts found to test performance endpoint")
        else:
            print(f"   Failed to get accounts: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_api_endpoints()

