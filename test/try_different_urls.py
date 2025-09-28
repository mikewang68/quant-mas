#!/usr/bin/env python3

import requests
import re

def try_different_urls():
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

    print("=== Trying different URLs and methods ===")

    # List of URLs to try
    urls_to_try = [
        f"{base_url}/login?form=login",
        f"{base_url}/cgi-bin/luci/login?form=login",
        f"{base_url}/cgi-bin/luci/",
        f"{base_url}/cgi-bin/luci/login",
        f"{base_url}/login",
        f"{base_url}/api/login",
        f"{base_url}/api/login?form=login",
    ]

    # List of data formats to try
    data_formats = [
        {
            'method': 'login',
            'username': USERNAME,
            'password': PASSWORD
        },
        {
            'operation': 'login',
            'username': USERNAME,
            'password': PASSWORD
        },
        {
            'action': 'login',
            'username': USERNAME,
            'password': PASSWORD
        }
    ]

    # Try different combinations
    for url in urls_to_try:
        print(f"\n--- Trying URL: {url} ---")

        for i, data in enumerate(data_formats, 1):
            print(f"  Data format {i}: {data}")

            try:
                # Try POST
                session.headers.clear()
                session.headers.update(headers)
                response = session.post(url, data=data, timeout=10)
                print(f"    POST status: {response.status_code}")

                if response.status_code == 200:
                    # Check for stok in response
                    stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', response.text)
                    if stok_match:
                        stok = stok_match.group(1)
                        print(f"    SUCCESS! Found stok: {stok}")
                        return stok

                    # Check for JSON response with stok
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        try:
                            json_data = response.json()
                            if 'stok' in json_data:
                                print(f"    SUCCESS! Found stok in JSON: {json_data['stok']}")
                                return json_data['stok']
                        except:
                            pass

                # If POST failed, try GET with parameters
                if response.status_code != 200:
                    get_response = session.get(url, params=data, timeout=10)
                    print(f"    GET status: {get_response.status_code}")

                    if get_response.status_code == 200:
                        stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', get_response.text)
                        if stok_match:
                            stok = stok_match.group(1)
                            print(f"    SUCCESS! Found stok in GET response: {stok}")
                            return stok

            except Exception as e:
                print(f"    Error: {e}")

    print("\n=== All URL/method combinations failed ===")
    return None

if __name__ == "__main__":
    stok = try_different_urls()
    if stok:
        print(f"\nValid stok obtained: {stok}")
    else:
        print("\nFailed to obtain valid stok")
        print("\nRecommendation: Try using Selenium to simulate browser behavior")

