#!/usr/bin/env python3
"""
Simple test script for Signal Generation V1 Strategy action logic
"""

def test_action_logic():
    """Test the action calculation logic with different scenarios"""
    print("Testing action calculation logic...")

    def calculate_action(signal_calc, signal_ai):
        """Helper function to calculate action based on the same logic as in the strategy"""
        # Determine action based on new rules:
        # - If both signal_calc and signal_ai are "买入", output "买入"
        # - If either signal_calc or signal_ai is "卖出", output "卖出"
        # - Otherwise, output "持有"
        if signal_calc == "买入" and signal_ai == "买入":
            return "买入"
        elif signal_calc == "卖出" or signal_ai == "卖出":
            return "卖出"
        else:
            return "持有"

    # Test case 1: Both signals are "买入"
    action = calculate_action("买入", "买入")
    print(f"Test 1 - Both 买入: Expected '买入', Got '{action}' - {'PASS' if action == '买入' else 'FAIL'}")

    # Test case 2: signal_calc is "卖出"
    action = calculate_action("卖出", "买入")
    print(f"Test 2 - signal_calc 卖出: Expected '卖出', Got '{action}' - {'PASS' if action == '卖出' else 'FAIL'}")

    # Test case 3: signal_ai is "卖出"
    action = calculate_action("买入", "卖出")
    print(f"Test 3 - signal_ai 卖出: Expected '卖出', Got '{action}' - {'PASS' if action == '卖出' else 'FAIL'}")

    # Test case 4: Both signals are "卖出"
    action = calculate_action("卖出", "卖出")
    print(f"Test 4 - Both 卖出: Expected '卖出', Got '{action}' - {'PASS' if action == '卖出' else 'FAIL'}")

    # Test case 5: signal_calc is "持有", signal_ai is "买入"
    action = calculate_action("持有", "买入")
    print(f"Test 5 - signal_calc 持有, signal_ai 买入: Expected '持有', Got '{action}' - {'PASS' if action == '持有' else 'FAIL'}")

    # Test case 6: signal_calc is "买入", signal_ai is "持有"
    action = calculate_action("买入", "持有")
    print(f"Test 6 - signal_calc 买入, signal_ai 持有: Expected '持有', Got '{action}' - {'PASS' if action == '持有' else 'FAIL'}")

    # Test case 7: Both signals are "持有"
    action = calculate_action("持有", "持有")
    print(f"Test 7 - Both 持有: Expected '持有', Got '{action}' - {'PASS' if action == '持有' else 'FAIL'}")

    print("Action logic tests completed.\n")


def main():
    """Main test function"""
    print("Signal Generation V1 Strategy Action Logic Test")
    print("=" * 50)

    # Test action logic
    test_action_logic()

    print("All tests completed.")


if __name__ == "__main__":
    main()

