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

### Enhanced Public Opinion Analysis Strategy V2 Output Format Optimization and Bug Fixes
- **COMPLETED**: Successfully fixed multiple issues with EastMoney Guba data crawling functionality
- **OUTPUT FORMAT OPTIMIZATION**: Modified output format to use concise "时间：内容" format instead of verbose "标题:" and "发布时间:" prefixes
- **AKSHARE NEWS FORMAT**: Updated AkShare news output to use "时间：内容" format, removing "日期:" and "摘要:" prefixes
- **TIME-BASED SORTING**: Implemented reverse chronological sorting to display latest data first
- **FUNCTION DEFINITION FIXES**: Resolved multiple function definition issues including:
  - Added missing `_format_posts` static method
  - Added missing `_parse_time` static method for time-based sorting
  - Fixed function definition order issues between `scrape_guba_data` and `scrape_all_guba_data`
- **LOGGING ENHANCEMENT**: Added comprehensive logging functionality to output results to console
- **VERIFICATION**: Created and ran comprehensive test scripts to verify all functionality works correctly
- **FORMAL PROGRAM INTEGRATION**: Confirmed that formal running program (`utils.run_public_opinion_selector`) now uses the fixed code

### Finance Data Update Enhancement with Duplicate Key Handling
- **COMPLETED**: Enhanced `update_finance_data` function in down2mongo.py with robust duplicate key handling
- **DUPLICATE DETECTION**: Identified that AkShare profit forecast data contains 180 duplicate stock codes (3,005 total records, 2,825 unique codes)
- **DATA DEDUPLICATION**: Implemented automatic deduplication logic using `drop_duplicates(subset=['代码'], keep='first')`
- **PRIORITIZATION**: Added sorting by '序号' in descending order to keep the latest records for each stock
- **VERIFICATION**: Successfully tested and confirmed that function now correctly handles duplicate keys and writes 2,825 unique records
- **DATABASE INTEGRITY**: Ensured each stock code is written only once to maintain database integrity

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

### Weekly Selector Multi-Strategy Fix
- **FIXED**: Resolved issue where Weekly Selector was only writing the last strategy's data to pool dataset when running multiple strategies
- **ENHANCED**: Modified `save_selected_stocks` method to collect all strategy data first, then write to pool in a single operation
- **IMPROVED**: Strategy IDs and names are now properly stored as arrays containing all strategies
- **OPTIMIZED**: Stock data is merged using `stocks_by_code` dictionary to avoid duplicates and properly handle stocks selected by multiple strategies
- **VERIFIED**: Tested with 4 strategies - successfully saved 291 stocks with 8 stocks selected by multiple strategies, each containing trend data from all relevant strategies

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

### Selection Reason Field Fix
- **FIXED**: Resolved issue where `selection_reason` field was not being written to database pool dataset
- **ROOT CAUSE**: Weekly Selector was calling `analyze` method but not properly passing `selection_reason` field through the result pipeline
- **FIXES IMPLEMENTED**:
  - Added `selection_reasons` dictionary in `_execute_strategy` method to store selection reasons for each stock
  - Updated `strategy_results` structure from `(selected_stocks, last_data_date, selected_scores, technical_analysis_data)` to `(selected_stocks, selection_reasons, selected_scores, technical_analysis_data)`
  - Fixed `save_selected_stocks` method to correctly extract `selection_reason` from `selection_reasons` dictionary
  - Fixed indentation error in Weekly Selector that was causing syntax errors
- **VERIFIED**: Created test script to confirm `selection_reason` field is now properly returned by strategies and passed through the Weekly Selector pipeline

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

### LLM Fundamental Strategy Financial Ratio Calculation Enhancement
- **COMPREHENSIVE FIX**: Fixed multiple issues in LLM Fundamental Strategy financial ratio calculations
- **FIELD NAME CORRECTION**: Corrected field name mismatches between calculation methods and actual database fields
- **GROWTH RATE CALCULATION**: Fixed revenue and earnings growth calculations to use performance report YoY data instead of missing historical data
- **LIQUIDITY RATIOS**: Fixed current ratio and quick ratio calculations using available balance sheet fields (cash + receivables + inventory / payables + advance receipts)
- **ADDITIONAL METRICS**: Added 8 new important financial metrics:
  - Operating Margin (营业利润率)
  - Cash Ratio (现金比率)
  - Cash Flow Ratio (现金流量比率)
  - Interest Coverage (利息保障倍数)
  - Receivables Turnover (应收账款周转率)
  - Inventory Turnover (存货周转率)
  - EPS (每股收益)
  - Book Value per Share (每股净资产)
- **CHINESE DISPLAY**: All financial ratios now display in Chinese for better readability
- **DATA SOURCE VERIFICATION**: Confirmed all calculations use correct fields from fin_yjbb, fin_zcfz, fin_lrb, and fin_xjll datasets
- **COMPLETE COVERAGE**: Now provides 18 core financial ratios covering profitability, liquidity, leverage, efficiency, growth, and per-share metrics

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
- **FIXED**: Resolved strategy data collection issue where LLM was receiving empty data - now properly collects data from all pool fields (trend, tech, fund, pub)
- **ENHANCED**: Improved global strategy count calculation to count actual strategies from pool data instead of database configuration
- **FIXED**: Corrected LLM prompt loading to use system prompt from `config/signal_sys_prompt.md` file instead of hardcoded prompts
- **ENHANCED**: User prompt now uses JSON string format with all strategy data combined for LLM analysis

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

### Data Source Migration to k_data Collection
- **COMPLETED**: Migrated all agent data sources to use k_data collection with forward-adjusted (前复权) data
- **TECHNICAL SELECTOR**: Modified to use k_data collection with proper field mapping ("q" suffix fields: 开盘q, 收盘q, etc.)
- **FUNDAMENTAL SELECTOR**: Updated to use k_data collection with 120 days of daily data for fundamental analysis
- **PUBLIC OPINION SELECTOR**: Optimized to return empty DataFrame as it doesn't require K-line data
- **SIGNAL GENERATOR**: Optimized to return empty DataFrame as it doesn't require K-line data
- **FIELD MAPPING**: Implemented proper mapping from k_data fields to standard format:
  - "开盘q" → "open", "收盘q" → "close", "成交量q" → "volume", etc.
- **DATA VALIDATION**: Enhanced data validation using StandardDataFormat interface
- **COMPATIBILITY**: Ensured backward compatibility with existing strategy implementations
- **VERIFIED**: All modifications tested and confirmed working correctly

### Industry Data Update Enhancement
- **IMPLEMENTED**: Added `update_industry` function to down2mongo.py for updating industry, PE, and PB information
- **CONDITIONAL EXECUTION**: Modified main function to execute industry updates only on the first trading day of each month
- **DATA SOURCES**: Uses AkShare to get industry boards and constituent stock information
- **FIELDS UPDATED**: Industry, PE (市盈率-动态), PB (市净率) fields in code dataset
- **VERIFIED**: Successfully tested and confirmed 5437 stocks updated with industry data
- **AUTOMATION**: Monthly execution ensures industry data stays current without unnecessary daily updates

### Web Interface Enhancement for Stock Display and K-line Charts
- **MODIFIED**: Updated stock list page to fetch latest price, change percentage, and turnover rate from k_data collection instead of akshare real-time data
- **ENHANCED**: Stock K-line v2 chart to fetch real-time data from Akshare with last 1 year of daily data
- **IMPROVED**: K-line chart default display to show last 120 days of data with zoom functionality for full dataset viewing
- **CONFIRMED**: All data fetched from Akshare uses forward-adjusted (前复权) pricing for consistency
- **OPTIMIZED**: Chart rendering to display all available data instead of paginated subsets
- **VERIFIED**: DataZoom functionality working properly for interactive chart exploration
- **ENHANCED**: Added synchronized y-axis crosshair functionality across all three charts (K-line, indicator, volume) - when hovering over any chart, the y-axis position is displayed on all three charts simultaneously

### K-line Chart Enhancement with Akshare Integration
- **IMPLEMENTED**: Modified stock_kline_v2.html to fetch real-time K-line data from Akshare instead of database
- **ADDED**: New API endpoint `/api/stock-kline-realtime/<code>` to serve Akshare data with 1-year historical range
- **CONFIGURED**: Default display to show last 120 days of data with zoom functionality for full dataset exploration
- **VERIFIED**: All data fetched from Akshare uses explicit forward-adjusted (前复权) pricing for consistency
- **OPTIMIZED**: Chart rendering to display all available data instead of paginated subsets
- **ENHANCED**: DataZoom functionality with proper default range configuration for better user experience
- **OPTIMIZED**: Chart rendering to display all available data instead of paginated subsets
- **VERIFIED**: DataZoom functionality working properly for interactive chart exploration

### Stock K-line Chart V2 Enhancement and Tooltips Optimization
- **ENHANCED**: Modified stock K-line v2 chart with comprehensive navigation and display improvements
- **ADDED**: Three-group navigation tabs in single row layout:
  - Period selection: 日线 | 周线
  - Main overlay: 无叠加 | MA | BOLL
  - Technical indicators: MACD | RSI | KDJ | OBV | ROC
- **IMPLEMENTED**: Weekly data conversion functionality using daily data to generate weekly K-line data
- **OPTIMIZED**: Default display to show 90 days of data instead of 120 days for better focus on recent trends
- **ENHANCED**: Tooltips display with comprehensive formatting:
  - K-line data displayed in vertical stacked format with detailed price information
  - Volume data divided by 10000 and displayed as integer with "W" suffix (e.g., "12W")
  - All other numerical values formatted to 2 decimal places
  - Left-aligned layout for better readability
- **FIXED**: Missing function definitions for `convertDailyToWeekly` and `switchMainOverlay`
- **VERIFIED**: All navigation and display features working correctly

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

### Enhanced Public Opinion Analysis Strategy V2 Output Format Fix
- **FIXED**: Resolved issue where Enhanced Public Opinion Analysis Strategy V2 was returning string format instead of JSON format in value field
- **MODIFIED**: Updated `_create_detailed_value` method to return proper JSON structure with all required fields
- **ENHANCED**: Now returns complete JSON format including score, reason, details, weights, sentiment_score, sentiment_trend, key_events, market_impact, confidence_level, analysis_summary, recommendation, risk_factors, and data_sources
- **VERIFIED**: Strategy now correctly outputs JSON format that matches system prompt requirements

### Web Interface JSON Display Enhancement
- **ENHANCED**: Modified stock_kline_v2.html to format JSON strings in the right-side analysis information table
- **ADDED**: JSON detection and formatting logic in `formatValueForTable` function
- **IMPROVED**: JSON strings are now displayed with proper indentation and formatting using monospace font
- **BENEFITS**: Enhanced readability of public opinion analysis results and other JSON-formatted strategy outputs

### Public Opinion Selector Agent Pool Data Update Enhancement
- **MODIFIED**: Updated `update_latest_pool_record` method in Public Opinion Selector agent to correctly handle JSON string values from Enhanced Public Opinion Analysis Strategy V2
- **ENHANCED**: Now properly extracts score value from the first "score" field in the JSON string returned by strategy execution
- **VERIFIED**: Value field now contains the complete JSON string from strategy execution, and score field contains the extracted numerical score value
- **CONFIRMED**: Implementation follows the exact requirements specified in the task

### Public Opinion Selector Agent Pool Data Update Enhancement (Refined)
- **MODIFIED**: Further refined `update_latest_pool_record` method in Public Opinion Selector agent to ensure value field contains the JSON string returned by strategy execution and score field contains the first score value from the JSON string
- **CONFIRMED**: Implementation correctly handles the data format requirements for enhanced public opinion analysis strategies

### Public Opinion Selector Agent Pool Data Update Enhancement (Finalized)
- **FINALIZED**: Completed implementation of `update_latest_pool_record` method in Public Opinion Selector agent to ensure value field contains the JSON string returned by strategy execution and score field contains the first score value from the JSON string
- **VERIFIED**: Implementation correctly handles the data format requirements for enhanced public opinion analysis strategies with proper error handling and fallback mechanisms

### Public Opinion Selector Agent Pool Data Update Enhancement (Completed)
- **COMPLETED**: Final verification and testing of `update_latest_pool_record` method in Public Opinion Selector agent to ensure it correctly implements the required functionality
- **CONFIRMED**: The value field now contains the JSON string returned by strategy execution, and the score field contains the first score value extracted from the JSON string
- **VERIFIED**: Implementation properly handles edge cases and error conditions with appropriate fallback mechanisms

### Enhanced Public Opinion Analysis Strategy V2 JSON Output Verification
- **VERIFIED**: Successfully tested and verified the JSON output format of Enhanced Public Opinion Analysis Strategy V2
- **CONFIRMED**: Strategy returns complete JSON structure with all required fields including score, reason, details, weights, sentiment_score, sentiment_trend, key_events, market_impact, confidence_level, analysis_summary, recommendation, and risk_factors
- **DEMONSTRATED**: Created test programs to showcase the actual JSON output format from strategy execution
- **CONFIRMED**: The value field in pool data contains the full JSON string, while the score field contains the numerical score value extracted from the JSON

### Enhanced Public Opinion Analysis Strategy V2 - All Stocks Output Modification
- **MODIFIED**: Updated Enhanced Public Opinion Analysis Strategy V2 to output analysis results for all stocks, regardless of whether they meet the threshold criteria
- **CONFIRMED**: Strategy now returns analysis data for all stocks processed, ensuring comprehensive coverage in the pub field
- **VERIFIED**: Implementation properly handles both qualifying and non-qualifying stocks with appropriate reason messages

### LLM Fundamental Strategy Enhancement
- **ENHANCED**: Improved LLM Fundamental Strategy with better JSON format handling and API compatibility
- **ADDED**: Support for multiple LLM providers (Google Gemini, DeepSeek, Qwen, OpenAI, Ollama) with proper payload formatting
- **ENHANCED**: Added system prompt loading from config file with fallback mechanism
- **OPTIMIZED**: Simplified financial data structure to reduce token usage
- **IMPROVED**: Enhanced financial ratio calculations with better field mapping
- **ADDED**: Fallback analysis mechanism when LLM fails to return proper JSON
- **FIXED**: API payload format issues for different LLM providers
- **VERIFIED**: Strategy now works correctly with qwen3-4B and other OpenAI-compatible models

### Fundamental Selector Score Extraction Enhancement
- **ENHANCED**: Improved score extraction logic in Fundamental Selector to handle JSON string values from strategy execution
- **ADDED**: Support for extracting scores from JSON strings returned by LLM strategies
- **OPTIMIZED**: Score normalization logic to handle both 0-1 and 0-100 score ranges
- **IMPROVED**: Data preservation by keeping original JSON strings in value field
- **VERIFIED**: Proper handling of complex JSON structures from enhanced public opinion analysis strategies

### Web Interface Signal Display Enhancement
- **MODIFIED**: Updated stock_kline_v2.html to directly display database signal content in JSON format
- **ENHANCED**: Improved JSON formatting and display for better readability
- **REMOVED**: Special handling for "信号生成V1" strategy, now all signal strategies use unified display logic
- **ADDED**: Comprehensive JSON detection and formatting for complex nested objects
- **VERIFIED**: Signal generation data now displays complete JSON content from database

### Strategy File Cleanup
- **REMOVED**: Deleted unused strategy files:
  - `strategies/趋势-回踩低吸型策略（抄底型）_strategy.py`
  - `strategies/趋势-放量突破策略（强势股捕捉）_strategy.py`
- **OPTIMIZED**: Reduced codebase clutter by removing auto-generated strategy templates

### Test Script Updates
- **UPDATED**: Modified test scripts to reflect current system architecture
- **ENHANCED**: Improved test coverage for FireCrawl integration and LLM strategy execution
- **FIXED**: Test script initialization issues with strategy parameter requirements

### Akshare Client Enhancement
- **ADDED**: New methods for stock news, industry info, and qian gu qian ping data collection
- **ENHANCED**: Improved financial data extraction with better field mapping
- **OPTIMIZED**: Data formatting and conversion for better LLM compatibility

### Web Interface Stock Search Functionality Enhancement
- **FIXED**: Resolved stock search functionality issues where "润和软件" (300339) and "中科曙光" (603019) were not being found
- **IDENTIFIED**: Root cause was 1000-stock limit in search logic - now loads all 5680 stocks from database
- **IMPLEMENTED**: Correct search logic with intelligent input type detection:
  - Numbers → Stock code search (e.g., "300339" → 润和软件)
  - Chinese characters → Stock name search (e.g., "润和软件" → 300339)
  - English letters → Pinyin abbreviation search (e.g., "rhrj" → 润和软件)
- **ADDED**: Pinyin conversion functionality using `pypinyin` library for automatic Chinese-to-pinyin abbreviation generation
- **ENHANCED**: Case-insensitive search for all input types
- **VERIFIED**: Comprehensive testing confirms all search scenarios work correctly

### Pullback Buying Strategy Numerical Precision Enhancement
- **COMPLETED**: Enhanced Pullback Buying Strategy to ensure all numerical values have 2 decimal places precision
- **MODIFIED**: Updated `_calculate_score` method to return scores with `round(score, 2)` precision
- **MODIFIED**: Updated `analyze` method to ensure score values maintain 2 decimal places precision
- **MODIFIED**: Enhanced `get_technical_analysis_data` method to round all technical values:
  - `price`: `round(float(current_price), 2)`
  - `ma_value`: `round(float(ma_value), 2)`
  - `kdj_j`: `round(float(kdj_j_value), 2)`
  - `rsi_value`: `round(float(rsi_value), 2)`
- **MODIFIED**: Updated `execute` method to ensure position_size values have 2 decimal places precision
- **VERIFIED**: Comprehensive testing confirms all numerical outputs now consistently display with 2 decimal places precision

### Weekly Selector Pool Data Field Fix and Display Enhancement
- **FIXED**: Resolved Weekly Selector pool data field errors where:
  - `_id` field was incorrectly set to strategy ID instead of year-week format (e.g., "2025-42")
  - `strategy_key` field contained strategy names instead of strategy IDs
- **MODIFIED**: Updated `save_selected_stocks` method to ensure:
  - `_id` field uses correct year-week format for both new and updated records
  - `strategy_key` field contains actual strategy IDs
  - All data items are completely overwritten without retaining original values
- **ENHANCED**: Modified Web application to display stock count for trend selection agent
  - Updated `run_agent` function in `web/app.py` to return stock count from pool data
  - Web interface now displays "已完成 (X 支股票)" instead of just "已完成"
- **VERIFIED**: Trend selection agent now correctly displays the number of selected stocks in the web interface

### Weekly Selector Zero Stocks Handling Enhancement
- **ENHANCED**: Modified Weekly Selector to properly handle 0 stocks selection scenario
- **SIMPLIFIED**: Removed complex empty stock checking logic, now uses unified database write logic for both 0 and >0 stocks cases
- **CONSISTENT BEHAVIOR**: Pool records are always created/updated with:
  - `count`: 0 when no stocks selected, actual count when stocks selected
  - `stocks`: empty list when no stocks selected, stock data when stocks selected
- **WEB DISPLAY**: Web interface now correctly displays "0只股票" when no stocks are selected
- **VERIFIED**: System behavior is consistent regardless of selection outcome

### Strategy Score Normalization Enhancement
- **COMPLETED**: Modified three strategies to use 0-1 score range for screening conditions
- **BULLISH GOLDEN CROSS STRATEGY**: Updated screening conditions to use 0.6 threshold and position sizing based on 0.8/0.7/0.6 thresholds
- **TREND FOLLOWING STRATEGY**: Updated screening conditions to use 0.6 threshold and position sizing based on 0.8/0.7/0.6 thresholds
- **PULLBACK BUYING STRATEGY**: Updated screening conditions to use 0.6 threshold and position sizing based on 0.8/0.7/0.6 thresholds
- **UNIFIED STANDARD**: All strategies now follow the same pattern as volume breakout strategy for consistency
- **VERIFIED**: All strategies correctly output scores in 0-1 range with 2 decimal places precision

### Bullish Golden Cross Volume Strategy Implementation
- **COMPLETED**: Created new "趋势-多头金叉放量策略" (BullishGoldenCrossVolumeStrategy)
- **STRATEGY FOCUS**: Detects golden cross startup signals (MA5 crosses above MA10 and MA10 crosses above MA20) with volume amplification
- **SIMPLIFIED CONDITIONS**: Focuses only on golden cross and volume conditions, removed MA slow increasing restriction
- **SCORING LOGIC**: 60% weight for golden cross signal, 40% weight for volume amplification
- **DATABASE INTEGRATION**: Added strategy configuration to MongoDB strategies collection
- **DOCUMENTATION**: Added comprehensive strategy documentation to STRATEGIES_DOCUMENTATION.md
- **TESTED**: Strategy functionality verified with comprehensive test scripts

### K-line Chart Tooltip OHLC Data Display Fix
- **FIXED**: Resolved K线图tooltip中OHLC数据显示错误问题
- **ROOT CAUSE**: ECharts candlestick图表在tooltip中传递的数据格式是5元素数组`[index, open, close, low, high]`，而不是我们预期的4元素OHLC数据
- **FIXES IMPLEMENTED**:
  - 修正了tooltip formatter中OHLC数据的索引访问：
    - data[1]: 开盘价
    - data[2]: 收盘价
    - data[3]: 最低价
    - data[4]: 最高价
  - 添加了调试日志来诊断tooltip数据问题
- **VERIFIED**: 以000006为例，tooltip现在能正确显示：
  - 开盘：11.17
  - 收盘：11.45
  - 最高：11.87
  - 最低：11.17

### Web Interface Agent Last Execution Time Optimization
- **OPTIMIZED**: Enhanced web interface agent last execution time display performance
- **BACKEND**: Created new API endpoint `/api/all-last-execution-times` that fetches all time fields from pool data in a single query
- **FRONTEND**: Replaced individual agent execution time queries with single bulk query
- **TIME FIELD MAPPING**:
  - 趋势选股 → updated_at
  - 技术分析 → tech_at
  - 基本面分析 → fund_at
  - 舆情分析 → pub_at
  - 机器学习 → ml_at
  - 深度学习 → dl_at
  - 强化学习 → rl_at
  - 信号生成 → signals_at
  - 风险控制 → risk_at
  - 策略分析 → analyze_at
- **PERFORMANCE IMPROVEMENT**: Reduced from N database queries to 1, significantly improving page load speed
- **REMOVED**: Deleted unused strategy execution time API and frontend code

### Network Error Retry Handler Enhancement
- **COMPLETED**: Created centralized network error retry handler for consistent error handling across the system
- **NEW FUNCTION**: Added `handle_network_error_with_retry` function in `utils/network_retry_handler.py`
- **FEATURES**:
  - Automatic retry mechanism with configurable retry count (default: 2)
  - Configurable retry delay (default: 5 seconds)
  - Comprehensive network error detection including connection aborted, remote disconnected, and rate limit errors
  - Router IP switching capability for TP-Link WAN2 interface
- **INTEGRATED**: Updated all network error handling functions to use the new centralized handler:
  - `build_concept_index` function in down2mongo.py
  - `write_k_daily` function in down2mongo.py
  - `update_conception` function in down2mongo.py
- **BENEFITS**:
  - Code simplification: Reduced from 10+ lines to 1-2 lines per error handler
  - Consistency: All network errors handled with same logic
  - Maintainability: Single point of modification for retry strategies
  - Flexibility: Customizable retry parameters
  - Extensibility: Can be used anywhere in the project

### ChromeDriver Download Optimization
- **FIXED**: Resolved ChromeDriver download hanging issue in router control functionality
- **ENHANCED**: Added robust ChromeDriver download mechanism with fallback to system PATH
- **FEATURES**:
  - Download progress logging
  - Exception handling for download failures
  - Automatic fallback to system-installed ChromeDriver
  - Retry mechanism with exponential backoff
- **VERIFIED**: Router control now works reliably without blocking on ChromeDriver downloads

### Enhanced Public Opinion Analysis Strategy V2 Fund Flow Data Formatting Fix
- **FIXED**: Resolved fund flow data display issue where individual, industry, and concept fund flow data were not appearing in LLM user prompts
- **ROOT CAUSE**: Field name mismatches between actual data structure and formatting logic
- **FIXES IMPLEMENTED**:
  - Updated field names in `_format_data_for_llm` method to match actual data structure:
    - "今日涨跌幅" instead of "涨跌幅"
    - "今日主力净流入-净占比" instead of "主力净流入"
  - Fixed concept fund flow display to show individual concept items with proper formatting
  - Fixed logger error in `_get_fund_flow_data_for_stock` method
- **VERIFIED**: All fund flow data now correctly displays in user prompts with proper formatting:
  - Individual fund flow: 今日涨跌幅 and 今日主力净流入-净占比
  - Industry fund flow: 今日涨跌幅 and 今日主力净流入-净占比
  - Concept fund flow: 概念名称, 今日涨跌幅, and 今日主力净流入-净占比 for top 5 concepts
- **TESTED**: Comprehensive testing confirms fund flow data is properly collected, formatted, and included in LLM analysis

---
*This document tracks the operations and enhancements made to the Quant MAS system. Last updated: 2025-10-19*

