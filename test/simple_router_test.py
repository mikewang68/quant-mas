#!/usr/bin/env python3

import requests
import re
import json

def test_router_auth():
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

    print("=== Step 1: Get login page ===")
    try:
        login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
        print(f"Login page status code: {login_page_response.status_code}")
        print(f"Login page content length: {len(login_page_response.text)}")

        # Look for hidden fields or tokens
        hidden_fields = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']*)["\'][^>]*/?>', login_page_response.text)
        print(f"Hidden fields found: {hidden_fields}")

        # Look for CSRF token
        csrf_token_match = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', login_page_response.text)
        csrf_token = csrf_token_match.group(1) if csrf_token_match else None
        print(f"CSRF token: {csrf_token}")

    except Exception as e:
        print(f"Error getting login page: {e}")
        return False

    print("\n=== Step 2: Try to login ===")
    try:
        # Try different login approaches
        login_data = {
            'method': 'login',
            'username': USERNAME,
            'password': PASSWORD
        }

        if csrf_token:
            login_data['csrf_token'] = csrf_token

        print(f"Login data: {login_data}")

        # Try POST to root URL
        login_response = session.post(
            f"{base_url}/",
            data=login_data,
            timeout=15,
            allow_redirects=False
        )

        print(f"Login response status code: {login_response.status_code}")
        print(f"Login response headers: {dict(login_response.headers)}")
        print(f"Login response content length: {len(login_response.text)}")

        # Check for stok in response
        stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', login_response.text)
        if stok_match:
            stok = stok_match.group(1)
            print(f"Found stok: {stok}")
            return True
        else:
            print("No stok found in response")

        # Check if success in response
        if '"success":true' in login_response.text.lower():
            print("Login successful (success:true found)")
            return True

        # Print first 1000 chars of response for debugging
        response_preview = login_response.text[:1000] if len(login_response.text) > 1000 else login_response.text
        print(f"Response preview: {response_preview}")

    except Exception as e:
        print(f"Error during login: {e}")
        return False

    return False

if __name__ == "__main__":
    success = test_router_auth()
    print(f"\nTest result: {'SUCCESS' if success else 'FAILED'}")

