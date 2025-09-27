# Qian Gu Qian Ping (千股千评) Data Integration

This document describes the Qian Gu Qian Ping data integration implemented in the Enhanced Public Opinion Analysis Strategy V2.

## Overview

The integration adds comprehensive market sentiment data from Eastmoney's Qian Gu Qian Ping (千股千评) service to enhance the public opinion analysis capabilities of the strategy.

## New Files Added

### Documentation
- `docs/qgqp_integration_guide.md` - Detailed guide on Qian Gu Qian Ping integration
- `docs/enhanced_public_opinion_analysis_strategy_v2.md` - Updated strategy documentation

### Examples
- `examples/qgqp_data_usage_example.py` - Example script demonstrating usage

### Tests
- `test/test_qgqp_integration_final.py` - Final comprehensive integration test
- `test/comprehensive_test_enhanced_public_opinion_strategy_v2.py` - Comprehensive strategy test

## Key Features Implemented

1. **One-time Data Loading**: Overall market sentiment data for all stocks loaded at strategy initialization using `stock_comment_em()`
2. **Efficient Data Lookup**: Quick lookup of Qian Gu Qian Ping data for specific stocks
3. **Detailed Guba Data**: Collection of specific data using:
   - `stock_comment_detail_scrd_focus_em()` for 用户关注指数
   - `stock_comment_detail_zlkp_jgcyd_em()` for 机构参与度
   - `stock_comment_detail_zhpj_lspf_em()` for 历史评分
   - `stock_comment_detail_scrd_desire_daily_em()` for 日度市场参与意愿
4. **Seamless Integration**: Data automatically included in LLM analysis workflows

## Testing

All integration features have been thoroughly tested and verified:
- Strategy initialization with data loading
- Data lookup for specific stocks
- Detailed Guba data collection
- Data integration in collection process
- Data formatting for LLM analysis

## Usage

The integration works automatically when the Enhanced Public Opinion Analysis Strategy V2 is used. No additional configuration is required.

To test the integration:
```bash
python test/test_qgqp_integration_final.py
```

To see usage examples:
```bash
python examples/qgqp_data_usage_example.py
```

