# Qian Gu Qian Ping (千股千评) Data Integration

This document provides an overview of the Qian Gu Qian Ping data integration implemented in the Enhanced Public Opinion Analysis Strategy V2.

## Overview

The Qian Gu Qian Ping (千股千评) data integration enhances the Enhanced Public Opinion Analysis Strategy V2 by adding comprehensive market sentiment data from Eastmoney's thousand stocks thousand reviews system.

## Key Features

1. **Overall Market Sentiment Data**: One-time loading of data for all stocks using `stock_comment_em()`
2. **Detailed Guba Data**: Specific stock data collection using specialized AkShare functions
3. **Seamless Integration**: Automatic inclusion in LLM analysis workflows
4. **Efficient Access**: Cached data for fast lookup during analysis

## Implementation Files

- `strategies/enhanced_public_opinion_analysis_strategy_v2.py` - Main strategy with Qian Gu Qian Ping integration
- `docs/enhanced_public_opinion_analysis_strategy_v2.md` - Updated strategy documentation
- `docs/qgqp_integration_guide.md` - Detailed integration guide
- `examples/qgqp_data_usage_example.py` - Usage example script
- `test/test_qgqp_integration_final.py` - Final integration test

## Data Sources

### Overall Market Data
- Function: `stock_comment_em()`
- Loaded once at strategy initialization
- Provides composite scores, rankings, and sentiment metrics for all stocks

### Detailed Stock Data
- `stock_comment_detail_scrd_focus_em()`: 用户关注指数 (User focus index)
- `stock_comment_detail_zlkp_jgcyd_em()`: 机构参与度 (Institutional participation)
- `stock_comment_detail_zhpj_lspf_em()`: 历史评分 (Historical rating)
- `stock_comment_detail_scrd_desire_daily_em()`: 日度市场参与意愿 (Daily market participation desire)

## Testing

All features have been thoroughly tested and verified:

```bash
# Run the final integration test
python test/test_qgqp_integration_final.py

# Run the usage example
python examples/qgqp_data_usage_example.py
```

## Benefits

1. **Enhanced Analysis**: Additional market sentiment data improves public opinion assessment
2. **Performance**: One-time loading reduces API calls and improves efficiency
3. **Comprehensive Coverage**: Combines overall market view with detailed stock-specific data
4. **Seamless Workflow**: Integrates automatically with existing LLM analysis processes

