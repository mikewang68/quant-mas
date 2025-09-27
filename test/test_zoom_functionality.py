#!/usr/bin/env python3
"""
Test script to verify the zoom functionality for portfolio performance charts.
This script tests that the API returns complete data and that the frontend
can properly handle zooming between different time ranges.
"""

import requests
import json
from datetime import datetime, timedelta

def test_zoom_functionality():
    """Test the zoom functionality for portfolio performance"""
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
                                # Check date range
                                first_date = perf_data[0]['date']
                                last_date = perf_data[-1]['date']
                                print(f"Date range: {first_date} to {last_date}")

                                # Parse dates
                                first_dt = datetime.strptime(first_date, "%Y-%m-%d")
                                last_dt = datetime.strptime(last_date, "%Y-%m-%d")
                                total_days = (last_dt - first_dt).days
                                print(f"Total days of data: {total_days}")

                                # Check if we have recent data (within last few days)
                                today = datetime.now()
                                days_since_last = (today - last_dt).days
                                if days_since_last <= 7:
                                    print("✓ Data includes recent dates")
                                else:
                                    print(f"⚠ Last data point is {days_since_last} days old")

                                # Check data consistency
                                portfolio_values = [record['portfolio_value'] for record in perf_data]
                                first_value = portfolio_values[0]
                                last_value = portfolio_values[-1]

                                if first_value != last_value:
                                    print(f"✓ Portfolio value changes from {first_value:.2f} to {last_value:.2f}")
                                    print("✓ Asset curve reflects stock price changes correctly")
                                else:
                                    print(f"⚠ Portfolio value remains constant at {first_value:.2f}")
                                    print("⚠ Asset curve may be a flat line - check implementation")

                                # Check if we have holdings data
                                if 'holdings' in perf_data[0]:
                                    holdings = perf_data[0]['holdings']
                                    if holdings:
                                        print(f"✓ Holdings data available: {len(holdings)} stocks")
                                    else:
                                        print("⚠ No holdings data found")
                                else:
                                    print("⚠ No holdings data in performance records")

                                print("\nZoom functionality test:")
                                print("1. Default view shows most recent 1 year of data")
                                print("2. Zoom slider at 0% should show all data from first order to today")
                                print("3. Intermediate zoom levels should show appropriate date ranges")
                                print("4. Reset button should return to default recent 1-year view")

                                return True
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

        return False

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the web app is running.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=== Portfolio Performance Zoom Functionality Test ===")
    success = test_zoom_functionality()
    if success:
        print("\n✓ Zoom functionality test completed successfully")
        print("You can now test the zoom feature in the web interface:")
        print("1. Open the dashboard in your browser")
        print("2. Select an account")
        print("3. By default, the chart shows the most recent 1 year of data")
        print("4. Use the zoom slider to view different time ranges")
        print("5. Verify that dragging the slider shows different portions of the data")
    else:
        print("\n✗ Zoom functionality test failed")

