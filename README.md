# Quantitative Trading System

This is a multi-agent quantitative trading system built with Python. The system uses technical analysis, fundamental analysis, and machine learning to make trading decisions.

## Project Structure

```
├── agents/                 # Trading agents (智能体)
│   ├── base_agent.py              # Base agent class
│   ├── weekly_selector.py         # Weekly stock selector agent
│   ├── technical_selector.py      # Technical analysis agent
│   ├── fundamental_selector.py    # Fundamental analysis agent
│   ├── public_opinion_selector.py # Public opinion analysis agent
│   └── daily_trader.py            # Daily trading agent
├── backtesting/            # Backtesting framework
│   └── backtester.py       # Backtesting engine
├── config/                 # Configuration files
│   ├── app_settings.yaml   # Application settings
│   ├── config.yaml         # System configuration
│   └── database.yaml       # Database configuration
├── data/                   # Data management
│   ├── data_fetcher.py     # Data fetching utilities
│   └── mongodb_manager.py  # MongoDB database manager
├── strategies/             # Trading strategies
│   ├── base_strategy.py           # Base strategy class
│   ├── ma_crossover_strategy.py   # Moving average crossover strategy
│   ├── accelerating_uptrend_strategy.py  # Accelerating uptrend strategy
│   ├── momentum_strategy.py       # Momentum strategy
│   ├── trend_following_strategy.py # Trend following strategy
│   ├── three_ma_bullish_arrangement_strategy.py # Three MA bullish arrangement strategy
│   ├── vmap_turnover_strategy.py  # VMAP turnover strategy
│   ├── hma_turnover_strategy.py   # HMA turnover strategy
│   ├── volume_breakout_strategy.py # Volume breakout strategy
│   ├── pullback_buying_strategy.py # Pullback buying strategy
│   ├── fundamental_strategy.py     # Traditional fundamental analysis strategy
│   ├── llm_fundamental_strategy.py # LLM-based fundamental analysis strategy
│   ├── public_opinion_analysis_strategy.py # Public opinion analysis strategy
│   └── multi_agent_strategy.py    # Multi-agent strategy
├── utils/                  # Utility functions
│   ├── logger.py           # Logging utilities
│   └── paths.py            # Path utilities
├── web/                    # Web interface
│   ├── app.py              # Flask web application
│   ├── static/             # Static files (CSS, JS, images)
│   └── templates/          # HTML templates
├── docs/                   # Documentation
│   └── *.md                # Various documentation files
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Multi-Agent Architecture

This system implements a multi-agent architecture where different agents handle specialized tasks:

### 1. Weekly Stock Selector Agent (`agents/weekly_selector.py`)
- Selects stocks for weekly trading based on technical indicators and fundamental analysis
- Filters stocks based on market capitalization, volume, and trend criteria
- Uses weekly data to identify potential trading opportunities

### 2. Technical Analysis Agent (`agents/technical_selector.py`)
- Performs daily technical analysis on stocks in the pool
- Dynamically loads and executes multiple technical analysis strategies
- Updates pool with technical analysis results for each strategy

### 3. Fundamental Analysis Agent (`agents/fundamental_selector.py`)
- Performs fundamental analysis on stocks in the pool
- Supports both traditional financial ratio analysis and LLM-based analysis
- Updates pool with fundamental analysis results

### 4. Public Opinion Analysis Agent (`agents/public_opinion_selector.py`)
- Analyzes public opinion and sentiment for stock selection
- Uses various public opinion analysis strategies
- Updates pool with public opinion analysis results

### 5. Daily Trader Agent (`agents/daily_trader.py`)
- Makes daily trading decisions for selected stocks
- Implements technical analysis using indicators like MA, MACD, RSI, Bollinger Bands
- Manages position sizing, stop-loss, and take-profit mechanisms

### 6. Base Agent (`agents/base_agent.py`)
- Abstract base class defining the agent interface
- Provides common functionality like logging

## Data Management

### MongoDB Manager (`data/mongodb_manager.py`)
- Handles all interactions with MongoDB database
- Stores stock codes, K-line data, and update dates
- Recently modified to handle different adjust types (none, qfq, hfq)
- Supports dynamic loading of strategies from database
- Manages agent configurations and strategy assignments

### Data Fetcher (`data/data_fetcher.py`)
- Fetches data from external sources
- Provides interface for getting stock lists, K-line data, and stock information
- Implements rate limiting to avoid overwhelming data sources

## Web Interface

### Flask Application (`web/app.py`)
- Provides REST API and web UI for system monitoring and control
- Exposes endpoints for:
  - System status monitoring
  - Stock list management
  - Strategy selection
  - Backtesting execution
  - Trade execution
  - Real-time stock and cryptocurrency price retrieval
  - Account management with profit/loss calculation
  - Dynamic agent execution based on program field

## Configuration

The system uses YAML configuration files for easy customization:
- `config.yaml`: Main system configuration
- `database.yaml`: Database connection settings
- `app_settings.yaml`: Application-specific settings

## Backtesting

The backtesting framework allows testing strategies with historical data:
- Uses backtrader for strategy backtesting
- Provides performance metrics and analysis
- Supports multi-agent backtesting scenarios

## Getting Started

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure database settings in `config/database.yaml`

3. Run the web application:
   ```
   python web/app.py
   ```

4. Access the web interface at `http://localhost:5000`

## Key Features

1. **Multi-Agent Approach**: Different agents handle specialized tasks
2. **Technical Analysis**: Implements various technical indicators (MA, MACD, RSI, Bollinger Bands)
3. **Fundamental Analysis**: Traditional financial ratio analysis and LLM-based analysis
4. **Public Opinion Analysis**: Sentiment analysis for stock selection
5. **Risk Management**: Position sizing limits, stop-loss, and take-profit mechanisms
6. **Modular Design**: Each component has a single responsibility
7. **Database Integration**: Uses MongoDB for persistent storage
8. **Web Interface**: Provides REST API and dashboard for system monitoring
9. **Backtesting**: Comprehensive backtesting framework for strategy evaluation
10. **Real-time Market Data**:
    - Stock prices via akshare library
    - Cryptocurrency prices via Binance API
11. **Account Management**:
    - Real-time profit/loss calculation
    - Support for both stock and cryptocurrency accounts
12. **Configurable Data Adjustment**:
    - Choose between no adjustment, pre-adjusted (qfq), or post-adjusted (hfq) price data
    - Settings stored in MongoDB and configurable through web interface
13. **Dynamic Strategy Loading**:
    - Strategies are dynamically loaded from database
    - Agents execute strategies based on their configuration
    - Support for multiple strategies per agent

