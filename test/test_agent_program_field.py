#!/usr/bin/env python3
"""
Test script to verify that the program field is properly handled in agent operations
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager

def test_agent_program_field():
    """Test that the program field is properly handled in agent operations"""
    try:
        # Initialize MongoDB manager
        mongo_manager = MongoDBManager()
        
        # Test data with program field
        test_agent = {
            "name": "Test Agent with Program",
            "description": "Test agent to verify program field handling",
            "status": "active",
            "program": "technical_selector.py",
            "strategies": []
        }
        
        # Create agent
        agent_id = mongo_manager.create_agent(test_agent)
        print(f"Created agent with ID: {agent_id}")
        
        if not agent_id:
            print("ERROR: Failed to create agent")
            return False
            
        # Retrieve agent
        retrieved_agent = mongo_manager.get_agent(agent_id)
        print(f"Retrieved agent: {retrieved_agent}")
        
        if not retrieved_agent:
            print("ERROR: Failed to retrieve agent")
            return False
            
        # Check if program field is present
        if "program" not in retrieved_agent:
            print("ERROR: Program field not found in retrieved agent")
            return False
            
        if retrieved_agent["program"] != "technical_selector.py":
            print(f"ERROR: Program field value mismatch. Expected 'technical_selector.py', got '{retrieved_agent['program']}'")
            return False
            
        # Update agent with new program
        update_result = mongo_manager.update_agent(agent_id, {
            "program": "updated_program.py"
        })
        
        if not update_result:
            print("ERROR: Failed to update agent")
            return False
            
        # Retrieve updated agent
        updated_agent = mongo_manager.get_agent(agent_id)
        print(f"Updated agent: {updated_agent}")
        
        if updated_agent["program"] != "updated_program.py":
            print(f"ERROR: Updated program field value mismatch. Expected 'updated_program.py', got '{updated_agent['program']}'")
            return False
            
        # Get all agents to verify program field is included
        all_agents = mongo_manager.get_agents()
        print(f"Total agents retrieved: {len(all_agents)}")
        
        # Find our test agent
        test_agent_found = None
        for agent in all_agents:
            if agent["_id"] == agent_id:
                test_agent_found = agent
                break
                
        if not test_agent_found:
            print("ERROR: Test agent not found in all agents list")
            return False
            
        if "program" not in test_agent_found:
            print("ERROR: Program field not found in agent from all agents list")
            return False
            
        # Clean up - delete test agent
        delete_result = mongo_manager.delete_agent(agent_id)
        if not delete_result:
            print("WARNING: Failed to delete test agent")
            
        print("SUCCESS: All tests passed! The program field is properly handled.")
        return True
        
    except Exception as e:
        print(f"ERROR: Exception occurred during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_agent_program_field()
    sys.exit(0 if success else 1)

