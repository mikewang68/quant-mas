#!/usr/bin/env python3

import requests
import re

def analyze_login_js():
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

    print("=== Analyzing login JavaScript ===")
    try:
        # Get the login page
        login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
        content = login_page_response.text

        # Look for the doLogin function in detail
        do_login_match = re.search(r'function\s+doLogin\s*\([^)]*\)\s*{([^}]+(?:}[^}]+)*})', content)
        if do_login_match:
            do_login_function = do_login_match.group(1)
            print("=== doLogin function ===")
            print(do_login_function[:2000])  # Show more content
            print("..." if len(do_login_function) > 2000 else "")

            # Look for AJAX calls in doLogin
            ajax_calls = re.findall(r'\$.ajax\([^}]*}', do_login_function)
            print(f"\nAJAX calls in doLogin: {len(ajax_calls)}")
            for i, call in enumerate(ajax_calls):
                print(f"AJAX call {i+1}:")
                print(call[:500] + "..." if len(call) > 500 else call)
                print()

            # Look for URL in AJAX calls
            url_matches = re.findall(r'url\s*:\s*["\']([^"\']*)["\']', do_login_function)
            print(f"URLs found in AJAX calls: {url_matches}")

            # Look for data in AJAX calls
            data_matches = re.findall(r'data\s*:\s*({[^}]*})', do_login_function)
            print(f"Data objects found in AJAX calls: {data_matches}")

            # Look for password processing
            password_refs = re.findall(r'(pass|pwd)[^;]*', do_login_function, re.IGNORECASE)
            print(f"Password references: {password_refs[:10]}")  # First 10

        else:
            print("doLogin function not found")

        # Look for normal_login function
        normal_login_match = re.search(r'function\s+normal_login\s*\([^)]*\)\s*{([^}]+(?:}[^}]+)*})', content)
        if normal_login_match:
            normal_login_function = normal_login_match.group(1)
            print("\n=== normal_login function ===")
            print(normal_login_function[:1000])
            print("..." if len(normal_login_function) > 1000 else "")

        # Look for password encryption functions
        encrypt_functions = re.findall(r'function\s+(\w*encrypt\w*|\w*pwd\w*|\w*pass\w*)\s*\([^)]*\)', content, re.IGNORECASE)
        print(f"\nPotential encryption/password functions: {encrypt_functions[:10]}")

        # Look for specific encryption patterns
        encrypt_patterns = [
            r'encrypt\(.*?password',
            r'encode\(.*?password',
            r'md5\(.*?password',
            r'sha.*?password',
            r'base64.*?password'
        ]

        for pattern in encrypt_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"Pattern '{pattern}' matches: {matches[:5]}")

    except Exception as e:
        print(f"Error analyzing login JavaScript: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_login_js()

