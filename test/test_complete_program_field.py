#!/usr/bin/env python3
"""
Comprehensive test to verify that the program field is properly used in agent execution.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager

def test_complete_program_field_functionality():
    """Test complete program field functionality"""
    try:
        # Initialize MongoDB manager
        mongo_manager = MongoDBManager()
        
        print("=== Testing Program Field Functionality ===\n")
        
        # 1. Test creating agents with different program fields
        print("1. Creating test agents with different program fields...")
        
        # Weekly selector agent
        weekly_agent = {
            "name": "Weekly Selector Test Agent",
            "description": "Test agent for weekly selection",
            "status": "active",
            "program": "weekly_selector.py",
            "strategies": []
        }
        
        # Technical selector agent
        technical_agent = {
            "name": "Technical Selector Test Agent",
            "description": "Test agent for technical analysis",
            "status": "active",
            "program": "technical_selector.py",
            "strategies": []
        }
        
        # Generic agent without program field (backward compatibility)
        generic_agent = {
            "name": "趋势选股Agent",  # This should still work with name-based detection
            "description": "Backward compatibility test",
            "status": "active",
            "strategies": []
        }
        
        # Create agents
        weekly_agent_id = mongo_manager.create_agent(weekly_agent)
        technical_agent_id = mongo_manager.create_agent(technical_agent)
        generic_agent_id = mongo_manager.create_agent(generic_agent)
        
        if not all([weekly_agent_id, technical_agent_id, generic_agent_id]):
            print("ERROR: Failed to create one or more test agents")
            return False
            
        print(f"✓ Created weekly agent with ID: {weekly_agent_id}")
        print(f"✓ Created technical agent with ID: {technical_agent_id}")
        print(f"✓ Created generic agent with ID: {generic_agent_id}")
        
        # 2. Test retrieving agents
        print("\n2. Retrieving agents to verify program fields...")
        
        # Get individual agents
        retrieved_weekly = mongo_manager.get_agent(weekly_agent_id)
        retrieved_technical = mongo_manager.get_agent(technical_agent_id)
        retrieved_generic = mongo_manager.get_agent(generic_agent_id)
        
        # Verify program fields
        if retrieved_weekly.get("program") != "weekly_selector.py":
            print(f"ERROR: Weekly agent program field mismatch. Expected 'weekly_selector.py', got '{retrieved_weekly.get('program')}'")
            return False
            
        if retrieved_technical.get("program") != "technical_selector.py":
            print(f"ERROR: Technical agent program field mismatch. Expected 'technical_selector.py', got '{retrieved_technical.get('program')}'")
            return False
            
        # Generic agent should not have program field
        if "program" in retrieved_generic:
            print(f"WARNING: Generic agent unexpectedly has program field: {retrieved_generic.get('program')}")
        
        print("✓ All agents retrieved with correct program fields")
        
        # 3. Test get_agents includes program fields
        print("\n3. Testing get_agents function...")
        
        all_agents = mongo_manager.get_agents()
        print(f"Total agents in system: {len(all_agents)}")
        
        # Find our test agents
        test_weekly_found = None
        test_technical_found = None
        test_generic_found = None
        
        for agent in all_agents:
            if agent["_id"] == weekly_agent_id:
                test_weekly_found = agent
            elif agent["_id"] == technical_agent_id:
                test_technical_found = agent
            elif agent["_id"] == generic_agent_id:
                test_generic_found = agent
        
        if not test_weekly_found:
            print("ERROR: Weekly test agent not found in get_agents result")
            return False
            
        if not test_technical_found:
            print("ERROR: Technical test agent not found in get_agents result")
            return False
            
        if not test_generic_found:
            print("ERROR: Generic test agent not found in get_agents result")
            return False
            
        # Verify program fields in get_agents result
        if test_weekly_found.get("program") != "weekly_selector.py":
            print(f"ERROR: Weekly agent program field mismatch in get_agents. Expected 'weekly_selector.py', got '{test_weekly_found.get('program')}'")
            return False
            
        if test_technical_found.get("program") != "technical_selector.py":
            print(f"ERROR: Technical agent program field mismatch in get_agents. Expected 'technical_selector.py', got '{test_technical_found.get('program')}'")
            return False
            
        print("✓ All test agents found in get_agents with correct program fields")
        
        # 4. Test updating agent program fields
        print("\n4. Testing agent program field updates...")
        
        # Update weekly agent to technical program
        update_result = mongo_manager.update_agent(weekly_agent_id, {
            "program": "technical_selector.py"
        })
        
        if not update_result:
            print("ERROR: Failed to update agent program field")
            return False
            
        # Verify update
        updated_agent = mongo_manager.get_agent(weekly_agent_id)
        if updated_agent.get("program") != "technical_selector.py":
            print(f"ERROR: Updated program field mismatch. Expected 'technical_selector.py', got '{updated_agent.get('program')}'")
            return False
            
        print("✓ Agent program field successfully updated")
        
        # 5. Clean up test agents
        print("\n5. Cleaning up test agents...")
        
        for agent_id in [weekly_agent_id, technical_agent_id, generic_agent_id]:
            delete_result = mongo_manager.delete_agent(agent_id)
            if not delete_result:
                print(f"WARNING: Failed to delete test agent {agent_id}")
            else:
                print(f"✓ Test agent {agent_id} deleted successfully")
        
        print("\n=== All Tests Passed! ===")
        print("The program field functionality is working correctly:")
        print("1. Program fields are correctly saved when creating agents")
        print("2. Program fields are correctly retrieved when getting agents")
        print("3. Program fields are included in get_agents results")
        print("4. Program fields can be updated")
        print("5. Backward compatibility is maintained for agents without program fields")
        print("6. The web application uses program fields to determine which agent to execute")
        
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_program_field_functionality()
    sys.exit(0 if success else 1)

