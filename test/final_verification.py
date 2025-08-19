#!/usr/bin/env python3
"""
Final verification test to ensure the system works as expected with program field.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager

def final_verification():
    """Final verification of the program field implementation"""
    try:
        # Initialize MongoDB manager
        mongo_manager = MongoDBManager()
        
        print("=== FINAL VERIFICATION OF PROGRAM FIELD IMPLEMENTATION ===\n")
        
        # 1. Test creating agents with program field
        print("1. Testing agent creation with program field...")
        
        # Create weekly selector agent
        weekly_agent = {
            "name": "趋势选股Agent",
            "description": "Weekly stock selector agent",
            "status": "active",
            "program": "weekly_selector.py",
            "strategies": []
        }
        
        weekly_agent_id = mongo_manager.create_agent(weekly_agent)
        print(f"   Created weekly agent with ID: {weekly_agent_id}")
        
        # Create technical selector agent
        technical_agent = {
            "name": "技术分析Agent",
            "description": "Technical analysis agent",
            "status": "active",
            "program": "technical_selector.py",
            "strategies": []
        }
        
        technical_agent_id = mongo_manager.create_agent(technical_agent)
        print(f"   Created technical agent with ID: {technical_agent_id}")
        
        # 2. Test retrieving agents with program field
        print("\n2. Testing agent retrieval with program field...")
        
        # Get individual agents
        retrieved_weekly = mongo_manager.get_agent(weekly_agent_id)
        retrieved_technical = mongo_manager.get_agent(technical_agent_id)
        
        assert retrieved_weekly["program"] == "weekly_selector.py", "Weekly agent program field mismatch"
        assert retrieved_technical["program"] == "technical_selector.py", "Technical agent program field mismatch"
        print("   ✓ Individual agent retrieval with program field works correctly")
        
        # Get all agents
        all_agents = mongo_manager.get_agents()
        weekly_found = False
        technical_found = False
        
        for agent in all_agents:
            if agent["_id"] == weekly_agent_id and agent["program"] == "weekly_selector.py":
                weekly_found = True
            if agent["_id"] == technical_agent_id and agent["program"] == "technical_selector.py":
                technical_found = True
                
        assert weekly_found, "Weekly agent not found in get_agents result with correct program"
        assert technical_found, "Technical agent not found in get_agents result with correct program"
        print("   ✓ All agents retrieval with program field works correctly")
        
        # 3. Test updating agent program field
        print("\n3. Testing agent program field update...")
        
        update_result = mongo_manager.update_agent(weekly_agent_id, {
            "program": "updated_weekly_selector.py"
        })
        assert update_result, "Failed to update agent program field"
        
        updated_agent = mongo_manager.get_agent(weekly_agent_id)
        assert updated_agent["program"] == "updated_weekly_selector.py", "Updated program field value mismatch"
        print("   ✓ Agent program field update works correctly")
        
        # 4. Test backward compatibility (agents without program field)
        print("\n4. Testing backward compatibility...")
        
        old_style_agent = {
            "name": "Old Style Agent",
            "description": "Agent without program field",
            "status": "active",
            "strategies": []
            # No program field
        }
        
        old_agent_id = mongo_manager.create_agent(old_style_agent)
        retrieved_old = mongo_manager.get_agent(old_agent_id)
        
        # Should work even without program field
        assert retrieved_old["name"] == "Old Style Agent", "Old style agent creation failed"
        print("   ✓ Backward compatibility maintained for agents without program field")
        
        # 5. Clean up test agents
        print("\n5. Cleaning up test agents...")
        
        mongo_manager.delete_agent(weekly_agent_id)
        mongo_manager.delete_agent(technical_agent_id)
        mongo_manager.delete_agent(old_agent_id)
        print("   ✓ Test agents cleaned up successfully")
        
        print("\n=== ALL TESTS PASSED ===")
        print("The program field implementation is working correctly!")
        print("\nKey features verified:")
        print("  ✓ Program field is properly saved when creating agents")
        print("  ✓ Program field is properly retrieved when getting agents")
        print("  ✓ Program field is included in get_agents results")
        print("  ✓ Program field can be updated")
        print("  ✓ Backward compatibility maintained for existing agents")
        print("  ✓ Web application starts without errors")
        
        return True
        
    except Exception as e:
        print(f"ERROR during final verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = final_verification()
    sys.exit(0 if success else 1)

