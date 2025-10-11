"""
Test program to track LLM Fundamental Strategy database writing process
This will help identify why think content is being written to database instead of proper JSON
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
from agents.fundamental_selector import FundamentalStockSelector
from config.mongodb_config import MongoDBConfig
from pymongo import MongoClient
import pandas as pd

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_llm_writing_trace.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MockDataFetcher:
    """Mock data fetcher for testing"""
    def get_stock_data(self, stock_code, days=120):
        """Return mock stock data"""
        logger.info(f"MockDataFetcher: Getting data for {stock_code}")
        # Return empty DataFrame with required columns
        return pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'open': [10.0] * 10,
            'close': [10.5] * 10,
            'high': [11.0] * 10,
            'low': [9.5] * 10,
            'volume': [1000000] * 10
        })

class MockLLMStrategy(LLMFundamentalStrategy):
    """Mock LLM strategy that simulates the actual LLM response processing"""

    def __init__(self, name="基于LLM的基本面分析策略", params=None):
        super().__init__(name, params)
        self.mock_response_used = False

    def get_llm_analysis(self, user_prompt):
        """Mock LLM analysis that properly simulates the actual response processing"""
        logger.info("MockLLMStrategy: get_llm_analysis called")
        logger.info(f"User prompt content: {user_prompt['content'][:500]}...")

        # Simulate the problematic LLM response that contains think content
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

        self.mock_response_used = True

        # Apply the same think content filtering that happens in the real LLM strategy
        import re
        content = problematic_response
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        content = re.sub(r'首先，我需要.*?\n\n', '', content, flags=re.DOTALL)
        content = re.sub(r'首先.*?\n\n', '', content, flags=re.DOTALL)

        # Check if think content was filtered
        if "<think>" in content:
            logger.error("✗ Think content still present after filtering!")
            # Return the problematic response that will cause JSON parsing to fail
            return {
                "score": 0.0,
                "value": problematic_response
            }
        else:
            logger.info("✓ Think content successfully filtered")
            # Return the proper JSON response that should be written to database
            return {
                "score": 0.643,
                "value": {
                    "score": 0.643,
                    "reason": "盈利能力尚可，但成长性不足，需关注营收下滑风险。",
                    "details": {
                        "profitability": {
                            "score": 0.75,
                            "reason": "ROE高于行业平均，但净利率有待提升"
                        },
                        "solvency": {
                            "score": 0.7,
                            "reason": "资产负债率略高于行业平均，短期偿债能力一般"
                        },
                        "efficiency": {
                            "score": 0.7,
                            "reason": "总资产周转率良好，但存货周转率偏低，信息不足"
                        },
                        "growth": {
                            "score": 0.4,
                            "reason": "营收和利润大幅下滑，成长性较差"
                        },
                        "industry_comparison": {
                            "score": 0.75,
                            "reason": "ROE优于行业平均，但负债率较高"
                        },
                        "risk": {
                            "score": 0.6,
                            "reason": "营收利润下滑，经营风险增加"
                        }
                    },
                    "weights": {
                        "profitability": 0.25,
                        "solvency": 0.15,
                        "efficiency": 0.15,
                        "growth": 0.2,
                        "industry_comparison": 0.15,
                        "risk": 0.1
                    },
                    "confidence_level": 0.8,
                    "analysis_summary": "公司盈利能力尚可，但营收和利润下滑明显，需关注经营风险。",
                    "recommendation": "观望",
                    "risk_factors": [
                        "营收下滑",
                        "利润下滑",
                        "原材料价格波动"
                    ],
                    "key_strengths": [
                        "ROE较高",
                        "资产周转率良好"
                    ]
                }
            }

class MockFundamentalSelector(FundamentalStockSelector):
    """Mock fundamental selector for testing database writing"""

    def __init__(self):
        super().__init__()
        self.written_records = []

    def update_latest_pool_record(self, stock_code, strategy_name, result):
        """Mock database writing to track what gets written"""
        logger.info(f"MockFundamentalSelector: update_latest_pool_record called")
        logger.info(f"Stock code: {stock_code}")
        logger.info(f"Strategy name: {strategy_name}")
        logger.info(f"Result: {result}")

        # Store the record for analysis
        record = {
            "stock_code": stock_code,
            "strategy_name": strategy_name,
            "result": result
        }
        self.written_records.append(record)

        logger.info(f"Mock database write completed for {stock_code}")

def test_llm_strategy_execution():
    """Test the LLM strategy execution process"""
    logger.info("=== Starting LLM Strategy Execution Test ===")

    # Create mock strategy
    strategy = MockLLMStrategy()
    strategy.data_fetcher = MockDataFetcher()

    # Create mock stock data
    stock_data = {
        "000985": pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'open': [10.0] * 10,
            'close': [10.5] * 10,
            'high': [11.0] * 10,
            'low': [9.5] * 10,
            'volume': [1000000] * 10
        })
    }

    # Execute strategy
    logger.info("Executing LLM strategy...")
    results = strategy.execute(stock_data, "test_agent", None)

    logger.info(f"Strategy execution completed. Results: {results}")

    # Check if mock response was used
    if strategy.mock_response_used:
        logger.info("✓ Mock LLM response was used")
    else:
        logger.error("✗ Mock LLM response was NOT used")

    return results

def test_database_writing():
    """Test the database writing process"""
    logger.info("=== Starting Database Writing Test ===")

    # Create mock selector
    selector = MockFundamentalSelector()

    # Create test result (simulating what comes from LLM strategy)
    test_result = {
        "code": "000985",
        "score": 0.0,  # This should be 0.643
        "value": "<think>\n用户指定的股票是：股票代码 000985...\n</think>"
    }

    # Test database writing
    logger.info("Testing database writing...")
    selector.update_latest_pool_record(
        stock_code="000985",
        strategy_name="LLM基本面分析策略",
        result=test_result
    )

    # Analyze what was written
    if selector.written_records:
        record = selector.written_records[0]
        logger.info(f"Written record analysis:")
        logger.info(f"  Stock code: {record['stock_code']}")
        logger.info(f"  Strategy name: {record['strategy_name']}")
        logger.info(f"  Result score: {record['result']['score']}")
        logger.info(f"  Result value length: {len(record['result']['value'])}")
        logger.info(f"  Result value preview: {record['result']['value'][:200]}...")

        # Check for think content
        if "<think>" in record['result']['value']:
            logger.error("✗ Think content found in database record!")
        else:
            logger.info("✓ No think content in database record")

    return selector.written_records

def analyze_llm_response_parsing():
    """Analyze the LLM response parsing logic"""
    logger.info("=== Analyzing LLM Response Parsing ===")

    # Create a real LLM strategy instance to test parsing
    strategy = LLMFundamentalStrategy()

    # Test the think content filtering
    test_response_with_think = """<think>
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

    # Test the _fix_json_string method
    logger.info("Testing _fix_json_string method...")
    fixed_response = strategy._fix_json_string(test_response_with_think)
    logger.info(f"Fixed response preview: {fixed_response[:200]}...")

    # Test think content filtering
    import re
    filtered_response = re.sub(r'<think>.*?</think>', '', test_response_with_think, flags=re.DOTALL)
    filtered_response = re.sub(r'首先，我需要.*?\n\n', '', filtered_response, flags=re.DOTALL)
    filtered_response = re.sub(r'首先.*?\n\n', '', filtered_response, flags=re.DOTALL)

    logger.info(f"Filtered response preview: {filtered_response[:200]}...")

    if "<think>" in filtered_response:
        logger.error("✗ Think content still present after filtering!")
    else:
        logger.info("✓ Think content successfully filtered")

def main():
    """Main test function"""
    logger.info("=== LLM Fundamental Strategy Database Writing Trace Test ===")

    try:
        # Test 1: LLM Strategy Execution
        strategy_results = test_llm_strategy_execution()

        # Test 2: Database Writing
        written_records = test_database_writing()

        # Test 3: LLM Response Parsing Analysis
        analyze_llm_response_parsing()

        # Summary
        logger.info("\n=== Test Summary ===")
        logger.info("✓ LLM Strategy Execution Test completed")
        logger.info("✓ Database Writing Test completed")
        logger.info("✓ LLM Response Parsing Analysis completed")

        # Identify the issue
        logger.info("\n=== Issue Analysis ===")
        logger.info("The problem appears to be in the LLM response parsing logic.")
        logger.info("The think content is not being properly filtered before database writing.")
        logger.info("The _fix_json_string method may not be handling think content correctly.")

    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()

