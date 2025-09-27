#!/usr/bin/env python3

import requests
import re

def simulate_full_login():
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

    print("=== Simulating full login process ===")

    try:
        # Step 1: Get the login page
        print("Step 1: Getting login page...")
        login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
        print(f"Login page status code: {login_page_response.status_code}")
        print(f"Session cookies: {session.cookies.get_dict()}")

        # Step 2: Try to submit login form
        print("\nStep 2: Submitting login form...")
        login_data = {
            'method': 'login',
            'username': USERNAME,
            'password': PASSWORD
        }

        login_response = session.post(f"{base_url}/", data=login_data, timeout=10, allow_redirects=True)
        print(f"Login response status code: {login_response.status_code}")
        print(f"Final URL after login: {login_response.url}")
        print(f"Session cookies after login: {session.cookies.get_dict()}")

        # Check if we were redirected to index.html
        if '/webpages/index.html' in login_response.url:
            print("Successfully redirected to index page!")

            # Check for stok in the final URL
            stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', login_response.url)
            if stok_match:
                stok = stok_match.group(1)
                print(f"SUCCESS! Found valid stok: {stok}")

                # Now try to use this stok to access WAN status
                print(f"\nStep 3: Testing stok with WAN status API...")
                wan_url = f"{base_url}/cgi-bin/luci/;stok={stok}/admin/status?form=wan"
                wan_response = session.get(wan_url, timeout=10)
                print(f"WAN status response code: {wan_response.status_code}")

                if wan_response.status_code == 200:
                    print("Successfully accessed WAN status with valid stok!")
                    print(f"Response content: {wan_response.text[:500]}...")
                else:
                    print("Failed to access WAN status")

                return stok
            else:
                print("No stok found in redirect URL")
        else:
            print("Not redirected to index page")
            print(f"Response content: {login_response.text[:500] if len(login_response.text) > 500 else login_response.text}")

    except Exception as e:
        print(f"Error during login simulation: {e}")
        import traceback
        traceback.print_exc()

    return None

if __name__ == "__main__":
    stok = simulate_full_login()
    if stok:
        print(f"\nValid stok obtained: {stok}")
    else:
        print("\nFailed to obtain valid stok")

