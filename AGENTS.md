# AGENTS.md - Quant MAS System Operations Log

## System Overview

The Quant MAS (Multi-Agent System) is a quantitative trading platform with multiple specialized agents working together to analyze, select, and execute trading strategies.

## Agent Architecture

### Core Agents

1. **Technical Selector Agent** (`agents/technical_selector.py`)
   - Responsible for technical analysis and stock selection
   - Uses various technical indicators and strategies
   - Generates trading signals based on technical patterns

2. **Weekly Selector Agent** (`agents/weekly_selector.py`)
   - Performs weekly stock selection and portfolio construction
   - Integrates multiple strategy outputs
   - Manages position sizing and risk management

3. **Daily Trader Agent** (`agents/daily_trader.py`)
   - Handles daily trading operations
   - Executes trades based on selected strategies
   - Manages order execution and position monitoring

4. **Public Opinion Selector Agent** (`agents/public_opinion_selector.py`)
   - Analyzes public opinion and sentiment for stock selection
   - Uses various public opinion analysis strategies
   - Generates trading signals based on market sentiment and news analysis

### Base Agent Framework (`agents/base_agent.py`)
- Provides common functionality for all agents
- Handles configuration, logging, and error handling
- Implements standard agent lifecycle methods

## Strategy System

### Strategy Types
- **Technical Analysis Strategies**: MACD, RSI, Bollinger Bands, Moving Average crossovers
- **Trend Following**: Momentum, Breakout, Trend detection
- **Mean Reversion**: Support/Resistance, Volatility-based
- **Multi-Agent**: Combined strategy approaches
- **Fundamental Analysis**: Traditional financial ratio analysis and LLM-based analysis
- **Public Opinion Analysis**: Sentiment analysis based on news and social media data

### Key Strategy Files
- `strategies/base_strategy.py` - Base strategy interface
- `strategies/macd_strategy.py` - MACD indicator strategy
- `strategies/rsi_strategy.py` - RSI-based strategy
- `strategies/ma_crossover_strategy.py` - Moving average crossover
- `strategies/multi_agent_strategy.py` - Multi-agent coordination
- `strategies/fundamental_strategy.py` - Traditional fundamental analysis strategy
- `strategies/llm_fundamental_strategy.py` - LLM-based fundamental analysis strategy
- `strategies/enhanced_public_opinion_analysis_strategy_v2.py` - Enhanced public opinion analysis strategy with expanded data sources

## Data Management

### Database Operations (`data/` directory)
- MongoDB integration for strategy storage
- Real-time market data processing
- Historical data management

### Data Sources
- Akshare for Chinese market data
- Technical indicator calculations
- Real-time price feeds

## Configuration System

### Configuration Files
- `config/config.yaml` - Main system configuration
- `config/strategy_params.yaml` - Strategy parameters
- `config/technical_strategies.yaml` - Technical strategy settings
- `config/mongodb_config.py` - Database configuration

## Testing and Debugging

### Test Suite Structure
- Unit tests for individual strategies
- Integration tests for agent coordination
- Performance testing for backtesting
- Data quality validation

### Key Test Files
- `test/test_technical_selector.py` - Technical agent testing
- `test/test_weekly_selector.py` - Weekly selection testing
- `test/test_strategy_fields.py` - Strategy field validation
- `test/check_mongodb.py` - Database connectivity tests
- `test/test_fundamental_selector.py` - Fundamental selector testing

## Recent Operations and Enhancements

### Public Opinion Selector Framework Creation
- Created new Public Opinion Selector agent framework based on Technical Selector pattern
- Added support for dynamically loading strategies assigned to "舆情分析Agent" from database
- Implemented pool dataset integration with "pub" field for public opinion analysis results
- Created runner script for executing public opinion analysis strategies
- Updated documentation to include new agent and usage patterns
- Added example strategy and database insertion scripts to help users get started
- Created utility script to initialize and configure the 舆情分析Agent in MongoDB database with proper Chinese description

### Enhanced Public Opinion Analysis Strategy V2 Implementation
- Successfully implemented new Enhanced Public Opinion Analysis Strategy V2 with expanded data sources
- Added support for Eastmoney Guba (股吧) data collection including user focus index, institutional ratings, and participation data
- Enhanced AkShare data collection with 5-day news window and industry information
- Improved FireCrawl integration with batch processing and availability checking
- Implemented robust error handling with graceful degradation when data sources are unavailable
- Added support for multiple LLM providers (Google Gemini, DeepSeek, etc.) with dynamic API key configuration
- Created comprehensive documentation for the strategy in `docs/enhanced_public_opinion_analysis_strategy_v2.md`
- Added strategy configuration to MongoDB database with proper parameter mapping
- Verified strategy functionality with test scripts and confirmed successful execution
- Integrated strategy with existing Public Opinion Selector agent framework

### FireCrawl Integration Enhancement and Fix
- **FIXED**: Resolved FireCrawl availability detection issue where custom "SCRAPERS-JS" deployments were incorrectly identified as incompatible
- **FIXED**: Corrected FireCrawl API request format to properly work with v1 endpoints
- **ENHANCED**: Updated FireCrawl availability checking logic to actually test endpoint functionality rather than assuming based on deployment type
- **VERIFIED**: FireCrawl integration now works correctly with local deployments, properly detecting and utilizing available endpoints
- **DOCUMENTED**: Created comprehensive FireCrawl configuration guide explaining the integration and troubleshooting steps

### Technical Analysis Enhancements
- Enhanced technical indicator calculations
- Improved signal generation algorithms
- Better integration with market data sources
- **System-wide Adjustment Setting Consistency**: Technical selector now properly retrieves and uses the system adjustment setting from database configuration, ensuring consistency with other agents

### Strategy Program Field System
- Added program field extraction and management
- Enhanced strategy metadata handling
- Improved strategy versioning and tracking

### Database Optimization
- MongoDB schema improvements
- Performance optimization for large datasets
- Better error handling and recovery

### Strategy Implementation Validation
- Completed analysis of strategy-to-pool interaction patterns
- Confirmed all strategies follow consistent update patterns for pool records
- Verified no code modifications needed as implementations are correct and consistent
- Successfully executed MongoDB find operation on pool collection
- Queried for document with strategy_key "weekly_selector_three_ma"
- Retrieved sample data to validate pool document structure
- Confirmed existing strategy patterns are correct and don't require modification
- Validated consistent update pattern across all strategies
- Verified standard document structure maintenance across all strategy files

### Pool Record Sorting Fix
- **FIXED**: Resolved issue where Technical Selector and Fundamental Selector were using non-existent `selection_date` field for sorting
- Modified both selectors to use `_id` field for finding and updating the latest pool record
- Ensured consistency in pool record operations across all selector agents
- Verified that sorting now works correctly with the proper field

### Enhanced Public Opinion Analysis Strategy V2 with Qian Gu Qian Ping Data Integration
- Added support for qian gu qian ping (千股千评) data collection using `stock_comment_em()` function
- Implemented one-time loading of overall market sentiment data for all stocks at strategy initialization
- Added detailed Guba data collection for specific stocks using:
  - `stock_comment_detail_scrd_focus_em()`: 用户关注指数 (User focus index)
  - `stock_comment_detail_zlkp_jgcyd_em()`: 机构参与度 (Institutional participation)
  - `stock_comment_detail_zhpj_lspf_em()`: 历史评分 (Historical rating)
  - `stock_comment_detail_scrd_desire_daily_em()`: 日度市场参与意愿 (Daily market participation desire)
- Integrated qian gu qian ping data into LLM analysis for enhanced public opinion assessment
- Updated strategy to collect and format qian gu qian ping data for comprehensive stock evaluation
- Verified functionality with comprehensive testing including data loading, lookup, and LLM integration
- Confirmed successful implementation with final integration testing

### FireCrawl Integration Enhancement and Fix
- **FIXED**: Resolved FireCrawl availability detection issue where custom "SCRAPERS-JS" deployments were incorrectly identified as incompatible
- **FIXED**: Corrected FireCrawl API request format to properly work with v1 endpoints
- **ENHANCED**: Updated FireCrawl availability checking logic to actually test endpoint functionality rather than assuming based on deployment type
- **VERIFIED**: FireCrawl integration now works correctly with local deployments, properly detecting and utilizing available endpoints
- **DOCUMENTED**: Created comprehensive FireCrawl configuration guide explaining the integration and troubleshooting steps

### LLM Strategy Retry Mechanism Enhancement
- Enhanced LLM Fundamental Strategy with retry mechanisms for improved reliability
- Added automatic retry logic for JSON parsing failures and LLM API call failures
- Implemented exponential backoff (1s, 2s, 4s delays) to prevent overwhelming LLM services
- When all retries fail, return default score of 0.0 to ensure continuity
- Updated documentation to reflect the new retry logic and error handling

### Volume Breakout Strategy Implementation
- Successfully implemented new Volume Breakout strategy following established patterns
- Created comprehensive documentation for the strategy
- Added strategy configuration to MongoDB database
- Verified strategy functionality with test scripts
- Integrated strategy with existing Weekly Selector agent framework
- Updated main strategies documentation to include the new strategy

### Pullback Buying Strategy Implementation
- Successfully implemented new Pullback Buying Strategy (第18个策略) following documentation specifications
- Created comprehensive documentation for the strategy in both general strategies documentation and specific analysis document
- Added strategy configuration to MongoDB database with proper parameter mapping
- Enhanced StrategyResultFormatter to support Pullback Buying strategy specific data format
- Verified strategy functionality and integration with the Weekly Selector agent framework

### Pool Data Structure Fix
- Identified and fixed issue where extra fields (selection_reason, position, strategy_name, technical_analysis, uptrend_accelerating) were being written to pool data
- Updated Technical Selector agent to filter extra fields and only write standard fields (code, score, golden_cross, value, tech)
- Created cleanup script to remove existing extra fields from database
- Verified that pool data structure is now consistent and follows expected format

### Score Normalization Enhancement
- Implemented score normalization in Technical Selector agent to ensure consistency across strategies
- Added logic to normalize scores from 0-100 range to 0-1 range for strategies that output scores in different ranges
- Verified that both 0-1 range strategies (MACD, RSI) and 0-100 range strategies (三均线多头排列, 趋势跟踪, 回踩低吸, 放量突破) work correctly with the normalization
- Updated Technical Selector to properly handle scores from all strategies and maintain consistent 0-1 range output
- Confirmed that Weekly Selector already had proper score normalization implementation

### Golden Cross Output Standardization
- Modified Weekly Selector to ensure golden_cross values are output as 1 or 0 instead of True/False
- Updated the save_selected_stocks method to convert boolean values to integer format
- Ensured consistency in data storage format across the system

### HMA Turnover Strategy Fix
- Fixed critical error in HMATurnoverStrategy where code was calling non-existent `talib.hma` function
- Implemented correct HMA (Hull Moving Average) calculation using the formula: `HMA = WMA(2*WMA(n/2) - WMA(n)), sqrt(n))`
- Added proper data type conversion for TA-Lib compatibility (pandas Series to numpy arrays)
- Verified strategy functionality with test scripts and confirmed successful execution
- Strategy now properly analyzes stock data based on HMA price acceleration with turnover rate filtering

### Web Application Enhancement for Fundamental Analysis Agents
- Added proper handling for fundamental analysis agents in the web application
- Fundamental analysis agents (with "基本面分析" in their name) are now properly executed instead of being simulated
- Added specific code path to initialize and run FundamentalStockSelector when fundamental analysis agents are triggered
- Ensured consistent execution pattern across all agent types (technical, fundamental, weekly selector)

### Technical Selector Score Field Fix
- **FIXED**: Resolved issue where Technical Selector was not properly writing strategy score values to pool data
- Modified `update_latest_pool_record` method to include `score` field from strategy results
- Technical Selector now correctly writes actual strategy scores (e.g., 0.85) instead of default 0 values
- Ensures accurate score representation in `tech.策略名称.score` fields

### Fundamental Selector Implementation
- **COMPLETED**: Created runner script for the Fundamental Stock Selector agent
- Implemented `utils/run_fundamental_selector.py` to execute fundamental analysis strategies
- Added test script `test/test_fundamental_selector.py` to verify proper initialization and execution
- Created verification script `test/verify_fundamental_scores.py` to check pool data integrity
- Updated documentation to include fundamental selector in usage patterns
- Fundamental selector properly loads strategies from database and executes LLM-based fundamental analysis
- Results are correctly written to the pool collection with fund field containing strategy scores and analysis
- **OPTIMIZED**: Added logic to skip stock analysis when valid scores already exist in pool data, reducing unnecessary LLM calls during network issues

### Enhanced Public Opinion Analysis Strategy V2 Value Field Enhancement
- **ENHANCED**: Modified Enhanced Public Opinion Analysis Strategy V2 to provide detailed information in the value field instead of simple counts
- Updated `_create_detailed_value` method to include specific data in LLM analysis details, data source details, and Eastmoney Guba detailed data
- LLM analysis details now include comprehensive analysis summary that supports key events and risk factors
- Data source details now show specific information rather than just item counts for all 6 data sources (AkShare news, industry info, qian gu qian ping, Guba data, professional sites, FireCrawl data)
- Eastmoney Guba detailed data now shows specific numerical values rather than just record counts for all 4 categories (user focus index, institutional participation, historical rating, daily market participation desire)
- Created and ran test scripts to verify the enhanced value field output contains specific data as required
- Updated documentation to reflect the enhanced value field content structure

## Usage Patterns

### Running Agents
```bash
# Run technical selector
python -m agents.technical_selector

# Run weekly selector
python -m agents.weekly_selector

# Run daily trader
python -m agents.daily_trader

# Run public opinion selector
python -m utils.run_public_opinion_selector

# Run fundamental selector
python -m utils.run_fundamental_selector
```

### Testing Strategies
```bash
# Run specific strategy tests
python -m test.test_macd_strategy

# Run comprehensive testing
python -m test.test_system
```

### Backtesting
```bash
# Run backtesting framework
python -m backtesting.backtester
```

## Monitoring and Logging

### Log Files
- `logs/quant_system.log` - Main system log
- `logs/app.log` - Application-level logging
- `logs/web.log` - Web interface logging

### Debugging Tools
- Real-time strategy output monitoring
- Performance metrics collection
- Error tracking and reporting

## Future Development Directions

1. **Machine Learning Integration**
   - Predictive modeling enhancements
   - Pattern recognition improvements
   - Adaptive strategy optimization

2. **Risk Management**
   - Enhanced position sizing algorithms
   - Dynamic risk adjustment
   - Portfolio optimization

3. **Real-time Execution**
   - Low-latency trading integration
   - Order management system
   - Execution quality monitoring

4. **Multi-market Support**
   - Additional market data sources
   - Cross-market arbitrage
   - Global portfolio management

5. **Fundamental Analysis Enhancement**
   - Advanced LLM-based financial analysis
   - Multi-source data integration for fundamental metrics
   - Dynamic industry comparison benchmarks
   - Enhanced financial ratio calculation and analysis

---
*This document tracks the operations and enhancements made to the Quant MAS system. Last updated: 2025-09-07*

