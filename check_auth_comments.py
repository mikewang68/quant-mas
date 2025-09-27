#!/usr/bin/env python3

import requests
import re

def check_auth_comments():
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

    print("=== Checking for authentication comments or documentation ===")
    try:
        # Get the login page
        login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
        content = login_page_response.text

        # Look for comments
        comments = re.findall(r'<!--.*?-->', content, re.DOTALL)
        print(f"Comments found: {len(comments)}")

        auth_comments = [comment for comment in comments if any(word in comment.lower() for word in ['auth', 'login', 'token', 'stok'])]
        print(f"Authentication-related comments: {len(auth_comments)}")

        for i, comment in enumerate(auth_comments[:3]):  # First 3
            print(f"\nAuth comment {i+1}:")
            print(comment[:500] + "..." if len(comment) > 500 else comment)

        # Look for JavaScript comments
        js_comments = re.findall(r'/\*.*?\*/', content, re.DOTALL)
        print(f"\nJavaScript comments found: {len(js_comments)}")

        auth_js_comments = [comment for comment in js_comments if any(word in comment.lower() for word in ['auth', 'login', 'token', 'stok'])]
        print(f"Authentication-related JS comments: {len(auth_js_comments)}")

        for i, comment in enumerate(auth_js_comments[:3]):  # First 3
            print(f"\nAuth JS comment {i+1}:")
            print(comment[:300] + "..." if len(comment) > 300 else comment)

        # Look for any documentation or help text
        help_texts = re.findall(r'help[^}]*text[^}]*[\'"][^\'"]*[\'"]', content, re.IGNORECASE)
        print(f"\nHelp texts found: {len(help_texts)}")

        # Look for any references to authentication flow
        auth_flow_refs = re.findall(r'(sequence|flow|step).*?(auth|login)', content, re.IGNORECASE)
        print(f"Auth flow references: {auth_flow_refs}")

        # Look for any configuration objects that might contain auth info
        config_objects = re.findall(r'var\s+\w+\s*=\s*{[^}]*auth[^}]*}', content, re.IGNORECASE)
        print(f"\nConfig objects with auth: {len(config_objects)}")

        for i, config in enumerate(config_objects[:2]):  # First 2
            print(f"\nConfig object {i+1}:")
            print(config[:300] + "..." if len(config) > 300 else config)

    except Exception as e:
        print(f"Error checking auth comments: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_auth_comments()

