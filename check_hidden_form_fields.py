#!/usr/bin/env python3

import requests
import re

def check_hidden_form_fields():
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

    print("=== Checking for hidden form fields ===")
    try:
        # Get the login page
        login_page_response = session.get(f"{base_url}/webpages/login.html", timeout=10)
        content = login_page_response.text

        # Look for all input fields, including hidden ones
        input_fields = re.findall(r'<input[^>]*>', content)
        print(f"Total input fields found: {len(input_fields)}")

        # Look for hidden input fields specifically
        hidden_fields = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*>', content)
        print(f"Hidden input fields found: {len(hidden_fields)}")

        for i, field in enumerate(hidden_fields):
            print(f"Hidden field {i+1}: {field}")

            # Extract name and value
            name_match = re.search(r'name=["\']([^"\']*)["\']', field)
            value_match = re.search(r'value=["\']([^"\']*)["\']', field)

            name = name_match.group(1) if name_match else "Unknown"
            value = value_match.group(1) if value_match else "Empty"

            print(f"  Name: {name}, Value: {value}")

        # Look for any form elements
        forms = re.findall(r'<form[^>]*>.*?</form>', content, re.DOTALL)
        print(f"\nForm elements found: {len(forms)}")

        for i, form in enumerate(forms):
            print(f"\nForm {i+1}:")
            print(form[:300] + "..." if len(form) > 300 else form)

            # Look for action attribute
            action_match = re.search(r'action=["\']([^"\']*)["\']', form)
            if action_match:
                print(f"  Action: {action_match.group(1)}")

            # Look for method attribute
            method_match = re.search(r'method=["\']([^"\']*)["\']', form)
            if method_match:
                print(f"  Method: {method_match.group(1)}")

        # Look for any JavaScript that might populate hidden fields
        js_populate = re.findall(r'document\.getElementById\([^)]*\)\.value\s*=', content)
        print(f"\nJavaScript field population found: {len(js_populate)}")

        for populate in js_populate[:5]:  # First 5
            print(f"  {populate}")

    except Exception as e:
        print(f"Error checking hidden form fields: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_hidden_form_fields()

