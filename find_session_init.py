#!/usr/bin/env python3

import requests
import re

def find_session_init():
    # Router configuration
    ROUTER_IP = "192.168.1.1"
    base_url = f"http://{ROUTER_IP}"

    # Create a session
    session = requests.Session()

    # Set headers to mimic a browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    })

    print("=== Finding session initialization calls ===")
    try:
        # Get the login page
        login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
        content = login_page_response.text

        # Look for any AJAX calls that might initialize the session
        ajax_calls = re.findall(r'\$.ajax\s*\([^}]*\}', content)
        print(f"Total AJAX calls found: {len(ajax_calls)}")

        # Look for calls that might initialize session or get tokens
        init_calls = [call for call in ajax_calls if any(word in call.lower() for word in ['init', 'token', 'stok', 'session', 'start'])]
        print(f"Session initialization calls: {len(init_calls)}")

        for i, call in enumerate(init_calls[:5]):  # First 5
            print(f"\nInit call {i+1}:")
            print(call[:500] + "..." if len(call) > 500 else call)

            # Extract URL
            url_match = re.search(r'url\s*:\s*["\']([^"\']*)["\']', call)
            if url_match:
                print(f"  URL: {url_match.group(1)}")

        # Look for any calls to login page with parameters
        login_page_calls = re.findall(r'location\.href\s*=\s*["\'][^"\']*login[^"\']*["\']', content)
        print(f"\nLogin page redirect calls: {len(login_page_calls)}")

        for call in login_page_calls:
            print(f"  {call}")

        # Look for any references to "pre-login" or similar
        pre_login_refs = re.findall(r'pre[-_]login|before[-_]login', content, re.IGNORECASE)
        print(f"\nPre-login references: {pre_login_refs}")

        # Look for any calls that might set up the environment before login
        setup_calls = re.findall(r'\w+\s*\([^}]*\)\s*;\s*//\s*(setup|init|pre)', content, re.IGNORECASE)
        print(f"Setup calls with comments: {len(setup_calls)}")

        # Look for any document.ready or similar initialization functions
        init_functions = re.findall(r'(document\.ready|function\s*\(\s*\)\s*{[^}]*pre[-_]login)', content)
        print(f"Init functions: {len(init_functions)}")

    except Exception as e:
        print(f"Error finding session init: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_session_init()

