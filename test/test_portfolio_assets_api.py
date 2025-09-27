#!/usr/bin/env python3
"""
Test script to check if the portfolio assets API endpoint is working correctly.
"""

import requests
import json

def test_portfolio_assets_api():
    """Test the portfolio assets API endpoint"""
    base_url = "http://localhost:5000"

    try:
        # First get accounts
        print("Testing GET /api/accounts...")
        response = requests.get(f"{base_url}/api/accounts")

        if response.status_code == 200:
            accounts = response.json()
            print(f"Found {len(accounts)} accounts")

            if accounts:
                # Test the portfolio assets endpoint with the first account
                account_id = accounts[0]['_id']
                account_name = accounts[0].get('name', 'Unknown')
                print(f"\nTesting GET /api/portfolio-assets/{account_id} for account '{account_name}'...")

                assets_response = requests.get(f"{base_url}/api/portfolio-assets/{account_id}")
                print(f"Status Code: {assets_response.status_code}")

                if assets_response.status_code == 200:
                    try:
                        assets_data = assets_response.json()
                        print(f"Asset data keys: {list(assets_data.keys())}")

                        if 'asset_data' in assets_data:
                            asset_data = assets_data['asset_data']
                            print(f"Number of asset records: {len(asset_data)}")

                            if asset_data:
                                # Show first few records
                                print("\nFirst 3 asset records:")
                                for i, record in enumerate(asset_data[:3]):
                                    print(f"  {i+1}. Date: {record.get('date')}, "
                                          f"Stock: {record.get('stock_code')}, "
                                          f"Close: {record.get('close_price')}, "
                                          f"Quantity: {record.get('quantity')}, "
                                          f"Holding Value: {record.get('holding_value')}, "
                                          f"Cash: {record.get('cash')}, "
                                          f"Total Assets: {record.get('total_assets')}")
                            else:
                                print("No asset data records found")
                        else:
                            print("No 'asset_data' key in response")
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        print(f"Response text: {assets_response.text}")
                else:
                    print(f"Error getting portfolio assets: {assets_response.status_code}")
                    print(f"Response text: {assets_response.text}")
            else:
                print("No accounts found")
        else:
            print(f"Error getting accounts: {response.status_code}")
            print(f"Response text: {response.text}")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the web app is running.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_portfolio_assets_api()

