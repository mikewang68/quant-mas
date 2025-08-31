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

### Key Strategy Files
- `strategies/base_strategy.py` - Base strategy interface
- `strategies/macd_strategy.py` - MACD indicator strategy
- `strategies/rsi_strategy.py` - RSI-based strategy
- `strategies/ma_crossover_strategy.py` - Moving average crossover
- `strategies/multi_agent_strategy.py` - Multi-agent coordination
- `strategies/fundamental_strategy.py` - Traditional fundamental analysis strategy
- `strategies/llm_fundamental_strategy.py` - LLM-based fundamental analysis strategy

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

## Recent Operations and Enhancements

### Public Opinion Selector Framework Creation
- Created new Public Opinion Selector agent framework based on Technical Selector pattern
- Added support for dynamically loading strategies assigned to "舆情分析Agent" from database
- Implemented pool dataset integration with "pub" field for public opinion analysis results
- Created runner script for executing public opinion analysis strategies
- Updated documentation to include new agent and usage patterns
- Added example strategy and database insertion scripts to help users get started
- Created utility script to initialize and configure the 舆情分析Agent in MongoDB database with proper Chinese description

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

### Fundamental Analysis Strategies Implementation
- Added two fundamental analysis strategies to the system:
  - **Traditional Fundamental Strategy**: Standard financial ratio analysis with configurable parameters
  - **LLM Fundamental Strategy**: AI-powered analysis using large language models
- Both strategies are fully configurable through database parameters
- LLM strategy supports flexible provider configuration with dynamic API key environment variable handling
- Created configuration files and database insertion scripts for both strategies
- Assigned strategies to the Fundamental Analysis Agent for proper execution

### LLM Configuration Flexibility Enhancement
- Improved LLM fundamental strategy to support different LLM providers
- Added configurable API key environment variable name in database configuration
- Strategy now reads API key from dynamically specified environment variable
- Supports switching between providers (Google Gemini, OpenAI, Anthropic, etc.) without code changes
- Configuration fully dynamic from database with no hardcoded values
- Updated both database configuration and strategy implementation

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

---
*This document tracks the operations and enhancements made to the Quant MAS system. Last updated: 2025-08-30*

