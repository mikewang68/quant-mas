#!/usr/bin/env python3

import requests
import re

def find_public_endpoints():
    # Router configuration
    ROUTER_IP = "192.168.1.1"
    base_url = f"http://{ROUTER_IP}"

    # Create a session
    session = requests.Session()

    # Set headers to mimic a browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/html, */*; q=0.01',
    })

    print("=== Finding public endpoints ===")

    # Common router endpoints to try
    common_endpoints = [
        "/",
        "/webpages/login.html",
        "/webpages/index.html",
        "/status",
        "/api/status",
        "/api/info",
        "/info",
        "/api/version",
        "/version",
        "/api/wan",
        "/wan",
        "/cgi-bin/luci",
        "/cgi-bin/luci/",
        "/admin",
        "/admin/status",
        "/admin/wan",
    ]

    for i, endpoint in enumerate(common_endpoints, 1):
        url = f"{base_url}{endpoint}"
        print(f"\n--- Test {i}: {url} ---")
        try:
            response = session.get(url, timeout=5)
            print(f"Status code: {response.status_code}")

            # For successful responses, check content
            if response.status_code == 200:
                print(f"Content length: {len(response.text)}")

                # Check if it's JSON
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    print("Content type: JSON")
                    try:
                        json_data = response.json()
                        print(f"JSON keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict'}")
                    except:
                        print("Failed to parse as JSON")
                else:
                    print(f"Content type: {content_type}")
                    # Look for interesting patterns in HTML/text
                    if len(response.text) < 1000:
                        print(f"Content preview: {response.text}")
                    else:
                        print(f"Content preview: {response.text[:500]}...")

                        # Look for IP addresses
                        ip_matches = re.findall(r'([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', response.text)
                        if ip_matches:
                            print(f"IP addresses found: {ip_matches[:5]}")

        except Exception as e:
            print(f"Error accessing {url}: {e}")

if __name__ == "__main__":
    find_public_endpoints()

