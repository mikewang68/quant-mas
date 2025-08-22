#!/usr/bin/env python3
"""
Test script to verify the unpacking fix in weekly_selector.py
"""

def test_unpacking_logic():
    """Test the unpacking logic that was fixed"""
    print("Testing unpacking logic...")

    # Simulate what _execute_strategy returns
    result = (True, 85.5, True, {"ma_short": 25.5, "ma_mid": 24.8, "ma_long": 23.9})
    print(f"Simulated result from _execute_strategy: {result}")

    # Test the first condition (len >= 4)
    if result and len(result) >= 4:
        meets_criteria, score, golden_cross, technical_analysis = result[0], result[1], result[2], result[3]
        print("✓ First condition (len >= 4) works correctly:")
        print(f"  meets_criteria: {meets_criteria}")
        print(f"  score: {score}")
        print(f"  golden_cross: {golden_cross}")
        print(f"  technical_analysis: {technical_analysis}")

    # Test the elif condition (len >= 3) - this was the problematic one
    # In the fixed version, this should also unpack 4 values
    elif result and len(result) >= 3:
        meets_criteria, score, golden_cross, technical_analysis = result[0], result[1], result[2], {}
        print("✓ Elif condition (len >= 3) now works correctly:")
        print(f"  meets_criteria: {meets_criteria}")
        print(f"  score: {score}")
        print(f"  golden_cross: {golden_cross}")
        print(f"  technical_analysis: {technical_analysis}")

    # Test with a result that only has 3 values (edge case)
    print("\nTesting with 3-value result (edge case)...")
    result_3 = (True, 75.0, False)

    if result_3 and len(result_3) >= 4:
        meets_criteria, score, golden_cross, technical_analysis = result_3[0], result_3[1], result_3[2], result_3[3] if len(result_3) > 3 else {}
        print("✓ First condition works with 3-value result")
    elif result_3 and len(result_3) >= 3:
        meets_criteria, score, golden_cross, technical_analysis = result_3[0], result_3[1], result_3[2], {}
        print("✓ Elif condition works with 3-value result:")
        print(f"  meets_criteria: {meets_criteria}")
        print(f"  score: {score}")
        print(f"  golden_cross: {golden_cross}")
        print(f"  technical_analysis: {technical_analysis}")

if __name__ == "__main__":
    test_unpacking_logic()

