#!/usr/bin/env python3

import requests
import re
import json

def check_successful_responses():
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

    print("=== Checking successful response content ===")

    # Test the successful URLs
    successful_urls = [
        f"{base_url}/cgi-bin/luci/login?form=login",
        f"{base_url}/cgi-bin/luci/login"
    ]

    data_formats = [
        {
            'method': 'login',
            'username': USERNAME,
            'password': PASSWORD
        },
        {
            'action': 'login',
            'username': USERNAME,
            'password': PASSWORD
        }
    ]

    for url in successful_urls:
        print(f"\n--- Testing URL: {url} ---")

        for i, data in enumerate(data_formats, 1):
            print(f"  Data format {i}: {data}")

            try:
                # Try POST
                session.headers.clear()
                session.headers.update(headers)
                response = session.post(url, data=data, timeout=10)
                print(f"    Status: {response.status_code}")
                print(f"    Content-Type: {response.headers.get('Content-Type', 'Unknown')}")

                # Print response details
                content = response.text
                print(f"    Response length: {len(content)}")

                # Check for stok in response
                stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', content)
                if stok_match:
                    stok = stok_match.group(1)
                    print(f"    SUCCESS! Found stok: {stok}")
                    return stok

                # Check for JSON response with stok
                if 'application/json' in response.headers.get('Content-Type', '', '').lower():
                    try:
                        json_data = response.json()
                        print(f"    JSON response: {json_data}")
                        if 'stok' in json_data:
                            print(f"    SUCCESS! Found stok in JSON: {json_data['stok']}")
                            return json_data['stok']
                        if 'error_code' in json_data:
                            print(f"    Error code: {json_data['error_code']}")
                    except Exception as json_e:
                        print(f"    JSON parsing error: {json_e}")

                # Show preview of response
                preview = content[:1000] if len(content) > 1000 else content
                print(f"    Response preview: {preview}")

            except Exception as e:
                print(f"    Error: {e}")

    print("\n=== No valid stok found in successful responses ===")
    return None

if __name__ == "__main__":
    stok = check_successful_responses()
    if stok:
        print(f"\nValid stok obtained: {stok}")
    else:
        print("\nFailed to obtain valid stok")

