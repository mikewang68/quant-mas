#!/usr/bin/env python3
"""
Test script to verify that the program field is properly handled in agent operations.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager

def test_program_field():
    """Test that the program field is properly handled in agent operations"""
    try:
        # Initialize MongoDB manager
        mongo_manager = MongoDBManager()
        
        # Create a new agent with program field
        test_agent = {
            "name": "Test Agent with Program Field",
            "description": "Test agent to verify program field handling",
            "status": "active",
            "program": "test_agent_program.py",
            "strategies": []
        }
        
        print("Creating test agent with program field...")
        agent_id = mongo_manager.create_agent(test_agent)
        if not agent_id:
            print("ERROR: Failed to create test agent")
            return False
            
        print(f"Created agent with ID: {agent_id}")
        
        # Retrieve the agent to verify program field is saved
        retrieved_agent = mongo_manager.get_agent(agent_id)
        print(f"Retrieved agent: {retrieved_agent}")
        
        if not retrieved_agent:
            print("ERROR: Failed to retrieve agent")
            return False
            
        if "program" not in retrieved_agent:
            print("ERROR: Program field not found in retrieved agent")
            return False
            
        if retrieved_agent["program"] != "test_agent_program.py":
            print(f"ERROR: Program field value mismatch. Expected 'test_agent_program.py', got '{retrieved_agent['program']}'")
            return False
            
        print("✓ Program field correctly saved and retrieved for individual agent")
        
        # Test get_agents includes program field
        agents = mongo_manager.get_agents()
        print(f"\nGet agents test - Total agents: {len(agents)}")
        
        # Find our test agent in the list
        test_agent_found = None
        for agent in agents:
            if agent["_id"] == agent_id:
                test_agent_found = agent
                break
                
        if not test_agent_found:
            print("ERROR: Test agent not found in get_agents result")
            return False
            
        if "program" not in test_agent_found:
            print("ERROR: Program field not found in test agent from get_agents result")
            return False
            
        if test_agent_found["program"] != "test_agent_program.py":
            print(f"ERROR: Program field value mismatch in get_agents result. Expected 'test_agent_program.py', got '{test_agent_found['program']}'")
            return False
            
        print("✓ Program field correctly included in get_agents result")
        
        # Test updating the agent's program field
        update_result = mongo_manager.update_agent(agent_id, {
            "program": "updated_program.py"
        })
        
        if not update_result:
            print("ERROR: Failed to update agent program field")
            return False
            
        # Retrieve updated agent
        updated_agent = mongo_manager.get_agent(agent_id)
        if updated_agent["program"] != "updated_program.py":
            print(f"ERROR: Updated program field value mismatch. Expected 'updated_program.py', got '{updated_agent['program']}'")
            return False
            
        print("✓ Program field correctly updated")
        
        # Clean up - delete test agent
        delete_result = mongo_manager.delete_agent(agent_id)
        if not delete_result:
            print("WARNING: Failed to delete test agent")
        else:
            print("✓ Test agent cleaned up successfully")
        
        print("\nAll tests passed! The program field is properly handled.")
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_program_field()
    sys.exit(0 if success else 1)

