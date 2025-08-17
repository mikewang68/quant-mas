# Technical Analysis Strategies Documentation

This document provides detailed information about the technical analysis strategies implemented in the quant trading system.

## Overview

The system currently implements several technical analysis strategies that are used by the `TechnicalStockSelector` agent to filter stocks based on various technical indicators. These strategies are stored in the MongoDB `strategies` collection and are executed by the technical analysis agent.

## Available Strategies

### 1. RSI Strategy (测试策略1-RSI)
- **ID**: 689d4726db90938e01ab0788
- **Type**: rsi
- **Description**: 测试RSI策略 (Test RSI Strategy)
- **Parameters**:
  - `rsi_period`: 14 (RSI calculation period)
  - `rsi_min`: 30 (Minimum RSI threshold)
  - `rsi_max`: 70 (Maximum RSI threshold)
- **Decision Criteria**: 
  - Selects stocks where the RSI value is between 30 and 70, indicating the stock is neither overbought nor oversold
  - This range suggests the stock is in a neutral trading range

### 2. MACD Strategy (测试策略2-MACD)
- **ID**: 689d4726db90938e01ab0789
- **Type**: macd
- **Description**: 测试MACD策略 (Test MACD Strategy)
- **Parameters**: None (uses default MACD settings)
- **Decision Criteria**:
  - Looks for bullish crossover patterns where the MACD line crosses above the signal line
  - Confirms the MACD line is positive (above zero)
  - Requires a previous bearish condition to confirm the crossover

### 3. Bollinger Bands Strategy (测试策略3-布林带)
- **ID**: 689d4726db90938e01ab078a
- **Type**: bollinger
- **Description**: 测试布林带策略 (Test Bollinger Bands Strategy)
- **Parameters**:
  - `bb_period`: 20 (Bollinger Bands calculation period)
  - `bb_stddev`: 2.0 (Standard deviation multiplier)
- **Decision Criteria**:
  - Selects stocks where the price is above the middle band but below the upper band
  - This indicates the stock is in the upper half of the band but not overbought

### 4. Weekly Line Selection Strategy (周线选股)
- **ID**: 689853fd9a7440733f19d935
- **Type**: technical
- **Description**: 使用斐波那契数列设置3均线，分别是5,13,34,均线多头排列 (Using Fibonacci sequence to set 3 moving averages: 5, 13, 34, with bullish alignment)
- **Parameters**:
  - `long`: 34 (Long-term moving average period)
  - `mid`: 13 (Medium-term moving average period)
  - `short`: 5 (Short-term moving average period)
- **Decision Criteria**:
  - Selects stocks where the moving averages are in bullish alignment (5-day > 13-day > 34-day)
  - This indicates a strong upward trend

## Technical Indicators Calculated

The system calculates and stores the following technical indicators for each stock:

1. **RSI (Relative Strength Index)**: Measures the speed and change of price movements
2. **MACD (Moving Average Convergence Divergence)**: Shows the relationship between two moving averages
3. **Bollinger Bands**: Provides relative definitions of high and low prices
4. **Moving Averages**: Simple and exponential moving averages for different periods
5. **Stochastic Oscillator**: Compares a particular closing price to a range of prices over time
6. **Williams %R**: Measures overbought and oversold levels
7. **CCI (Commodity Channel Index)**: Identifies cyclical trends

## Database Record Structure

### Agents Collection
- Contains agent definitions with their associated strategies
- The technical analysis agent (技术分析Agent) uses strategies 689d4726db90938e01ab0788, 689d4726db90938e01ab0789, and 689d4726db90938e01ab078a

### Strategies Collection
- Contains detailed strategy definitions with parameters and decision criteria
- Each strategy has a unique ID, name, type, description, and parameters

### Pool Collection
- Stores the results of strategy executions
- Contains stock selections with technical analysis data
- Records are identified by year-week keys (e.g., "2025-32")
- Each record includes:
  - Selected stocks with their codes
  - Technical analysis results for each stock
  - Metadata including selection date, reference date, and timestamps

## Usage Examples

To execute technical analysis strategies:

1. Call the `/run_agent` API endpoint with the technical analysis agent
2. The system will execute all associated strategies
3. Results are saved to the pool collection with clear labeling
4. Technical analysis data is updated for all stocks in the pool

## Future Improvements

1. Add more sophisticated strategies with configurable parameters
2. Implement strategy combination logic for better filtering
3. Add backtesting capabilities for strategy validation
4. Include visualization tools for technical indicators
5. Add performance tracking for each strategy

