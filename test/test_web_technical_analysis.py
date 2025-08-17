#!/usr/bin/env python3
"""
Test script to verify technical analysis execution through web API
"""

import sys
import os
import requests
import time

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Main function to test technical analysis execution through web API"""
    print("Testing technical analysis execution through web API...")
    
    # First, let's get a list of agents to find a technical selector agent
    try:
        response = requests.get("http://localhost:5000/api/agents")
        if response.status_code == 200:
            agents = response.json()
            print(f"Found {len(agents)} agents")
            
            # Find a technical selector agent
            technical_agent = None
            for agent in agents:
                name = agent.get('name', '')
                if '技术' in name and ('选股' in name or '分析' in name):
                    technical_agent = agent
                    print(f"Found technical selector agent: {name} (ID: {agent.get('_id')})")
                    break
            
            if not technical_agent:
                print("No technical selector agent found")
                return 1
                
            # Run the technical selector agent
            agent_id = technical_agent['_id']
            print(f"\nRunning technical selector agent with ID: {agent_id}")
            
            run_response = requests.post(
                "http://localhost:5000/api/run-agent",
                json={"agent_id": agent_id}
            )
            
            if run_response.status_code == 200:
                result = run_response.json()
                print(f"Agent execution result: {result}")
                
                if result.get('status') == 'success':
                    print("Technical analysis executed successfully through web API!")
                    return 0
                else:
                    print(f"Agent execution failed: {result.get('message')}")
                    return 1
            else:
                print(f"Failed to execute agent. Status code: {run_response.status_code}")
                print(f"Response: {run_response.text}")
                return 1
        else:
            print(f"Failed to get agents. Status code: {response.status_code}")
            return 1
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to the web server. Make sure the Flask app is running.")
        print("Start the web server with: python -m web.app")
        return 1
    except Exception as e:
        print(f"Error testing web API: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

