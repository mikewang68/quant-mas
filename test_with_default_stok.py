#!/usr/bin/env python3

import requests
import re
import json

def test_with_default_stok():
    # Router configuration
    ROUTER_IP = "192.168.1.1"
    base_url = f"http://{ROUTER_IP}"
    DEFAULT_STOK = "12345"

    # Create a session
    session = requests.Session()

    # Set headers to mimic a browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'{base_url}/webpages/index.html',
    })

    print("=== Testing with default stok ===")

    # Try different API endpoints with the default stok
    endpoints_to_try = [
        f"{base_url}/cgi-bin/luci/;stok={DEFAULT_STOK}/admin/status?form=wan",
        f"{base_url}/cgi-bin/luci/;stok={DEFAULT_STOK}/admin/network?form=wan_status",
        f"{base_url}/cgi-bin/luci/;stok={DEFAULT_STOK}/admin/status?form=all",
        f"{base_url}/admin/status?form=wan",
        f"{base_url}/admin/network?form=wan_status"
    ]

    for i, url in enumerate(endpoints_to_try, 1):
        print(f"\n--- Test {i}: {url} ---")
        try:
            response = session.get(url, timeout=10)
            print(f"Status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")

            # Print response content (first 1000 chars)
            content_preview = response.text[:1000] if len(response.text) > 1000 else response.text
            print(f"Response content: {content_preview}")

            # Try to parse as JSON
            if response.headers.get('Content-Type', '').startswith('application/json'):
                try:
                    json_data = response.json()
                    print(f"JSON data: {json_data}")
                except:
                    pass

            # Look for IP addresses in response
            ip_matches = re.findall(r'([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', response.text)
            valid_ips = []
            for ip in ip_matches:
                if is_valid_public_ip(ip):
                    valid_ips.append(ip)

            if valid_ips:
                print(f"Valid public IPs found: {valid_ips}")

        except Exception as e:
            print(f"Error in test {i}: {e}")

def is_valid_public_ip(ip):
    """验证是否为有效的公网IP地址"""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        for part in parts:
            num = int(part)
            if num < 0 or num > 255:
                return False
        # 排除一些常见的非公网IP
        if parts[0] == '127' or (parts[0] == '192' and parts[1] == '168') or parts[0] == '10':
            return False
        if parts[0] == '172' and 16 <= int(parts[1]) <= 31:
            return False
        return True
    except:
        return False

if __name__ == "__main__":
    test_with_default_stok()

