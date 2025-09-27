# Qian Gu Qian Ping (千股千评) Data Integration Guide

This document explains how the Qian Gu Qian Ping (千股千评) data integration works in the Enhanced Public Opinion Analysis Strategy V2.

## Overview

The Enhanced Public Opinion Analysis Strategy V2 now includes integration with Qian Gu Qian Ping data from Eastmoney. This provides additional market sentiment information for stock analysis.

## Features

### 1. Overall Market Sentiment Data
- Loads data for all stocks using `stock_comment_em()` function at strategy initialization
- Data is loaded once and cached for efficient lookup during analysis
- Provides comprehensive market overview including scores, rankings, and sentiment metrics

### 2. Detailed Guba Data
For specific stocks, the strategy collects detailed data using:
- `stock_comment_detail_scrd_focus_em()`: 用户关注指数 (User focus index)
- `stock_comment_detail_zlkp_jgcyd_em()`: 机构参与度 (Institutional participation)
- `stock_comment_detail_zhpj_lspf_em()`: 历史评分 (Historical rating)
- `stock_comment_detail_scrd_desire_daily_em()`: 日度市场参与意愿 (Daily market participation desire)

## Implementation Details

### Data Loading
The Qian Gu Qian Ping data is loaded automatically when the strategy is initialized:

```python
# In strategy constructor
self.qian_gu_qian_ping_data = None
self._load_qian_gu_qian_ping_data()
```

### Data Access
You can access the data in two ways:

1. **Overall market data lookup:**
```python
qgqp_data = strategy.get_qian_gu_qian_ping_data_for_stock("300339")
```

2. **Detailed Guba data collection:**
```python
detailed_data = strategy.get_detailed_guba_data("300339")
```

### Integration with LLM Analysis
The collected data is automatically integrated into the LLM analysis format through the `collect_all_data()` and `_format_data_for_llm()` methods.

## Testing

To verify the integration is working correctly, run:

```bash
python test/comprehensive_test_enhanced_public_opinion_strategy_v2.py
```

## Benefits

1. **Enhanced Analysis**: Additional market sentiment data improves the accuracy of public opinion analysis
2. **Efficient Data Access**: One-time loading reduces API calls and improves performance
3. **Comprehensive Coverage**: Combines overall market sentiment with detailed stock-specific data
4. **Seamless Integration**: Works automatically with existing LLM analysis workflows

## Data Fields

### Qian Gu Qian Ping Data
- 序号 (Index)
- 代码 (Stock code)
- 名称 (Stock name)
- 最新价 (Latest price)
- 涨跌幅 (Price change percentage)
- 换手率 (Turnover rate)
- 市盈率 (P/E ratio)
- 主力成本 (Main player cost)
- 机构参与度 (Institutional participation)
- 综合得分 (Composite score)
- 上升 (Ranking change)
- 目前排名 (Current ranking)
- 关注指数 (Focus index)
- 交易日 (Trading date)

### Detailed Guba Data
- 用户关注指数 (User focus index) with historical data
- 机构参与度 (Institutional participation) with historical data
- 历史评分 (Historical rating) with historical data
- 日度市场参与意愿 (Daily market participation desire) with recent data

