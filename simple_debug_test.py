#!/usr/bin/env python3
"""
Simple debug test to identify the unpacking issue
"""

def test_execute_strategy_result():
    """Test the _execute_strategy result handling"""
    print("Testing _execute_strategy result handling...")

    # Simulate what _execute_strategy might return
    # Case 1: 4 values returned
    result1 = (True, 85.5, True, {'ma_short': 105.0, 'ma_mid': 100.0, 'ma_long': 95.0})
    print(f"Result1 (4 values): {result1}")

    # This should work fine
    try:
        meets_criteria, score, golden_cross, technical_analysis = result1
        print(f"Unpacked result1 successfully: {meets_criteria}, {score}, {golden_cross}, {technical_analysis}")
    except Exception as e:
        print(f"Error unpacking result1: {e}")

    # Case 2: 3 values returned
    result2 = (True, 85.5, True)
    print(f"\nResult2 (3 values): {result2}")

    # This should work fine
    try:
        meets_criteria, score, golden_cross = result2
        print(f"Unpacked result2 successfully: {meets_criteria}, {score}, {golden_cross}")
    except Exception as e:
        print(f"Error unpacking result2: {e}")

    # Simulate the actual code logic from weekly_selector.py
    print("\n--- Simulating weekly_selector.py logic ---")

    # Simulate result from _execute_strategy
    result = result1  # 4 values

    if result and len(result) >= 4:
        print("Taking 4-value branch")
        meets_criteria, score, golden_cross, technical_analysis = result
        print(f"4-value unpacking successful: {meets_criteria}, {score}, {golden_cross}, {technical_analysis}")
    elif result and len(result) >= 3:
        print("Taking 3-value branch")
        meets_criteria, score, golden_cross = result[0], result[1], result[2]
        print(f"3-value unpacking successful: {meets_criteria}, {score}, {golden_cross}")

if __name__ == "__main__":
    test_execute_strategy_result()

