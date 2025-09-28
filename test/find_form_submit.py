#!/usr/bin/env python3

import requests
import re

def find_form_submit():
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

    print("=== Finding form submit implementation ===")
    try:
        # Get the login page
        login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
        content = login_page_response.text

        # Look for the form submit function or plugin
        form_submit_matches = re.findall(r'form\([^)]*\)\s*["\']submit["\']\s*,\s*({[^}]*})', content)
        print(f"Form submit calls found: {len(form_submit_matches)}")

        for i, match in enumerate(form_submit_matches):
            print(f"Form submit call {i+1}:")
            print(match)
            print()

        # Look for form plugin implementation
        form_plugin_matches = re.findall(r'\.form\s*\([^}]*submit[^}]*}', content)
        print(f"Form plugin implementations found: {len(form_plugin_matches)}")

        for i, match in enumerate(form_plugin_matches[:3]):  # First 3
            print(f"Form plugin {i+1}:")
            print(match[:500] + "..." if len(match) > 500 else match)
            print()

        # Look for AJAX implementation that might be used by the form plugin
        ajax_impl_matches = re.findall(r'\$.ajax\s*\({[^}]*url[^}]*}', content)
        print(f"AJAX implementations found: {len(ajax_impl_matches)}")

        for i, match in enumerate(ajax_impl_matches[:3]):  # First 3
            print(f"AJAX implementation {i+1}:")
            print(match[:300] + "..." if len(match) > 300 else match)

            # Extract URL and data from AJAX call
            url_match = re.search(r'url\s*:\s*["\']([^"\']*)["\']', match)
            if url_match:
                print(f"  URL: {url_match.group(1)}")

            data_match = re.search(r'data\s*:\s*({[^}]*})', match)
            if data_match:
                print(f"  Data: {data_match.group(1)}")

            print()

        # Look for any references to the login endpoint
        login_endpoints = re.findall(r'["\'](\/[^\s"\']*login[^\s"\']*)["\']', content)
        print(f"Login endpoints found: {list(set(login_endpoints))}")

    except Exception as e:
        print(f"Error finding form submit implementation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_form_submit()

