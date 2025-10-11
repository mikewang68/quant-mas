#!/usr/bin/env python3
"""
Test program for LLM Fundamental Strategy - Output LLM JSON Response
专门测试LLM基本面分析策略，输出大模型返回的JSON字符串
"""

import os
import sys
import json
import logging

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

# Configure logging to see detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_llm_json_response():
    """
    Test function to capture and display LLM JSON response
    """
    print("=" * 80)
    print("LLM基本面分析策略 - JSON响应输出测试")
    print("=" * 80)

    # Check for required environment variables
    required_env_vars = ["GEMINI_API_KEY", "DEEPSEEK_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"警告: 以下环境变量未设置: {', '.join(missing_vars)}")
        print("请设置环境变量:")
        for var in missing_vars:
            print(f"  export {var}='your_api_key_here'")
        print("\n注意: 如果没有API密钥，测试将无法调用LLM服务")
    else:
        print("✓ 所有必需的环境变量已设置")

    print("\n" + "-" * 80)

    # Create LLM Fundamental Strategy instance
    strategy_params = {
        "llm_config_name": "deepseek",  # 使用DeepSeek配置
        "strategy_name": "基于LLM的基本面分析策略"
    }

    try:
        strategy = LLMFundamentalStrategy(
            name="LLM基本面分析策略测试", params=strategy_params
        )
        print("✓ LLM基本面分析策略初始化成功")

        # Display LLM configuration
        print(f"\nLLM配置信息:")
        print(f"  API URL: {strategy.llm_config.get('api_url', 'N/A')}")
        print(f"  模型: {strategy.llm_config.get('model', 'N/A')}")
        print(f"  提供商: {strategy.llm_config.get('provider', 'N/A')}")
        print(f"  超时时间: {strategy.llm_config.get('timeout', 'N/A')}秒")

    except Exception as e:
        print(f"✗ 策略初始化失败: {e}")
        return

    print("\n" + "-" * 80)

    # Test stock codes
    test_stocks = ["300339", "000001", "600036"]  # 润和软件, 平安银行, 招商银行

    for stock_code in test_stocks:
        print(f"\n正在分析股票 {stock_code}...")
        print("-" * 50)

        try:
            # Perform fundamental analysis
            result = strategy.analyze_stock_fundamentals(stock_code)

            print(f"\n✓ 股票 {stock_code} 分析完成")

            # Display analysis results
            print(f"\n分析结果:")
            print(f"  评分 (score): {result.get('score', 'N/A')}")

            # Handle value field - it might be a string or JSON
            value = result.get('value', 'N/A')
            if isinstance(value, str):
                # Try to parse as JSON
                try:
                    parsed_value = json.loads(value)
                    print(f"  值 (value): JSON格式")
                    print(json.dumps(parsed_value, indent=2, ensure_ascii=False))
                except json.JSONDecodeError:
                    # If not JSON, display as string
                    print(f"  值 (value): 字符串格式")
                    print(f"  {value}")
            else:
                print(f"  值 (value): {value}")

            # Display the full raw result
            print(f"\n完整原始结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

        except Exception as e:
            print(f"✗ 股票 {stock_code} 分析失败: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 50)


def test_llm_prompt_format():
    """
    Test function to examine the prompt format sent to LLM
    """
    print("\n" + "=" * 80)
    print("LLM提示词格式测试")
    print("=" * 80)

    strategy = LLMFundamentalStrategy(
        name="LLM提示词测试", params={"llm_config_name": "deepseek"}
    )

    # Test stock code
    stock_code = "300339"

    try:
        # Get stock information to create prompt
        stock_info = strategy.get_stock_info(stock_code)
        financial_data = strategy.get_financial_data(stock_code)
        financial_ratios = strategy.calculate_financial_ratios(financial_data)
        industry_info = strategy.get_industry_info(stock_code)

        # Create analysis prompt
        user_prompt = strategy.create_analysis_prompt(
            stock_info, financial_data, financial_ratios, industry_info
        )

        print(f"\n股票 {stock_code} 的提示词内容:")
        print("-" * 50)
        print(user_prompt.get('content', 'N/A'))

        # Also show system prompt
        system_prompt = strategy._load_system_prompt()
        print(f"\n系统提示词:")
        print("-" * 50)
        print(system_prompt.get('content', 'N/A')[:500] + "..." if len(system_prompt.get('content', '')) > 500 else system_prompt.get('content', 'N/A'))

    except Exception as e:
        print(f"✗ 提示词测试失败: {e}")


def main():
    """
    Main function to run all tests
    """
    print("开始LLM基本面分析策略测试...")

    # Test 1: LLM JSON Response
    test_llm_json_response()

    # Test 2: Prompt Format
    test_llm_prompt_format()

    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()

