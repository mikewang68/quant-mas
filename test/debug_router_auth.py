#!/usr/bin/env python3

import requests
import re
import json
from urllib.parse import urlparse

def debug_router_auth():
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })

    print("=== Step 1: Get login page ===")
    try:
        # First, get the login page to establish session
        login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
        print(f"Login page status code: {login_page_response.status_code}")
        print(f"Login page cookies: {session.cookies.get_dict()}")

        # Look for any hidden fields or tokens in the login form
        hidden_fields = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']*)["\'][^>]*/?>', login_page_response.text)
        print(f"Hidden fields found: {hidden_fields}")

        # Look for CSRF token
        csrf_token_match = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', login_page_response.text)
        csrf_token = csrf_token_match.group(1) if csrf_token_match else None
        print(f"CSRF token: {csrf_token}")

        # Look for any JavaScript variables that might be important
        js_vars = re.findall(r'var\s+(\w+)\s*=\s*["\']([^"\']*)["\']', login_page_response.text)
        print(f"JavaScript variables: {js_vars[:5]}...")  # Show first 5

    except Exception as e:
        print(f"Error getting login page: {e}")
        return False

    print("\n=== Step 2: Try different login approaches ===")

    # Approach 1: POST to root with form data
    print("\n--- Approach 1: POST to / with form data ---")
    try:
        login_data = {
            'method': 'login',
            'username': USERNAME,
            'password': PASSWORD
        }

        if csrf_token:
            login_data['csrf_token'] = csrf_token

        # Update headers for form submission
        session.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f'{base_url}/webpages/login.html',
            'X-Requested-With': 'XMLHttpRequest'
        })

        response = session.post(f"{base_url}/", data=login_data, timeout=10, allow_redirects=False)
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Session cookies after login: {session.cookies.get_dict()}")

        # Check response content
        if len(response.text) < 1000:
            print(f"Response content: {response.text}")
        else:
            print(f"Response preview: {response.text[:500]}...")

        # Check for stok
        stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', response.text)
        if stok_match:
            print(f"SUCCESS! Found stok: {stok_match.group(1)}")
            return True

    except Exception as e:
        print(f"Error in approach 1: {e}")

    # Approach 2: Try POST to /login
    print("\n--- Approach 2: POST to /login ---")
    try:
        login_data = {
            'method': 'login',
            'username': USERNAME,
            'password': PASSWORD
        }

        if csrf_token:
            login_data['csrf_token'] = csrf_token

        response = session.post(f"{base_url}/login", data=login_data, timeout=10, allow_redirects=False)
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        # Check response content
        if len(response.text) < 1000:
            print(f"Response content: {response.text}")
        else:
            print(f"Response preview: {response.text[:500]}...")

        # Check for stok
        stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', response.text)
        if stok_match:
            print(f"SUCCESS! Found stok: {stok_match.group(1)}")
            return True

    except Exception as e:
        print(f"Error in approach 2: {e}")

    # Approach 3: Try JSON request
    print("\n--- Approach 3: JSON request to / ---")
    try:
        session.headers.update({
            'Content-Type': 'application/json',
            'Referer': f'{base_url}/webpages/login.html',
            'X-Requested-With': 'XMLHttpRequest'
        })

        json_data = {
            'method': 'login',
            'params': {
                'username': USERNAME,
                'password': PASSWORD
            }
        }

        if csrf_token:
            json_data['params']['csrf_token'] = csrf_token

        response = session.post(f"{base_url}/", json=json_data, timeout=10, allow_redirects=False)
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        # Check response content
        if len(response.text) < 1000:
            print(f"Response content: {response.text}")
        else:
            print(f"Response preview: {response.text[:500]}...")

        # Check for stok
        stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', response.text)
        if stok_match:
            print(f"SUCCESS! Found stok: {stok_match.group(1)}")
            return True

    except Exception as e:
        print(f"Error in approach 3: {e}")

    print("\n=== All approaches failed ===")
    return False

if __name__ == "__main__":
    debug_router_auth()

