"""
Test script to verify the LLM Fundamental Strategy token optimization
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

def test_prompt_length_optimization():
    """Test that the prompt length is optimized for token limits"""
    print("Testing prompt length optimization...")

    # Create strategy instance
    strategy = LLMFundamentalStrategy(name="LLM基本面分析策略")

    # Create mock data to test prompt generation
    stock_info = {
        "股票代码": "000985",
        "股票简称": "大庆华科",
        "行业": "化工",
        "上市时间": "2000-01-01"
    }

    financial_ratios = {
        "roe": 0.15,
        "roa": 0.08,
        "gross_margin": 0.25,
        "net_margin": 0.12,
        "current_ratio": 1.8,
        "quick_ratio": 1.2,
        "debt_to_equity": 0.6,
        "asset_turnover": 0.8,
        "revenue_growth": 0.1,
        "earnings_growth": 0.15
    }

    industry_info = {
        "industry": "化工",
        "industry_averages": {
            "roe": 0.08,
            "pe": 15.0,
            "debt_to_equity": 0.5
        }
    }

    financial_data = {
        "financial_indicators": {
            "每股收益": {"2023Q3": 0.45, "2023Q2": 0.38},
            "每股净资产": {"2023Q3": 5.2, "2023Q2": 5.1},
            "净资产收益率": {"2023Q3": 0.15, "2023Q2": 0.12},
            "营业收入": {"2023Q3": 1500000000, "2023Q2": 1300000000},
            "净利润": {"2023Q3": 180000000, "2023Q2": 150000000}
        },
        "balance_sheet": {
            "资产总计": {"2023Q3": 5000000000, "2023Q2": 4800000000},
            "负债合计": {"2023Q3": 3000000000, "2023Q2": 2900000000},
            "股东权益合计": {"2023Q3": 2000000000, "2023Q2": 1900000000},
            "流动资产": {"2023Q3": 1800000000, "2023Q2": 1700000000},
            "流动负债": {"2023Q3": 1000000000, "2023Q2": 950000000}
        },
        "income_statement": {
            "营业收入": {"2023Q3": 1500000000, "2023Q2": 1300000000},
            "营业成本": {"2023Q3": 1125000000, "2023Q2": 975000000},
            "净利润": {"2023Q3": 180000000, "2023Q2": 150000000},
            "营业利润": {"2023Q3": 200000000, "2023Q2": 170000000}
        },
        "cash_flow": {
            "经营活动现金流量净额": {"2023Q3": 250000000, "2023Q2": 220000000}
        }
    }

    # Generate the prompt
    prompt = strategy.create_analysis_prompt(stock_info, financial_data, financial_ratios, industry_info)

    # Analyze prompt characteristics
    prompt_length = len(prompt)
    print(f"Prompt length: {prompt_length} characters")

    # Estimate token count (rough approximation: 1 token ≈ 4 characters for Chinese)
    estimated_tokens = prompt_length // 4
    print(f"Estimated tokens: ~{estimated_tokens}")

    # Check if within reasonable limits
    max_tokens = 4096  # qwen3-4B context limit
    if estimated_tokens <= max_tokens:
        print(f"✅ Prompt is within token limit ({estimated_tokens} <= {max_tokens})")
    else:
        print(f"❌ Prompt exceeds token limit ({estimated_tokens} > {max_tokens})")

    # Show simplified data structure
    print("\nSimplified financial data structure:")
    simplified_data = strategy._simplify_financial_data(financial_data)
    print(json.dumps(simplified_data, ensure_ascii=False, indent=2))

    print("\nSimplified financial ratios:")
    simplified_ratios = strategy._simplify_financial_ratios(financial_ratios)
    print(json.dumps(simplified_ratios, ensure_ascii=False, indent=2))

    print("\nSimplified industry info:")
    simplified_industry = strategy._simplify_industry_info(industry_info)
    print(json.dumps(simplified_industry, ensure_ascii=False, indent=2))

def test_data_simplification():
    """Test that data simplification works correctly"""
    print("\nTesting data simplification...")

    strategy = LLMFundamentalStrategy(name="LLM基本面分析策略")

    # Test with empty data
    empty_data = {}
    simplified = strategy._simplify_financial_data(empty_data)
    print(f"Empty data simplification: {simplified}")

    # Test with partial data
    partial_data = {
        "financial_indicators": {
            "每股收益": {"2023Q3": 0.45}
        }
    }
    simplified = strategy._simplify_financial_data(partial_data)
    print(f"Partial data simplification: {json.dumps(simplified, ensure_ascii=False)}")

    # Test financial ratios simplification
    full_ratios = {
        "roe": 0.15, "roa": 0.08, "gross_margin": 0.25, "net_margin": 0.12,
        "current_ratio": 1.8, "quick_ratio": 1.2, "debt_to_equity": 0.6,
        "asset_turnover": 0.8, "revenue_growth": 0.1, "earnings_growth": 0.15,
        "extra_ratio": 0.5  # This should be filtered out
    }
    simplified_ratios = strategy._simplify_financial_ratios(full_ratios)
    print(f"Ratios simplification: {json.dumps(simplified_ratios, ensure_ascii=False)}")
    print(f"Extra ratio filtered out: {'extra_ratio' not in simplified_ratios}")

if __name__ == "__main__":
    print("Testing LLM Fundamental Strategy Token Optimization")
    print("=" * 60)

    test_prompt_length_optimization()
    test_data_simplification()

    print("\n🎉 Token optimization tests completed!")
    print("\nThe optimization ensures:")
    print("1. Only key financial indicators are included")
    print("2. Only recent data is used (latest period)")
    print("3. Only essential financial ratios are kept")
    print("4. Industry info is simplified to core averages")
    print("5. Prompt structure is concise and focused")

