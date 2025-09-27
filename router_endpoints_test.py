#!/usr/bin/env python3

import requests
import re
import json

def test_router_endpoints():
    # Router configuration
    ROUTER_IP = "192.168.1.1"
    USERNAME = "wangdg68"
    PASSWORD = "wap951020ZJL"
    base_url = f"http://{ROUTER_IP}"

    # Create a session
    session = requests.Session()

    # Set headers to mimic a browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': f'{base_url}/webpages/login.html',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    })

    print("=== Testing different endpoints ===")

    # Test different endpoints that might be used for login
    endpoints_to_try = [
        "/",
        "/login",
        "/cgi-bin/luci",
        "/cgi-bin/luci/",
        "/admin/login",
        "/api/login"
    ]

    # Test different data formats
    data_formats = [
        # Format 1: Simple form data
        {
            'method': 'login',
            'username': USERNAME,
            'password': PASSWORD
        },
        # Format 2: Different parameter names
        {
            'action': 'login',
            'username': USERNAME,
            'password': PASSWORD
        },
        # Format 3: JSON-like in form data
        {
            'operation': 'login',
            'username': USERNAME,
            'password': PASSWORD
        }
    ]

    for endpoint in endpoints_to_try:
        for i, data in enumerate(data_formats, 1):
            print(f"\n--- Testing endpoint: {endpoint}, data format {i} ---")
            print(f"Data: {data}")

            try:
                response = session.post(
                    f"{base_url}{endpoint}",
                    data=data,
                    timeout=10,
                    allow_redirects=False
                )

                print(f"Status code: {response.status_code}")
                if 'Location' in response.headers:
                    print(f"Redirect to: {response.headers['Location']}")

                # Check response content
                content_preview = response.text[:500] if len(response.text) > 500 else response.text
                print(f"Content preview: {content_preview}")

                # Check for stok
                stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', response.text)
                if stok_match:
                    stok = stok_match.group(1)
                    print(f"SUCCESS! Found stok: {stok}")
                    return True

            except Exception as e:
                print(f"Error: {e}")
                continue

    print("\n=== Testing JSON requests ===")

    # Test JSON requests
    json_endpoints = ["/", "/login", "/cgi-bin/luci"]
    json_data_formats = [
        {
            "method": "login",
            "params": {
                "username": USERNAME,
                "password": PASSWORD
            }
        },
        {
            "operation": "login",
            "data": {
                "username": USERNAME,
                "password": PASSWORD
            }
        }
    ]

    session.headers.update({
        'Content-Type': 'application/json'
    })

    for endpoint in json_endpoints:
        for i, json_data in enumerate(json_data_formats, 1):
            print(f"\n--- Testing JSON endpoint: {endpoint}, format {i} ---")
            print(f"Data: {json_data}")

            try:
                response = session.post(
                    f"{base_url}{endpoint}",
                    json=json_data,
                    timeout=10,
                    allow_redirects=False
                )

                print(f"Status code: {response.status_code}")
                if 'Location' in response.headers:
                    print(f"Redirect to: {response.headers['Location']}")

                # Check response content
                content_preview = response.text[:500] if len(response.text) > 500 else response.text
                print(f"Content preview: {content_preview}")

                # Check for stok
                stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', response.text)
                if stok_match:
                    stok = stok_match.group(1)
                    print(f"SUCCESS! Found stok: {stok}")
                    return True

            except Exception as e:
                print(f"Error: {e}")
                continue

    return False

if __name__ == "__main__":
    success = test_router_endpoints()
    print(f"\nTest result: {'SUCCESS' if success else 'FAILED'}")

