#!/usr/bin/env python3
"""
Debug test for weekly selector to identify unpacking issues
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simple test to reproduce the unpacking issue
def test_unpacking():
    print("Testing unpacking scenarios...")

    # Simulate what might be returned from strategy.analyze()
    # Case 1: 4 values returned (meets_criteria, reason, score, golden_cross)
    result1 = (True, "Bullish arrangement", 85.5, True)
    print(f"Result1: {result1}")

    # This should work fine
    try:
        meets_criteria, reason, score, golden_cross = result1
        print(f"Unpacked result1 successfully: {meets_criteria}, {reason}, {score}, {golden_cross}")
    except Exception as e:
        print(f"Error unpacking result1: {e}")

    # Case 2: 3 values returned
    result2 = (True, "Bullish arrangement", 85.5)
    print(f"\nResult2: {result2}")

    # This should work fine
    try:
        meets_criteria, reason, score = result2
        print(f"Unpacked result2 successfully: {meets_criteria}, {reason}, {score}")
    except Exception as e:
        print(f"Error unpacking result2: {e}")

    # Case 3: Try to unpack 3 values from 4 values - this should cause the error
    try:
        meets_criteria, reason, score = result1  # This should fail
        print(f"Unpacked result1 as 3 values: {meets_criteria}, {reason}, {score}")
    except Exception as e:
        print(f"Expected error unpacking 3 values from 4: {e}")

    # Case 4: Try to unpack 4 values from 3 values - this should also cause an error
    try:
        meets_criteria, reason, score, golden_cross = result2  # This should fail
        print(f"Unpacked result2 as 4 values: {meets_criteria}, {reason}, {score}, {golden_cross}")
    except Exception as e:
        print(f"Expected error unpacking 4 values from 3: {e}")

if __name__ == "__main__":
    test_unpacking()

