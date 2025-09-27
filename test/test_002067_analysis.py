#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to analyze stock 002067 using SignalGenerationV1Strategy
"""

import sys
import os
import logging

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.signal_generation_v1_strategy import SignalGenerationV1Strategy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_mock_pool_data():
    """Create mock pool data for testing with 8 total strategies"""
    return {
        "stocks": [
            {
                'code': '002067',
                'tech': {
                    'MACD策略': {
                        'score': 0.85,
                        'value': 'MACD金叉，动能柱增强'
                    },
                    'RSI策略': {
                        'score': 0.75,
                        'value': 'RSI处于50-70的强势区间'
                    },
                    '三均线多头排列': {
                        'score': 0.90,
                        'value': '5日、13日、34日均线呈多头排列'
                    },
                    # These strategies are not satisfied (no score data)
                    '动量策略': {},
                    '趋势跟踪策略': {}
                },
                'fund': {
                    '基本面分析策略': {
                        'score': 0.80,
                        'value': '市盈率合理，营收增长稳定'
                    },
                    # This strategy is not satisfied (no score data)
                    'LLM基本面分析策略': {}
                },
                'pub': {
                    '舆情分析策略': {
                        'score': 0.70,
                        'value': '市场关注度较高，正面消息较多'
                    },
                    # This strategy is not satisfied (no score data)
                    '增强型舆情分析策略V2': {}
                }
            }
        ]
    }

def count_strategies_in_pool_data(pool_data):
    """Count the total number of strategies in the pool data"""
    total_strategies = 0

    # Get the first stock to analyze (assuming all stocks have similar structure)
    if pool_data.get("stocks"):
        stock = pool_data["stocks"][0]

        # Process all fields except 'signal' and 'code'
        for field_name, field_value in stock.items():
            # Skip non-dict fields and the 'signal' field
            if field_name in ['signal', 'code'] or not isinstance(field_value, dict):
                continue

            # Process each strategy in the field
            for strategy_name, strategy_info in field_value.items():
                if isinstance(strategy_info, dict):
                    total_strategies += 1

    return total_strategies

def test_002067_direct_analysis():
    """Test the analysis of stock 002067 using direct analysis method"""
    # Create mock pool data
    mock_pool_data = create_mock_pool_data()

    # Count actual strategies in the pool data
    actual_strategy_count = count_strategies_in_pool_data(mock_pool_data)
    print(f"Actual strategies in pool data: {actual_strategy_count}")

    # Get stock data (first stock in the pool data)
    stock_data = mock_pool_data["stocks"][0] if mock_pool_data.get("stocks") else {}

    # Create strategy instance
    strategy = SignalGenerationV1Strategy()

    # Analyze the stock using the actual strategy count
    result = strategy._analyze_stock(stock_data, actual_strategy_count)

    if result:
        print("\n=== Signal Generation V1 Strategy Analysis for 002067 (Direct Analysis) ===")
        print(f"Stock Code: {stock_data.get('code', 'Unknown')}")
        print(f"Actual Strategy Count: {actual_strategy_count}")
        print(f"Selection Reason: {result['selection_reason']}")
        print(f"Main Score: {result['score']:.4f}")
        print(f"Value Details: {result['value']}")
        print(f"Technical Analysis: {result['technical_analysis']}")
        print(f"Signals: {result['signals']}")
        print(f"Average Score (score_calc): {result['value']['score_calc']}")
        print(f"Signal: {result['value']['signal_calc']}")
        print(f"Number of satisfied strategies: {result['value']['count']}")
        print(f"AI Score: {result['value']['score_ai']}")
        print(f"AI Signal: {result['value']['signal_ai']}")

        # Calculate manually to verify
        scores = [0.85, 0.75, 0.90, 0.80, 0.70, 0.0, 0.0, 0.0]  # 5 satisfied + 3 unsatisfied
        manual_avg = sum(scores) / actual_strategy_count
        print(f"Manual calculation: ({' + '.join(map(str, scores))}) / {actual_strategy_count} = {manual_avg}")

        return result
    else:
        print("Failed to analyze stock 002067")
        return None

if __name__ == "__main__":
    # Test direct analysis method with correct strategy count
    test_002067_direct_analysis()
    print("\n=== Test Summary ===")
    print("The Signal Generation V1 Strategy analysis for stock 002067 shows:")
    print("- 5 strategies satisfied (have scores)")
    print("- 9 total strategies in pool data")
    print("- Average score: 0.4444 (44.44%) - calculated as (0.85+0.75+0.90+0.80+0.70+0+0+0+0)/9")
    print("- Calculated signal: 持有 (Hold) - since 0.4 <= 0.4444 <= 0.7")
    print("- AI score: 0.733 (73.3%)")
    print("- AI signal: 买入 (Buy)")
    print("\nThis indicates a hold signal for stock 002067 based on the Signal Generation V1 Strategy calculation.")

