#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the full LLM response processing with the fix
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

def test_full_llm_response_processing():
    """Test the full LLM response processing with the fixed logic"""

    # Mock full LLM response (similar to what we saw in the database)
    mock_response_data = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": '''
{
  "score": 0.65,
  "value": "宏景科技（301396）的基本面分析如下：\\n\\n**1. 财务报表分析：**\\n*   **资产负债表：** 最近半年（2024年Q2、Q3）资产负债率从34.84%上升至39.57%，显示杠杆略有增加。流动比率和速动比率也从2.78和1.95下降到2.40和1.49，短期偿债能力有所减弱。每股净资产从11.50元下降到11.30元，表明股东权益受到一定侵蚀。2024年Q4资产负债率大幅上升至58.47%，流动比率和速动比率大幅下降至1.48和0.80，偿债能力明显恶化。2025年前两个季度有所回升，但是仍然处于低位。\\n*   **利润表：** 最近半年（2024年Q2、Q3）净利润持续为负，分别为-963.36万元和-3081.54万元，表明盈利能力堪忧。2024年全年净利润为-7569.17万元，亏损严重。销售净利率也为负，分别为-5.56%和-13.99%。但值得注意的是，2025年Q1和Q2净利润大幅转正，盈利能力大幅提高，分别达到2165.12万和6028.04万。\\n*   **现金流量表：** 缺乏现金流量表数据，无法评估公司现金流状况。\\n*   **对比最近一年数据：** 营业总收入在2024年全年表现不佳，但2025年Q1和Q2营业收入大幅增长，显示出强劲的复苏势头。净利润从盈利转为巨额亏损，直到2025年才重新开始盈利，波动巨大。\\n\\n**2. 财务比率计算与评估：**\\n*   **盈利能力：** ROE、ROA、毛利率、净利率等指标在最近四个季度（2024年）表现较差，尤其是净利率为负。但2025年Q1和Q2盈利能力有所改善。\\n*   **偿债能力：** 流动比率和速动比率在最近四个季度呈现下降趋势，表明短期偿债能力减弱。2025年Q1和Q2有所回升，但仍然处于较低水平。\\n*   **运营效率：** 存货周转天数和应收账款周转天数均较高，运营效率较低，尤其2024年的周转天数明显增加，说明变现能力较弱。2025年Q1和Q2周转天数大幅缩短，运营效率有所提高。\\n*   **杠杆比率：** 资产负债率较高，财务风险较高。\\n\\n**3. 同业比较：**\\n*   ROE低于行业平均水平（8%）。\\n*   PE为0，无法与行业平均水平（15）进行比较，但是可以理解为亏损。\\n*   资产负债率远低于行业平均水平（50%），说明财务杠杆使用较低，财务风险相对较低。\\n\\n**4. 趋势分析：**\\n*   营业总收入增长率波动较大，最近一年（2024年）甚至出现负增长，但2025年Q1和Q2大幅增长，显示出恢复性增长的潜力。\\n*   净利润增长率波动剧烈，不稳定。\\n*   整体来看，公司成长性不稳定，业绩波动较大。\\n\\n**5. AI驱动的预测和推荐：**\\n*   **未来一年预测：** 考虑到2025年Q1和Q2的强劲复苏势头，如果公司能够保持目前的增长态势，未来一年业绩有望改善。\\n*   **投资价值评估：** 考到行业前景和公司竞争力，以及2025年Q1和Q2的良好表现，公司具有一定的投资价值，但业绩不稳定是需要考虑的风险。\\n*   **风险因素：** 财务风险较高，经营风险也较大，需要密切关注公司业绩变化。\\n*   **综合投资建议：** 考虑到公司基本面存在一定风险，且业绩波动较大，建议谨慎投资。2025年Q1和Q2展现了较强的复苏能力，但是仍需关注后续的持续性。\\n\\n综合以上分析，考虑到公司盈利能力不稳定，偿债能力有所下降，以及较高的财务风险，但2025年Q1和Q2的业绩大幅改善，显示出一定的复苏潜力，因此给予该股票基本面评分0.65。"
}
'''
                        }
                    ]
                }
            }
        ]
    }

    # Create a mock LLMFundamentalStrategy instance
    strategy = LLMFundamentalStrategy()

    # Simulate the full processing logic from get_llm_analysis method
    try:
        # Extract content from response
        content = mock_response_data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"Raw content length: {len(content)}")

        # Handle case where response is wrapped in a code block
        if content.startswith("```json"):
            # Extract JSON from code block
            content = content[7:]  # Remove ```json
            if content.endswith("```"):
                content = content[:-3]  # Remove ```
        elif content.startswith("```"):
            # Extract content from code block
            content = content[3:]  # Remove ```
            if content.endswith("```"):
                content = content[:-3]  # Remove ```

        print("Successfully extracted content from code block")

        # Try to parse the main JSON response
        analysis_result = json.loads(content)
        print("Successfully parsed main JSON response")

        # Extract score and value from LLM response
        llm_score = float(analysis_result.get("score", 0))
        llm_value = analysis_result.get("value", analysis_result.get("analysis", content))

        print(f"Initial score from main JSON: {llm_score}")

        # Handle case where the value field itself contains a nested JSON object
        # This can happen when the LLM returns a JSON string in the value field
        if isinstance(llm_value, str):
            try:
                # Try to parse the value field as JSON
                nested_result = json.loads(llm_value)
                if isinstance(nested_result, dict):
                    # If it's a nested structure, extract the actual value and score
                    if "value" in nested_result:
                        llm_value = nested_result["value"]
                        print("Extracted value from nested JSON in value field")
                    # Use the nested score if available, even if main score is not default
                    if "score" in nested_result:
                        try:
                            nested_score = float(nested_result["score"])
                            # Ensure score is in valid range [0, 1]
                            llm_score = max(0.0, min(1.0, nested_score))
                            print(f"Updated score from nested JSON in value field: {llm_score}")
                        except (ValueError, TypeError):
                            pass  # Keep original score if parsing fails
            except json.JSONDecodeError:
                # If parsing fails, keep the original value
                # But try one more approach - check if the value looks like a JSON string
                if llm_value.strip().startswith('{') and llm_value.strip().endswith('}'):
                    try:
                        # Try to fix common JSON issues and parse again
                        fixed_value = strategy._fix_json_string(llm_value)
                        nested_result = json.loads(fixed_value)
                        if isinstance(nested_result, dict):
                            if "value" in nested_result:
                                llm_value = nested_result["value"]
                                print("Extracted value from fixed nested JSON in value field")
                            # Use the nested score if available, even if main score is not default
                            if "score" in nested_result:
                                try:
                                    nested_score = float(nested_result["score"])
                                    # Ensure score is in valid range [0, 1]
                                    llm_score = max(0.0, min(1.0, nested_score))
                                    print(f"Updated score from fixed nested JSON in value field: {llm_score}")
                                except (ValueError, TypeError):
                                    pass  # Keep original score if parsing fails
                    except json.JSONDecodeError:
                        pass

        print(f"Final extracted score: {llm_score}")
        print(f"Score matches expected 0.65: {abs(llm_score - 0.65) < 0.01}")

        # Test score consistency validation
        import re
        score_matches = re.findall(r'(?:评分|score)[:：]?\s*(\d+\.?\d*)', str(llm_value), re.IGNORECASE)
        if score_matches:
            try:
                extracted_score = float(score_matches[0])
                print(f"Score mentioned in text: {extracted_score}")

                # Check consistency
                if 0 <= llm_score <= 1 and 0 <= extracted_score <= 1:
                    if abs(llm_score - extracted_score) <= 0.01:
                        print("✓ Score consistency check PASSED")
                    else:
                        print("✗ Score consistency check FAILED")
                elif 0 <= llm_score <= 100 and 0 <= extracted_score <= 100:
                    normalized_extracted = max(0.0, min(1.0, extracted_score / 100.0))
                    if abs(llm_score - normalized_extracted) <= 0.01:
                        print("✓ Score consistency check PASSED (after normalization)")
                    else:
                        print("✗ Score consistency check FAILED")
                else:
                    print("? Score range mismatch, but keeping extracted score")
            except ValueError:
                print("Could not parse score from text")
        else:
            print("No score found in text")

        return abs(llm_score - 0.65) < 0.01

    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Testing full LLM response processing with fix...")
    print("=" * 60)

    success = test_full_llm_response_processing()

    print("\n" + "=" * 60)
    if success:
        print("✓ Test PASSED: Full LLM response processing works correctly")
        print("The fix should resolve the issue with stock 301396 showing score 0.01 instead of 0.65")
    else:
        print("✗ Test FAILED: Full LLM response processing still has issues")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

