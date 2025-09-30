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

5. **Signal Generator Agent** (`agents/signal_generator.py`)
   - Generates trading signals by executing strategies and writing results to database
   - Analyzes existing strategy results in pool data to generate composite signals
   - Provides AI-enhanced analysis of strategy scores and values

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

### Signal Generator Agent and Strategy V1 Implementation
- **COMPLETED**: Created new Signal Generator Agent framework for analyzing existing strategy results and generating composite signals
- **IMPLEMENTED**: Signal Generation V1 Strategy that analyzes pool data to count satisfied strategies, calculate average scores, and generate buy/sell/hold signals
- **ADDED**: AI-enhanced analysis capabilities to provide additional score_ai and signal_ai outputs
- **INTEGRATED**: Signal Generation V1 Strategy with Signal Generator Agent framework
- **CONFIGURED**: Signal Generation V1 Strategy registered in database and assigned to Signal Generator Agent
- **TESTED**: Strategy execution and database integration verified with test scripts
- **DOCUMENTED**: Created comprehensive documentation for the strategy in `docs/signal_generation_v1_strategy.md`
- **ENHANCED**: Updated Signal Generation V1 Strategy to dynamically load LLM configuration from database and use external LLM services for AI analysis
- **FIXED**: Corrected output format to match required structure with proper nested signals field
- **UPDATED**: Synchronized documentation to reflect the correct output data structure
- **MODIFIED**: Updated signal action calculation logic to output only "买入" or "卖出" when both signal_calc and signal_ai agree on buy/sell, or empty string otherwise
- **FIXED**: Corrected database signal data storage to properly include signals from strategy execution

### Web Interface Enhancement for Signal Display
- **MODIFIED**: Updated stock K-line v2 HTML template to display signal generation agent content first in the right-side information table
- **CHANGED**: Renamed table header from "值" to "内容" for better clarity
- **ENHANCED**: Improved signal generation V1 data display to show detailed information including strategy counts, calculated signals, AI signals, scores, and AI analysis reasoning
- **MODIFIED**: Updated MA line styles in K-line charts with customized widths and colors (short: 1px white, medium: 2px yellow, long: 3px magenta)

### Order Account Name Enhancement
- **ADDED**: Added `account_name` field to order records to improve order tracking and display
- **MODIFIED**: Updated frontend to capture and send account name when creating orders
- **MODIFIED**: Updated backend API to store account name with order data
- **BENEFITS**: Improved performance by eliminating additional database lookups for account names in order listings

### Position Page Layout Optimization and Enhancement
- **MODIFIED**: Adjusted layout of position page to use non-equal column widths (left: 1/4, right: 3/4) for better information display
- **REMOVED**: Eliminated currency symbols (¥) from all monetary displays on the position page for cleaner presentation
- **ADDED**: Added profit/loss amount and profit/loss ratio to the left account summary panel
- **ENHANCED**: Implemented color-coded display for profit/loss information (green for profits, red for losses)
- **VERIFIED**: Confirmed that sell operations work correctly for accounts with multiple stocks, maintaining data consistency

### Dashboard Page Enhancement
- **ADDED**: Created comprehensive dashboard page with account selection functionality
- **IMPLEMENTED**: Account overview section with net asset value, returns, max drawdown, Sharpe ratio, win rate, profit/loss ratio, volatility, and VaR
- **ADDED**: Portfolio performance chart with historical equity curve visualization
- **CREATED**: Positions information section with current holdings, position ratio, and cash ratio
- **IMPLEMENTED**: Risk monitoring section with volatility, VaR, stop loss/take profit lines, and market risk alerts
- **ADDED**: Trading records section with recent trades and open trades tabs
- **ENHANCED**: Responsive design with tabbed interfaces for better user experience

### Historical Performance Chart Enhancement and Optimization
- **IMPLEMENTED**: Advanced historical performance chart with dual y-axis display
- **ADDED**: Real-time asset calculation from first stock purchase date using akshare data
- **ENHANCED**: Benchmark comparison with selectable indices (上证50, 沪深300, 中证500)
- **OPTIMIZED**: Chart styling with dark grid lines (#333), white index curve, and yellow asset curve
- **IMPROVED**: Legend colors matching curve colors for better visual consistency
- **SYNCHRONIZED**: Two curves start from the same point at account's first stock purchase for accurate performance comparison
- **ENHANCED**: Comprehensive tooltip information including:
  - Date, cash, total assets
  - Stock holdings with codes, quantities, current prices, cost prices
  - Market values, total costs, profit/loss calculations with color coding
  - Real-time profit/loss analysis with percentage calculations
- **IMPLEMENTED**: True dual y-axis system with left axis showing real index values and right axis showing assets in 万 units
- **ENHANCED**: Interactive features with zoom controls defaulting to last 1 year view
- **ADDED**: API endpoints for akshare data integration (/api/akshare/index-data, /api/akshare/stock-data)
- **OPTIMIZED**: Grid lines using dark theme for better visual clarity
- **IMPROVED**: Tooltip formatting with detailed asset breakdown and profit/loss color coding
- **ENHANCED**: Y-axis scaling optimization to avoid starting from 0, providing better visual range for data comparison
- **REFINED**: Curve synchronization logic to ensure both asset and benchmark curves start from exactly the same point for intuitive performance comparison
- **OPTIMIZED**: Y-axis label formatting to display integer values for better readability (指数轴显示整数，资产轴显示整数万元)
- **FIXED**: Dual-axis curve synchronization issue where both visible curves now use the same coordinate system (right axis) with normalized benchmark data
- **IMPLEMENTED**: Hidden reference series on left axis to maintain proper index scale display while keeping curves synchronized
- **PERFECTED**: Starting point synchronization ensuring both asset and benchmark curves begin from exactly the same point on 20200922

### TP-Link Router WAN2 Control Enhancement
- **IMPLEMENTED**: Enhanced Selenium-based automation script for TP-Link router WAN2 connection control
- **ADDED**: Flexible configuration support with both command-line arguments and JSON config files
- **ENHANCED**: Robust element location strategies with multiple fallback methods for improved reliability
- **IMPROVED**: Comprehensive error handling and logging for better debugging and monitoring
- **OPTIMIZED**: Performance with reduced wait times and efficient element interaction methods
- **ADDED**: Support for headless and non-headless modes for both automated and debugging usage
- **CREATED**: Detailed documentation and example usage scripts for easy adoption
- **VERIFIED**: Functionality with comprehensive test scripts ensuring proper operation

### TP-Link Router Right-side WAN2 Control Fix
- **FIXED**: Resolved issue where script was controlling left-side WAN1 instead of right-side WAN2
- **IMPLEMENTED**: Position-based element identification to ensure right-side WAN2 control
- **ADDED**: Enhanced button detection logic using x-coordinate positioning
- **CREATED**: Dedicated right-side WAN2 controller script with improved accuracy
- **VERIFIED**: Functionality to ensure proper control of right-side WAN2 interface

### TP-Link Router Right-side WAN2 Restart and Recording Enhancement
- **IMPLEMENTED**: Specialized script for restarting and recording right-side WAN2 operations
- **ADDED**: Position-based element identification specifically for right-side WAN2 interface
- **ENHANCED**: Improved button detection using coordinate-based positioning algorithms
- **ADDED**: Support for operation recording and logging
- **CREATED**: Comprehensive documentation and usage examples
- **VERIFIED**: Functionality to ensure accurate control of right-side WAN2 interface

### Dashboard Risk Metrics Calculation Enhancement
- **FIXED**: Resolved "calculateVolatility is not defined" JavaScript error by properly scoping functions within script tags
- **IMPLEMENTED**: Complete risk metrics calculation functionality including:
  - Volatility calculation based on historical asset data standard deviation with annualization
  - Sharpe Ratio calculation considering risk-free rate (assumed at 3%)
  - VaR (Value at Risk) calculation using historical simulation method at 95% confidence level
- **ENHANCED**: Improved robustness of calculation functions with proper edge case handling
- **ADDED**: Comprehensive debugging information to help diagnose calculation issues
- **VERIFIED**: Risk metrics now properly display on dashboard with real calculated values instead of default zeros
- **UPDATED**: Documentation to reflect the enhanced dashboard risk metrics functionality

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

# Run signal generator
python -m agents.signal_generator
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

6. **Web Interface Enhancement**
   - Improved stock display with alternating row colors for better readability
   - Added 涨跌幅 (change percentage) and 换手率 (turnover rate) columns to latest stock selection results
   - Removed ¥ symbol from current price display for cleaner presentation
   - Enhanced hover effects with color change, scaling, and shadow for improved user interaction
   - Added double-click functionality to open K-line charts for stocks
   - Implemented dynamic data loading from the pool collection with real-time stock information
   - Added moving平均 lines to stock K-line charts with parameters retrieved from strategy datasets
   - Enhanced K-line charts to specifically fetch moving average parameters from the "三均线多头排列策略（宽松型）" strategy in the database
   - Modified K-line charts to display all data by default with synchronized zooming across main chart, indicator chart, and volume chart
   - Added indicator chart between main chart and volume chart with tab switching functionality for MACD, RSI, and KDJ indicators
   - Enhanced dashboard recent trades section with proper profit/loss calculation for buy and sell transactions
   - Implemented average cost basis calculation for sell transactions with commission handling
   - Added color-coded display for profit/loss values (green for profits, red for losses)
   - Improved formatting with thousand separators and right alignment for better readability

---
*This document tracks the operations and enhancements made to the Quant MAS system. Last updated: 2025-09-30*

