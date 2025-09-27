#!/usr/bin/env python3

import requests
import re

def analyze_login_page():
    # Router configuration
    ROUTER_IP = "192.168.1.1"
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

    print("=== Analyzing login page ===")
    try:
        # Get the login page
        login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
        print(f"Login page status code: {login_page_response.status_code}")
        print(f"Login page content length: {len(login_page_response.text)}")
        print(f"Session cookies: {session.cookies.get_dict()}")

        # Save the login page content for analysis
        with open('login_page.html', 'w', encoding='utf-8') as f:
            f.write(login_page_response.text)
        print("Login page saved to login_page.html")

        # Look for the login form
        form_match = re.search(r'<form[^>]*id=["\']?login[^>]*>(.*?)</form>', login_page_response.text, re.DOTALL | re.IGNORECASE)
        if form_match:
            form_content = form_match.group(1)
            print(f"\nLogin form found:")
            print(form_content[:1000] + "..." if len(form_content) > 1000 else form_content)

            # Look for form action
            action_match = re.search(r'action=["\']([^"\']*)["\']', form_match.group(0))
            if action_match:
                print(f"\nForm action: {action_match.group(1)}")

            # Look for form method
            method_match = re.search(r'method=["\']([^"\']*)["\']', form_match.group(0))
            if method_match:
                print(f"Form method: {method_match.group(1)}")
        else:
            print("\nNo login form found with id containing 'login'")

        # Look for all forms
        all_forms = re.findall(r'<form[^>]*>(.*?)</form>', login_page_response.text, re.DOTALL | re.IGNORECASE)
        print(f"\nTotal forms found: {len(all_forms)}")

        # Look for JavaScript functions related to login
        login_js = re.findall(r'function\s+(\w*login\w*)\s*\([^)]*\)\s*{([^}]*)}', login_page_response.text, re.IGNORECASE)
        print(f"\nLogin-related JavaScript functions found: {len(login_js)}")
        for func_name, func_body in login_js[:3]:  # Show first 3
            print(f"Function: {func_name}")
            print(f"Body: {func_body[:200]}..." if len(func_body) > 200 else func_body)
            print()

        # Look for password encryption functions
        encrypt_js = re.findall(r'(encrypt|encode|md5|sha).*?function.*?password', login_page_response.text, re.IGNORECASE)
        if encrypt_js:
            print(f"Password encryption functions found: {encrypt_js}")

        # Look for any AJAX calls related to login
        ajax_calls = re.findall(r'\$.ajax\([^)]*url[^)]*\)', login_page_response.text, re.IGNORECASE)
        print(f"\nAJAX calls found: {len(ajax_calls)}")
        for call in ajax_calls[:2]:
            print(call[:200] + "..." if len(call) > 200 else call)
            print()

    except Exception as e:
        print(f"Error analyzing login page: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_login_page()

