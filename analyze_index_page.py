#!/usr/bin/env python3

import requests
import re

def analyze_index_page():
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

    print("=== Analyzing index page ===")
    try:
        # Get the index page
        index_response = session.get(f"{base_url}/webpages/index.html", timeout=10)
        content = index_response.text
        print(f"Index page content length: {len(content)}")

        # Save the index page for analysis
        with open('index_page.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Index page saved to index_page.html")

        # Look for JavaScript variables and functions
        js_vars = re.findall(r'var\s+(\w+)\s*=\s*([^;]+);', content)
        print(f"JavaScript variables found: {len(js_vars)}")

        # Look for stok-related variables
        stok_vars = [var for var in js_vars if 'stok' in var[0].lower() or 'stok' in var[1].lower()]
        print(f"stok-related variables: {stok_vars}")

        # Look for API URLs or endpoints
        urls = re.findall(r'https?://[^\s"\'>]+', content)
        local_urls = [url for url in urls if ROUTER_IP in url]
        print(f"Local URLs found: {len(local_urls)}")

        for url in local_urls[:10]:  # First 10
            print(f"  {url}")

        # Look for AJAX calls in the index page
        ajax_calls = re.findall(r'\$.ajax\s*\([^}]*\}', content)
        print(f"\nAJAX calls found: {len(ajax_calls)}")

        for i, call in enumerate(ajax_calls[:3]):  # First 3
            print(f"\nAJAX call {i+1}:")
            print(call[:300] + "..." if len(call) > 300 else call)

            # Extract URL from AJAX call
            url_match = re.search(r'url\s*:\s*["\']([^"\']*)["\']', call)
            if url_match:
                print(f"  URL: {url_match.group(1)}")

        # Look for form actions
        form_actions = re.findall(r'action=["\']([^"\']*)["\']', content)
        print(f"\nForm actions found: {form_actions}")

        # Look for any references to WAN or network control
        wan_controls = re.findall(r'(wan[0-9]*|disconnect|connect|reboot)[^(]*\([^)]*\)', content, re.IGNORECASE)
        print(f"\nWAN control functions: {wan_controls[:10]}")  # First 10

        # Look for any configuration objects
        config_objects = re.findall(r'var\s+\w+\s*=\s*{[^}]*}', content)
        print(f"\nConfiguration objects found: {len(config_objects)}")

        # Look for objects that might contain API endpoints
        api_objects = [obj for obj in config_objects if any(word in obj.lower() for word in ['api', 'url', 'endpoint'])]
        for i, obj in enumerate(api_objects[:2]):  # First 2
            print(f"\nAPI object {i+1}:")
            print(obj[:300] + "..." if len(obj) > 300 else obj)

    except Exception as e:
        print(f"Error analyzing index page: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_index_page()

