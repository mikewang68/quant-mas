#!/usr/bin/env python3

import requests
import re

def check_su_framework():
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

    print("=== Checking SU framework implementation ===")
    try:
        # Get the SU framework script
        su_script_url = f"{base_url}/js/su/su.full.min.js"
        print(f"Fetching SU framework from: {su_script_url}")

        su_response = session.get(su_script_url, timeout=10)
        print(f"SU framework status code: {su_response.status_code}")
        print(f"Content length: {len(su_response.text)}")

        if su_response.status_code == 200:
            content = su_response.text

            # Look for Proxy implementation
            proxy_impl = re.findall(r'Proxy[^}]*url[^}]*', content)
            print(f"Proxy implementations found: {len(proxy_impl)}")

            for i, impl in enumerate(proxy_impl[:3]):  # First 3
                print(f"\nProxy implementation {i+1}:")
                print(impl[:300] + "..." if len(impl) > 300 else impl)

            # Look for read method implementation
            read_methods = re.findall(r'read[^}]*data[^}]*', content)
            print(f"\nRead method implementations found: {len(read_methods)}")

            for i, method in enumerate(read_methods[:2]):  # First 2
                print(f"\nRead method {i+1}:")
                print(method[:200] + "..." if len(method) > 200 else method)

            # Look for URL construction
            url_construct = re.findall(r'url[^}]*\+[^}]*', content)
            print(f"\nURL construction patterns found: {len(url_construct)}")

            # Look for any AJAX or HTTP request patterns
            ajax_patterns = re.findall(r'(ajax|post|get).*?url', content, re.IGNORECASE)
            print(f"\nAJAX/HTTP patterns: {ajax_patterns[:10]}")  # First 10

            # Look for form-related methods
            form_methods = re.findall(r'form.*?(submit|read|load)', content, re.IGNORECASE)
            print(f"\nForm methods: {form_methods[:10]}")  # First 10

    except Exception as e:
        print(f"Error checking SU framework: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_su_framework()

