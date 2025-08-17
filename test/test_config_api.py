#!/usr/bin/env python3
"""
Test script for config API endpoints
"""

import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests

def test_config_api():
    """Test the config API endpoints"""
    base_url = "http://localhost:5000"  # Assuming the web app runs on default port
    
    try:
        # Test getting current config
        response = requests.get(f"{base_url}/api/config")
        print(f"GET /api/config status: {response.status_code}")
        if response.status_code == 200:
            config = response.json()
            print(f"Current config: {json.dumps(config, indent=2, ensure_ascii=False)}")
        else:
            print(f"Failed to get config: {response.text}")
            
        # Test saving config with data adjustment setting
        test_config = {
            "max_position": 0.1,
            "stop_loss": 0.05,
            "take_profit": 0.1,
            "commission": 0.001,
            "data_adjustment": "hfq"  # Post-adjusted
        }
        
        response = requests.post(f"{base_url}/api/config", 
                                json=test_config,
                                headers={'Content-Type': 'application/json'})
        print(f"POST /api/config status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Save result: {result}")
        else:
            print(f"Failed to save config: {response.text}")
            
        # Verify the setting was saved
        response = requests.get(f"{base_url}/api/config")
        if response.status_code == 200:
            config = response.json()
            print(f"Updated config: {json.dumps(config, indent=2, ensure_ascii=False)}")
            
    except Exception as e:
        print(f"Error testing config API: {e}")
        print("Make sure the web application is running on port 5000")

if __name__ == "__main__":
    test_config_api()

