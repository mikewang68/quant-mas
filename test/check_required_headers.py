#!/usr/bin/env python3

import requests
import re

def check_required_headers():
    # Router configuration
    ROUTER_IP = "192.168.1.1"
    USERNAME = "wangdg68"
    PASSWORD = "wap951020ZJL"
    base_url = f"http://{ROUTER_IP}"

    # Create a session
    session = requests.Session()

    print("=== Checking for required headers and cookies ===")

    try:
        # First, get the login page to establish session and get cookies
        print("Step 1: Getting login page...")
        login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
        print(f"Login page status code: {login_page_response.status_code}")
        print(f"Initial cookies: {session.cookies.get_dict()}")

        # Look for any Set-Cookie headers in the response
        set_cookie_headers = login_page_response.headers.get('Set-Cookie', '')
        if set_cookie_headers:
            print(f"Set-Cookie headers: {set_cookie_headers}")

        # Try to submit login with all possible headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'{base_url}/webpages/login.html',
            'Origin': base_url,
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
        }

        print(f"\nStep 2: Submitting login with full headers...")
        session.headers.clear()
        session.headers.update(headers)

        login_data = {
            'method': 'login',
            'username': USERNAME,
            'password': PASSWORD
        }

        login_response = session.post(f"{base_url}/", data=login_data, timeout=10)
        print(f"Login response status code: {login_response.status_code}")
        print(f"Cookies after login: {session.cookies.get_dict()}")

        # Check response
        if login_response.status_code == 200:
            content = login_response.text
            print(f"Response content length: {len(content)}")

            # Check for stok
            stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', content)
            if stok_match:
                stok = stok_match.group(1)
                print(f"SUCCESS! Found stok: {stok}")
                return stok

            # Check for JSON response
            content_type = login_response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                try:
                    json_data = login_response.json()
                    print(f"JSON response: {json_data}")
                    if 'stok' in json_data:
                        print(f"SUCCESS! Found stok in JSON: {json_data['stok']}")
                        return json_data['stok']
                except:
                    pass

            # Show first 500 chars of response if not too short
            if len(content) > 500:
                print(f"Response preview: {content[:500]}...")
            else:
                print(f"Response content: {content}")

    except Exception as e:
        print(f"Error checking required headers: {e}")
        import traceback
        traceback.print_exc()

    return None

if __name__ == "__main__":
    stok = check_required_headers()
    if stok:
        print(f"\nValid stok obtained: {stok}")
    else:
        print("\nFailed to obtain valid stok")

