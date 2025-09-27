#!/usr/bin/env python3

import requests
import re

def check_js_libraries():
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

    print("=== Checking for JavaScript libraries ===")
    try:
        # Get the login page
        login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
        content = login_page_response.text

        # Look for script tags
        script_tags = re.findall(r'<script[^>]*src=["\']([^"\']*)["\'][^>]*>', content)
        print(f"Script tags with src found: {len(script_tags)}")

        # Look for jQuery or other library references
        jquery_refs = [tag for tag in script_tags if 'jquery' in tag.lower()]
        print(f"jQuery references: {jquery_refs}")

        # Look for any custom framework references
        custom_refs = [tag for tag in script_tags if any(word in tag.lower() for word in ['su', 'tplink', 'widget'])]
        print(f"Custom framework references: {custom_refs}")

        # Look for form or widget related scripts
        form_scripts = [tag for tag in script_tags if any(word in tag.lower() for word in ['form', 'widget', 'login'])]
        print(f"Form/widget related scripts: {form_scripts}")

        # Look for any authentication or security related scripts
        auth_scripts = [tag for tag in script_tags if any(word in tag.lower() for word in ['auth', 'security', 'encrypt'])]
        print(f"Auth/security related scripts: {auth_scripts}")

        # Print first 10 script tags
        print(f"\nFirst 10 script tags:")
        for i, tag in enumerate(script_tags[:10]):
            print(f"  {i+1}: {tag}")

        # Look for inline scripts that might contain form handling logic
        inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
        print(f"\nInline scripts found: {len(inline_scripts)}")

        # Look for scripts that might handle form submission
        form_submit_scripts = [script for script in inline_scripts if 'submit' in script.lower() and ('form' in script.lower() or 'login' in script.lower())]
        print(f"Form submission scripts: {len(form_submit_scripts)}")

        for i, script in enumerate(form_submit_scripts[:2]):  # First 2
            print(f"\nForm submit script {i+1}:")
            print(script[:500] + "..." if len(script) > 500 else script)

    except Exception as e:
        print(f"Error checking JS libraries: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_js_libraries()

