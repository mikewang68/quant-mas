#!/usr/bin/env python3

import requests
import re

def test_login_endpoint():
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
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'{base_url}/webpages/login.html',
    })

    print("=== Testing login endpoint ===")

    # First, get the login page to establish session
    print("Getting login page...")
    login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
    print(f"Login page status code: {login_page_response.status_code}")
    print(f"Session cookies: {session.cookies.get_dict()}")

    # Try the login endpoint we found
    login_url = f"{base_url}/login?form=login"
    print(f"\nTrying login endpoint: {login_url}")

    # Try different data formats
    data_formats = [
        # Format 1: Simple form data
        {
            'method': 'login',
            'username': USERNAME,
            'password': PASSWORD
        },
        # Format 2: With operation parameter
        {
            'operation': 'login',
            'username': USERNAME,
            'password': PASSWORD
        }
    ]

    for i, data in enumerate(data_formats, 1):
        print(f"\n--- Test {i} with data: {data} ---")
        try:
            response = session.post(login_url, data=data, timeout=10)
            print(f"Status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Session cookies after request: {session.cookies.get_dict()}")

            # Print response content (first 1000 chars)
            content_preview = response.text[:1000] if len(response.text) > 1000 else response.text
            print(f"Response content: {content_preview}")

            # Check for stok in response
            stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', response.text)
            if stok_match:
                print(f"SUCCESS! Found stok in response: {stok_match.group(1)}")
                return True

            # Check for JSON response with stok
            if response.headers.get('Content-Type', '').startswith('application/json'):
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

    # Try JSON format
    print(f"\n--- Test with JSON data ---")
    session.headers.update({
        'Content-Type': 'application/json; charset=UTF-8',
    })

    json_data = {
        'method': 'login',
        'params': {
            'username': USERNAME,
            'password': PASSWORD
        }
    }

    try:
        response = session.post(login_url, json=json_data, timeout=10)
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
        if response.headers.get('Content-Type', '').startswith('application/json'):
            try:
                json_data_response = response.json()
                if 'stok' in json_data_response:
                    print(f"SUCCESS! Found stok in JSON: {json_data_response['stok']}")
                    return True
                print(f"JSON response: {json_data_response}")
            except:
                pass

    except Exception as e:
        print(f"Error in JSON test: {e}")

    print("\n=== All tests failed ===")
    return False

if __name__ == "__main__":
    test_login_endpoint()

