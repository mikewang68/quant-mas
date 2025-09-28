#!/usr/bin/env python3

import requests
import re

def try_direct_post():
    # Router configuration
    ROUTER_IP = "192.168.1.1"
    USERNAME = "wangdg68"
    PASSWORD = "wap951020ZJL"
    base_url = f"http://{ROUTER_IP}"

    # Create a session
    session = requests.Session()

    # Set headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'{base_url}/webpages/login.html',
    }

    print("=== Trying direct POST to root URL ===")

    # First, get the login page to establish session
    print("Getting login page...")
    login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
    print(f"Login page status code: {login_page_response.status_code}")

    # Try different data formats with proper headers
    test_cases = [
        {
            "name": "Method login with username/password",
            "data": {
                'method': 'login',
                'username': USERNAME,
                'password': PASSWORD
            },
            "headers": headers
        },
        {
            "name": "Operation login with username/password",
            "data": {
                'operation': 'login',
                'username': USERNAME,
                'password': PASSWORD
            },
            "headers": headers
        },
        {
            "name": "Action login with username/password",
            "data": {
                'action': 'login',
                'username': USERNAME,
                'password': PASSWORD
            },
            "headers": headers
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        print(f"Data: {test_case['data']}")

        try:
            # Update headers for this test
            session.headers.clear()
            session.headers.update(test_case['headers'])

            response = session.post(f"{base_url}/", data=test_case['data'], timeout=10)
            print(f"Status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")

            # Print response content (first 1000 chars)
            content_preview = response.text[:1000] if len(response.text) > 1000 else response.text
            print(f"Response content: {content_preview}")

            # Check for stok in response
            stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', response.text)
            if stok_match:
                print(f"SUCCESS! Found stok in response: {stok_match.group(1)}")
                return True

            # Check for JSON response with stok
            if 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    json_data = response.json()
                    if 'stok' in json_data:
                        print(f"SUCCESS! Found stok in JSON: {json_data['stok']}")
                        return True
                    print(f"JSON response: {json_data}")
                except:
                    pass

        except Exception as e:
            print(f"Error in test {i}: {e}")

    # Try with different Content-Type
    print(f"\n--- Test with different Content-Type ---")
    json_headers = headers.copy()
    json_headers['Content-Type'] = 'application/json'

    json_data = {
        'method': 'login',
        'username': USERNAME,
        'password': PASSWORD
    }

    try:
        session.headers.clear()
        session.headers.update(json_headers)
        response = session.post(f"{base_url}/", json=json_data, timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        # Print response content (first 1000 chars)
        content_preview = response.text[:1000] if len(response.text) > 1000 else response.text
        print(f"Response content: {content_preview}")

        # Check for stok in response
        stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', response.text)
        if stok_match:
            print(f"SUCCESS! Found stok in response: {stok_match.group(1)}")
            return True

    except Exception as e:
        print(f"Error in JSON test: {e}")

    print("\n=== All tests failed ===")
    return False

if __name__ == "__main__":
    try_direct_post()

