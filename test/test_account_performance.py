#!/usr/bin/env python3
"""
Test script to check if the account performance API endpoint is working correctly
and generating asset curves that reflect stock price changes.
"""

import requests
import json
from datetime import datetime

def test_account_performance_api():
    """Test the account performance API endpoint"""
    base_url = "http://localhost:5000"

    try:
        # First get accounts
        print("Testing GET /api/accounts...")
        response = requests.get(f"{base_url}/api/accounts")

        if response.status_code == 200:
            accounts = response.json()
            print(f"Found {len(accounts)} accounts")

            if accounts:
                # Test the account performance endpoint with the first account
                account_id = accounts[0]['_id']
                account_name = accounts[0].get('name', 'Unknown')
                print(f"\nTesting GET /api/account-performance/{account_id} for account '{account_name}'...")

                performance_response = requests.get(f"{base_url}/api/account-performance/{account_id}")
                print(f"Status Code: {performance_response.status_code}")

                if performance_response.status_code == 200:
                    try:
                        performance_data = performance_response.json()
                        print(f"Performance data keys: {list(performance_data.keys())}")

                        if 'performance_data' in performance_data:
                            perf_data = performance_data['performance_data']
                            print(f"Number of performance records: {len(perf_data)}")

                            if perf_data:
                                # Show first few records
                                print("\nFirst 5 performance records:")
                                for i, record in enumerate(perf_data[:5]):
                                    print(f"  {i+1}. Date: {record.get('date')}, "
                                          f"Portfolio Value: {record.get('portfolio_value'):.2f}, "
                                          f"Cash: {record.get('cash'):.2f}, "
                                          f"Stock Value: {record.get('stock_value'):.2f}")

                                # Show last few records
                                print("\nLast 5 performance records:")
                                for i, record in enumerate(perf_data[-5:]):
                                    idx = len(perf_data) - 5 + i
                                    print(f"  {idx+1}. Date: {record.get('date')}, "
                                          f"Portfolio Value: {record.get('portfolio_value'):.2f}, "
                                          f"Cash: {record.get('cash'):.2f}, "
                                          f"Stock Value: {record.get('stock_value'):.2f}")

                                # Check if portfolio value changes over time (indicating it's not a flat line)
                                first_value = perf_data[0].get('portfolio_value', 0)
                                last_value = perf_data[-1].get('portfolio_value', 0)

                                if first_value != last_value:
                                    print(f"\n✓ Portfolio value changes from {first_value:.2f} to {last_value:.2f}")
                                    print("✓ Asset curve should reflect stock price changes correctly")
                                else:
                                    print(f"\n⚠ Portfolio value remains constant at {first_value:.2f}")
                                    print("⚠ Asset curve may be a flat line - check implementation")

                                # Check if we have holdings data
                                if 'holdings' in perf_data[0]:
                                    holdings = perf_data[0]['holdings']
                                    if holdings:
                                        print(f"✓ Holdings data available: {len(holdings)} stocks")
                                        for code, info in list(holdings.items())[:3]:  # Show first 3 holdings
                                            print(f"  - {code}: {info.get('quantity', 0)} shares at cost {info.get('cost', 0):.2f}")
                                    else:
                                        print("⚠ No holdings data found")
                            else:
                                print("No performance data records found")
                        else:
                            print("No 'performance_data' key in response")
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        print(f"Response text: {performance_response.text}")
                else:
                    print(f"Error getting account performance: {performance_response.status_code}")
                    print(f"Response text: {performance_response.text}")
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
    test_account_performance_api()

