"""
Simple test to verify think content filtering in LLM fundamental strategy
"""

import sys
import os
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test think content filtering patterns
def test_think_content_filtering():
    """Test the think content filtering regex patterns"""

    # The problematic response that contains think content
    problematic_response = """<think>
用户指定的股票是：股票代码 000985，股票名称 大庆华科，行业 化学制品。

关键财务比率：
- roe: 0.16377410714285712 → 16.38%
- roa: 0.10134088397790056 → 10.13%
- gross_margin: 0.2 → 20%
- net_margin: 0.11834 → 11.83%
- current_ratio: 1.0521947097786046 → 1.05
- quick_ratio: 0.5823844482190861 → 0.58
- debt_to_equity: 0.6171089285714285 → 61.71%
- asset_turnover: 0.8659217877094972 → 0.87
- revenue_growth: -0.2922374429223744 → -29.22%
- earnings_growth: -0.423893891473063 → -42.39%

行业对比：
- 行业：化学制品
- 行业平均水平：
  - roe: 0.08 → 8%
  - pe: 15.0
  - debt_to_equity: 0.5 → 50%

最近财务数据：
- 关键财务指标：
  - 每股净资产: "4.71"
  - 净资产收益率: "1.49%" → 注意：这里写的是1.49%，但关键财务比率中roe是16.38%，有冲突。我需要检查。用户说“净资产收益率”是"1.49%"，但前面roe是0.16377...，这可能是个错误。在量化交易中，roe通常用小数表示，但这里最近财务数据中写的是百分比。我应该以关键财务比率为准，因为它是更精确的。用户输入中，关键财务比率的roe是0.16377，但最近财务数据说“净资产收益率”是1.49%。这可能是个笔误。1.49% vs 16.38%？16.38%是163.8%，但标准roe是百分比。我需要澄清：在输入中，关键财务比率的roe是0.16377，这表示16.377%，而最近财务数据的“净资产收益率”是1.49%，这明显不一致。可能最近财务数据有误。作为AI，我必须基于提供的数据，但用户说“严禁编造未提供的数据”。所以，我应该使用关键财务比率的数值，因为它是更详细的。或者，用户可能打错了。看上下文：最近财务数据中“净资产收益率”是"1.49%"，但关键财务比率中roe是0.16377（16.38%），这很奇怪。或许在最近财务数据中，是“每股净资产”等。用户说“净资产收益率”是"1.49%"，但行业平均水平roe是8%，所以1.49%太低。我假设关键财务比率是权威的，因为它是数字列表。我将使用关键财务比率的数值进行分析。

在最近财务数据中：
- 每股净资产: "4.71" → 这是4.71元
- 净资产收益率: "1.49%" → 这可能是1.49%，但关键财务比率的roe是16.38%，所以这里有冲突。为了分析，我将优先使用关键财务比率的数值，因为它是更直接的财务比率。用户指定“关键财务比率”有具体数值，所以我会用那些。

最近财务数据中的利润表关键项目是空的，所以没有额外数据。

现在，分析六个核心维度：

1. **盈利能力（profitability）**：关注 ROE、ROA、毛利率、净利率等。
   - ROE: 16.38% (高于行业平均8%)
   - ROA: 10.13%
   - 毛利率: 20%
   - 净利率: 11.83%
   - 优点：ROE和毛利率都较高，净利率也较好。
   - 问题：最近财务数据中净资产收益率是1.49%，但关键财务比率是16.38%，这很矛盾。我必须决定。用户输入中，关键财务比率的roe是0.16377，所以是16.38%，而最近财务数据说“净资产收益率”是1.49%。可能是个错误。在量化交易中，roe通常用百分比。我将假设关键财务比率是正确的，因为它是数字。或者，用户可能误写了单位。在分析中，我会以关键财务比率为准。所以，盈利能力强。

2. **偿债能力（solvency）**：关注流动比率、速动比率、资产负债率。
   - 流动比率: 1.05
   - 速动比率: 0.58
   - 资产负债率: 61.71% (debt_to_equity = 61.71%)
   - 行业平均水平debt_to_equity: 50% → 所以资产负债率较高。
   - 流动比率1.05 >1，但速动比率0.58 <1，表示有短期偿债风险。

3. **运营效率（efficiency）**：关注总资产周转率、存货周转率。
   - 总资产周转率: 0.87 (asset_turnover)

4. **成长性（growth）**：关注营收增长率、利润增长率。
   - 营收增长率: -29.22%
   - 利润增长率: -42.39%
   - 负增长，很糟糕。

5. **行业比较（industry_comparison）**：相对行业均值的竞争力。
   - 行业均值roe: 8%
   - 该公司的roe: 16.38% > 8% → 优于行业
   - 资产负债率: 61.71% > 行业50% → 高于行业

6. **风险因素（risk）**：财务结构、盈利波动、行业周期等。
   - 负债高，速动比率低（0.58），表示短期偿债能力弱。
   - 盈利下滑：营收和利润都大幅下降（-29.22%和-42.39%）
   - 化学制品行业可能受周期影响

现在，为每个维度打分（0~1）：

- **profitability**: 由于ROE高（16.38% vs 行业8%），毛利率20%（行业可能平均？但行业对比只给roe、pe、debt_to_equity，没有毛利率），净利率11.83%。盈利能力强，但最近财务数据有冲突。我将给高分。比如0.90（理由：ROE显著高于行业，毛利率稳定）
- **solvency**: 流动比率1.05（健康），但速动比率0.58（不足），资产负债率61.71%（高于行业50%）。所以偿债能力中等偏弱。给0.65（理由：短期偿债能力不足，资产负债率偏高）
- **efficiency**: 总资产周转率0.87（行业？行业对比没给）。假设行业平均可能更高或更低，但没有数据。给中等分，比如0.70
- **growth**: 营收和利润都大幅负增长（-29%和-42%），非常差。给0.20（最低）
- **industry_comparison**: ROE 16.38% > 8%，但资产负债率61.71% > 50%。整体看，盈利能力优于行业，但财务结构不如行业。可能给0.80（理由：盈利能力强，但负债率较高）
- **risk**: 高风险：负增长、速动比率低、负债高。给0.30（理由：盈利下滑快，短期偿债压力大）

综合评分计算：
权重：
- profitability: 0.25
- solvency: 0.15
- efficiency: 0.15
- growth: 0.20
- industry_comparison: 0.15
"""

    print("=== Testing Think Content Filtering ===")
    print(f"Original response length: {len(problematic_response)}")
    print(f"Original response starts with: {problematic_response[:100]}")

    # Test the current filtering patterns
    content = problematic_response

    # Current patterns from the strategy
    think_patterns = [
        r'<think>.*?</think>',  # Standard think tags
        r'首先，我需要.*?\n\n',  # Chinese think patterns
        r'首先.*?\n\n',
        r'<think>.*?(?=\n\n|$)',  # Think content until double newline or end
        r'首先.*?(?=\n\n|$)'  # Chinese think until double newline or end
    ]

    print("\n=== Testing Current Patterns ===")
    for i, pattern in enumerate(think_patterns):
        print(f"\nPattern {i+1}: {pattern}")
        filtered = re.sub(pattern, '', content, flags=re.DOTALL)
        print(f"  After filtering: {len(filtered)} chars")
        print(f"  Starts with: {filtered[:100]}")
        if "<think>" in filtered:
            print("  ✗ Think content still present!")
        else:
            print("  ✓ Think content removed!")

    # Apply all patterns
    print("\n=== Applying All Patterns ===")
    for pattern in think_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL)

    # Also remove any remaining think-related text
    content = re.sub(r'^\s*<think>\s*', '', content)
    content = re.sub(r'\s*</think>\s*$', '', content)

    # Remove any leading/trailing whitespace
    content = content.strip()

    print(f"\nFinal filtered content length: {len(content)}")
    print(f"Final content starts with: {content[:200]}")

    if "<think>" in content:
        print("\n✗ FAILED: Think content still present after all filtering!")
        print("The regex patterns are not matching the think content properly.")
    else:
        print("\n✓ SUCCESS: Think content successfully filtered!")

    # Test alternative patterns
    print("\n=== Testing Alternative Patterns ===")
    content_alt = problematic_response

    # Alternative pattern that might work better
    alt_patterns = [
        r'<think>[\s\S]*?</think>',  # More comprehensive pattern
        r'首先，我需要[\s\S]*?\n\n',
        r'首先[\s\S]*?\n\n'
    ]

    for pattern in alt_patterns:
        content_alt = re.sub(pattern, '', content_alt, flags=re.DOTALL)

    print(f"Alternative filtered length: {len(content_alt)}")
    print(f"Alternative content starts with: {content_alt[:200]}")

    if "<think>" in content_alt:
        print("✗ Alternative patterns also failed")
    else:
        print("✓ Alternative patterns worked!")

if __name__ == "__main__":
    test_think_content_filtering()

