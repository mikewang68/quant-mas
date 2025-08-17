# Quantitative Trading System

This is a multi-agent quantitative trading system built with Python. The system uses technical analysis and machine learning to make trading decisions.

## Project Structure

```
├── agents/                 # Trading agents (智能体)
│   ├── base_agent.py       # Base agent class
│   ├── weekly_selector.py  # Weekly stock selector agent
│   └── daily_trader.py     # Daily trading agent
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
│   ├── base_strategy.py    # Base strategy class
│   ├── ma_crossover_strategy.py  # Moving average crossover strategy
│   ├── accelerating_uptrend_strategy.py  # Accelerating uptrend strategy
│   └── multi_agent_strategy.py   # Multi-agent strategy
├── utils/                  # Utility functions
│   ├── logger.py           # Logging utilities
│   └── paths.py            # Path utilities
├── web/                    # Web interface
│   ├── app.py              # Flask web application
│   ├── static/             # Static files (CSS, JS, images)
│   └── templates/          # HTML templates
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Multi-Agent Architecture

This system implements a multi-agent architecture where different agents handle specialized tasks:

### 1. Weekly Stock Selector Agent (`agents/weekly_selector.py`)
- Selects stocks for weekly trading based on technical indicators and fundamental analysis
- Filters stocks based on market capitalization, volume, and trend criteria
- Uses weekly data to identify potential trading opportunities

### 2. Daily Trader Agent (`agents/daily_trader.py`)
- Makes daily trading decisions for selected stocks
- Implements technical analysis using indicators like MA, MACD, RSI, Bollinger Bands
- Manages position sizing, stop-loss, and take-profit mechanisms

### 3. Base Agent (`agents/base_agent.py`)
- Abstract base class defining the agent interface
- Provides common functionality like logging

## Strategy Implementation

### Multi-Agent Strategy (`strategies/multi_agent_strategy.py`)
- Combines both agents' functionalities in a backtrader strategy framework
- Coordinates weekly stock selection with daily trading decisions

### MA Crossover Strategy (`strategies/ma_crossover_strategy.py`)
- Simple moving average crossover strategy for comparison

## Data Management

### MongoDB Manager (`data/mongodb_manager.py`)
- Handles all interactions with MongoDB database
- Stores stock codes, K-line data, and update dates
- Recently modified to handle different adjust types (none, qfq, hfq)

### Data Fetcher (`data/data_fetcher.py`)
- Fetches data from external sources
- Provides interface for getting stock lists, K-line data, and stock information

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

## Configuration

The system uses YAML configuration files for easy customization:
- `config.yaml`: Main system configuration
- `database.yaml`: Database connection settings
- `app_settings.yaml`: Application-specific settings

## Backtesting

The backtesting framework allows testing strategies with historical data:
- Uses backtrader for strategy backtesting
- Provides performance metrics and analysis

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
3. **Risk Management**: Position sizing limits, stop-loss, and take-profit mechanisms
4. **Modular Design**: Each component has a single responsibility
5. **Database Integration**: Uses MongoDB for persistent storage
6. **Web Interface**: Provides REST API and dashboard for system monitoring
7. **Backtesting**: Comprehensive backtesting framework for strategy evaluation
8. **Real-time Market Data**: 
   - Stock prices via akshare library
   - Cryptocurrency prices via Binance API
9. **Account Management**: 
   - Real-time profit/loss calculation
   - Support for both stock and cryptocurrency accounts
10. **Configurable Data Adjustment**: 
    - Choose between no adjustment, pre-adjusted (qfq), or post-adjusted (hfq) price data
    - Settings stored in MongoDB and configurable through web interface

