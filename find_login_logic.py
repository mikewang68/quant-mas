#!/usr/bin/env python3

import requests
import re

def find_login_logic():
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

    print("=== Finding login logic ===")
    try:
        # Get the login page
        login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
        content = login_page_response.text

        # Look for all AJAX calls to understand the pattern
        ajax_calls = re.findall(r'\$.ajax\s*\(\s*{[^}]*url[^}]*[^}]*}\s*\)', content)
        print(f"Total AJAX calls found: {len(ajax_calls)}")

        login_ajax_calls = [call for call in ajax_calls if 'login' in call.lower()]
        print(f"Login-related AJAX calls: {len(login_ajax_calls)}")

        for i, call in enumerate(login_ajax_calls[:5]):  # First 5
            print(f"\nLogin AJAX call {i+1}:")
            print(call[:800] + "..." if len(call) > 800 else call)

            # Extract URL
            url_match = re.search(r'url\s*:\s*["\']([^"\']*)["\']', call)
            if url_match:
                print(f"  URL: {url_match.group(1)}")

            # Extract data
            data_match = re.search(r'data\s*:\s*({[^}]*)', call)
            if data_match:
                print(f"  Data pattern: {data_match.group(1)}")

        # Look for any references to CGI endpoints
        cgi_matches = re.findall(r'["\'](/cgi-bin/[^\s"\']*)["\']', content)
        print(f"\nCGI endpoints found: {list(set(cgi_matches))}")

        # Look for login-related CGI endpoints
        login_cgi_matches = [endpoint for endpoint in cgi_matches if 'login' in endpoint.lower()]
        print(f"Login-related CGI endpoints: {login_cgi_matches}")

        # Look for any references to form submissions with method=login
        form_method_matches = re.findall(r'["\']method["\']\s*:\s*["\']login["\']', content)
        print(f"\n'method': 'login' references found: {len(form_method_matches)}")

        # Look for any references to operation=login
        operation_matches = re.findall(r'["\']operation["\']\s*:\s*["\']login["\']', content)
        print(f"'operation': 'login' references found: {len(operation_matches)}")

        # Look for password encryption or processing
        password_processing = re.findall(r'(encrypt|encode|md5|sha).*?pass', content, re.IGNORECASE)
        print(f"Password processing functions: {password_processing}")

    except Exception as e:
        print(f"Error finding login logic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_login_logic()

