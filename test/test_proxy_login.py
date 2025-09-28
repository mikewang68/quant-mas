#!/usr/bin/env python3

import requests
import re
import json

def test_proxy_login():
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

    print("=== Testing proxy-style login ===")

    # Try the login URL we found
    login_url = f"{base_url}/login?form=login"
    print(f"Login URL: {login_url}")

    # Try different data formats that might work with the proxy
    test_cases = [
        {
            "name": "Method login with username/password",
            "data": {
                'method': 'login',
                'username': USERNAME,
                'password': PASSWORD
            }
        },
        {
            "name": "JSON-style data",
            "data": {
                'method': 'login',
                'params': {
                    'username': USERNAME,
                    'password': PASSWORD
                }
            }
        },
        {
            "name": "Operation style",
            "data": {
                'operation': 'login',
                'username': USERNAME,
                'password': PASSWORD
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        print(f"Data: {test_case['data']}")

        try:
            # Update session headers
            session.headers.clear()
            session.headers.update(headers)

            # Try as form data
            response = session.post(login_url, data=test_case['data'], timeout=10)
            print(f"Form POST status code: {response.status_code}")

            if response.status_code == 200:
                print(f"Response content: {response.text[:500] if len(response.text) > 500 else response.text}")

                # Check for JSON response
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    try:
                        json_data = response.json()
                        print(f"JSON response: {json_data}")

                        if 'stok' in json_data:
                            print(f"SUCCESS! Found stok: {json_data['stok']}")
                            return json_data['stok']
                    except:
                        pass

                # Check for stok in response text
                stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', response.text)
                if stok_match:
                    stok = stok_match.group(1)
                    print(f"SUCCESS! Found stok in response: {stok}")
                    return stok

        except Exception as e:
            print(f"Error in form POST test {i}: {e}")

        # Try as JSON data
        try:
            json_headers = headers.copy()
            json_headers['Content-Type'] = 'application/json; charset=UTF-8'
            session.headers.clear()
            session.headers.update(json_headers)

            response = session.post(login_url, json=test_case['data'], timeout=10)
            print(f"JSON POST status code: {response.status_code}")

            if response.status_code == 200:
                print(f"Response content: {response.text[:500] if len(response.text) > 500 else response.text}")

                # Check for JSON response
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    try:
                        json_data = response.json()
                        print(f"JSON response: {json_data}")

                        if 'stok' in json_data:
                            print(f"SUCCESS! Found stok: {json_data['stok']}")
                            return json_data['stok']
                    except:
                        pass

        except Exception as e:
            print(f"Error in JSON POST test {i}: {e}")

    print("\n=== All tests failed ===")
    return None

if __name__ == "__main__":
    stok = test_proxy_login()
    if stok:
        print(f"\nValid stok obtained: {stok}")
    else:
        print("\nFailed to obtain valid stok")

