#!/usr/bin/env python3
"""
Debug script to check the exact LLM response format
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
import json

def test_exact_llm_response():
    """Test with the exact LLM response format"""

    # Create a strategy instance
    strategy = LLMFundamentalStrategy(name="Test LLM Strategy", params={})

    # This is the exact response we saw in the debug output
    exact_response = '''{
    "score": 0.65,
    "value": "农产品（000061）的基本面分析如下：\n\n**1. 财务报表分析：**\n\n*   **资产负债表：** 最近半年（2024年3月至2024年9月）的数据显示，资产负债率维持在60%左右，较为稳定。流动比率和速动比率均低于1，表明短期偿债压力较大，需关注其流动性风险。保守速动比率也在0.3左右波动，表明公司可能需要依赖存货变现来偿还短期债务。\n*   **利润表：** 营业总收入在2024年二季度和三季度分别约为24亿和37亿，呈现增长趋势。净利润也从2.14亿增长至3.13亿，盈利能力有所增强。但销售净利率从13.15%下降至12.15%，表明成本控制或市场竞争压力可能对其盈利能力构成挑战。\n*   **现金流量表：** 缺乏最新的现金流量表数据，无法评估公司的现金流状况。\n\n**2. 财务比率计算与评估：**\n\n*   **盈利能力：** 最近四个季度（2023年12月、2024年3月、2024年6月、2024年9月）的净资产收益率（ROE）分别为7.58%、1.34%、3.42%、5.05%，波动较大，整体盈利能力较弱。销售毛利率从28.21%上升至31%再下降至26.68%，呈波动趋势，成本控制面临挑战。\n*   **偿债能力：** 流动比率和速动比率长期低于1，短期偿债压力较大。保守速动比率也较低，进一步验证了这一结论。\n*   **运营效率：** 存货周转率有所波动，应收账款周转天数也相对稳定，运营效率有待提升。\n*   **杠杆比率：** 资产负债率维持在较高水平（60%左右），财务风险较高。产权比率也较高，表明公司依赖债务融资。\n\n**3. 同业比较：**\n\n*   **行业平均水平：** 行业平均ROE为8%，农产品的ROE低于行业平均水平。行业平均PE为15，由于农产品PE为0，无法直接比较，但可能暗示盈利能力不足。行业平均资产负债率为0.5，农产品的资产负债率远高于行业平均水平。\n*   **行业地位：** 考虑到ROE低于行业平均，资产负债率远高于行业平均，公司在行业中的地位并不突出。\n\n**4. 趋势分析：**\n\n*   **历史趋势：** 营收增长率和利润增长率波动较大，表明公司业务发展不稳定。净资产收益率也波动较大，盈利能力不稳定。\n*   **成长性：** 虽然最近四个季度营收有所增长，但盈利能力指标下降，成长性面临挑战。\n\n**5. AI驱动的预测和推荐：**\n\n*   **未来预测：** 基于最近半年的财务状况，如果公司能够有效控制成本，提高盈利能力，降低财务杠杆，未来一年仍有发展潜力。\n*   **投资价值：** 考虑到公司盈利能力较弱，财务风险较高，投资价值有限。\n*   **风险因素：** 财务风险（高杠杆）和经营风险（盈利能力不稳定）是主要风险因素。\n*   **综合建议：** 考虑到上述风险因素，建议谨慎投资。农产品需要着重改善盈利能力，降低财务杠杆，才能提升投资价值。\n\n综合考虑以上因素，我给出的基本面评分是0.65。这个评分反映了公司在营收增长方面取得的进展，但同时也突出了公司在盈利能力、偿债能力和财务风险控制方面的不足。"
}'''

    print("Exact LLM response:")
    print(exact_response)
    print("\n" + "="*50)

    # Try to parse it directly
    try:
        parsed = json.loads(exact_response)
        print("Successfully parsed as JSON")
        print(f"Score: {parsed.get('score')}")
        print(f"Value type: {type(parsed.get('value'))}")
        print(f"Value length: {len(parsed.get('value', ''))}")
        print(f"Value (first 100 chars): {parsed.get('value', '')[:100]}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse as JSON: {e}")

    # Test the get_llm_analysis method
    print("\n" + "="*50)
    print("Testing get_llm_analysis method:")
    try:
        result = strategy.get_llm_analysis(exact_response)
        print(f"Result score: {result.get('score')}")
        print(f"Result value type: {type(result.get('value'))}")
        print(f"Result value length: {len(str(result.get('value', '')))}")
        value_str = str(result.get('value', ''))[:200]
        print(f"Result value (first 200 chars): {value_str}")

        # Check if the result value contains the score
        if "0.65" in str(result.get('value', '')):
            print("*** ISSUE: Score found in value field ***")
    except Exception as e:
        print(f"Error in get_llm_analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_exact_llm_response()

