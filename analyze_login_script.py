#!/usr/bin/env python3

import requests
import re

def analyze_login_script():
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

    print("=== Analyzing login script ===")
    try:
        # Get the login page
        login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
        content = login_page_response.text

        # Extract the inline script that contains login logic
        inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
        login_scripts = [script for script in inline_scripts if 'login' in script.lower()]

        if login_scripts:
            login_script = login_scripts[0]
            print("Found login script:")
            print(login_script[:1000] + "..." if len(login_script) > 1000 else login_script)

            # Look for the login URL
            login_url_match = re.search(r'LOGIN_URL\s*=\s*.*?url\(["\']([^"\']*)["\']\)', login_script)
            if login_url_match:
                login_url = login_url_match.group(1)
                print(f"\nLogin URL: {login_url}")

            # Look for how the login proxy is used
            proxy_usage = re.findall(r'loginProxy\.[^(]*\([^}]*\}', login_script)
            print(f"\nLogin proxy usage found: {len(proxy_usage)}")

            for usage in proxy_usage:
                print(f"Proxy usage: {usage[:300] + '...' if len(usage) > 300 else usage}")

                # Look for data being sent
                data_match = re.search(r'data\s*:\s*({[^}]*)', usage)
                if data_match:
                    print(f"  Data: {data_match.group(1)}")

            # Look for form submission logic
            submit_logic = re.findall(r'submit[^}]*{[^}]*}', login_script)
            print(f"\nSubmit logic found: {len(submit_logic)}")

            for logic in submit_logic:
                print(f"Submit logic: {logic}")

        else:
            print("No login script found")

        # Look for any references to encrypt.js usage
        encrypt_refs = re.findall(r'encrypt.*?pass', content, re.IGNORECASE)
        print(f"\nEncrypt references: {encrypt_refs}")

    except Exception as e:
        print(f"Error analyzing login script: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_login_script()

