#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for SignalGenerationV1Strategy output format
"""

import sys
import os
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.signal_generation_v1_strategy import SignalGenerationV1Strategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_signal_output_format():
    """Test signal output format"""
    print("Testing signal output format...")

    # Create strategy instance
    strategy = SignalGenerationV1Strategy()

    # Sample stock data for testing
    sample_stock = {
        'code': '000001',
        'tech': {
            'macd': {'score': 0.85, 'value': 'MACD金叉信号'},
            'rsi': {'score': 0.75, 'value': 'RSI处于正常范围'}
        },
        'fund': {
            'pe_ratio': {'score': 0.65, 'value': '市盈率合理'}
        },
        'pub': {
            'sentiment': {'score': 0.90, 'value': '舆情积极'}
        }
    }

    # Test stock analysis
    try:
        result = strategy._analyze_stock(sample_stock, 5)
        print(f"Analysis Result: {result}")

        # Check if result contains required fields
        required_fields = ['count', 'action', 'score_ai', 'score_calc', 'signal_calc', 'signal_ai', 'reason_ai', 'signals']
        for field in required_fields:
            if field in result:
                print(f"✓ Field '{field}' present")
            else:
                print(f"✗ Field '{field}' missing")

        # Check signals structure
        if 'signals' in result:
            signals = result['signals']
            print(f"Signals structure: {signals}")

            # Check if signals contains all required sub-fields
            required_signal_fields = ['count', 'action', 'score_calc', 'signal_calc', 'score_ai', 'signal_ai', 'reason_ai']
            for field in required_signal_fields:
                if field in signals:
                    print(f"✓ Signal field '{field}' present: {signals[field]}")
                else:
                    print(f"✗ Signal field '{field}' missing")

        return result
    except Exception as e:
        print(f"Error in stock analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Running SignalGenerationV1Strategy output format test...")

    # Test signal output format
    result = test_signal_output_format()

    print("\nTest completed.")

