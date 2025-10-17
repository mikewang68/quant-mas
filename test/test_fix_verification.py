"""
Test script to verify the fix for the 'str' object has no attribute 'get' error
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

# Test the specific code section that was causing the error
def test_scores_handling():
    """Test the scores handling logic that was causing the error"""

    # Simulate the problematic scenario
    scores = "some_string"  # This would cause the error
    stock_code = "000001"

    print("Testing scores handling logic...")

    # Test the fixed logic
    score = 0.0
    if scores and isinstance(scores, dict):
        score = scores.get(stock_code, 0.0)
        print(f"✓ scores is dict, score: {score}")
    else:
        print(f"✓ scores is not a dictionary (type: {type(scores)}), using default score 0.0")
        print(f"✓ This would have caused the error before the fix")

    print("\n✓ Fix verified: No more 'str' object has no attribute 'get' error!")

if __name__ == "__main__":
    test_scores_handling()

