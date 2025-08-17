# Technical Analysis Strategies Documentation (Enhanced)

This document provides detailed information about the technical analysis strategies implemented in the quant trading system, with enhanced clarity and detailed parameter specifications.

## Overview

The system implements several technical analysis strategies that are used by the `TechnicalStockSelector` agent to filter stocks based on various technical indicators. These strategies are stored in the MongoDB `strategies` collection and are executed by the technical analysis agent.

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
  - Selection Reason Format: "Selected - RSI: {value} (range: 30-70)" or "Not selected - RSI: {value} (range: 30-70)"

### 2. MACD Strategy (测试策略2-MACD)
- **ID**: 689d4726db90938e01ab0789
- **Type**: macd
- **Description**: 测试MACD策略 (Test MACD Strategy)
- **Parameters**: None (uses default MACD settings: 12, 26, 9)
- **Decision Criteria**:
  - Looks for bullish crossover patterns where the MACD line crosses above the signal line
  - Confirms the MACD line is positive (above zero)
  - Requires a previous bearish condition to confirm the crossover
  - Selection Reason Format: "Selected - MACD bullish crossover detected (MACD: {value}, Signal: {value})" or "Not selected - No MACD bullish crossover (MACD: {value}, Signal: {value})"

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
  - Selection Reason Format: "Selected - Price: {value}, Upper: {value}, Middle: {value}, Lower: {value}" or "Not selected - Price: {value}, Upper: {value}, Middle: {value}, Lower: {value}"

### 4. Multi-Indicator Strategy (周线选股)
- **ID**: 689853fd9a7440733f19d935
- **Type**: technical
- **Description**: 使用斐波那契数列设置3均线，分别是5,13,34,均线多头排列 (Using Fibonacci sequence to set 3 moving averages: 5, 13, 34, with bullish alignment)
- **Parameters**:
  - `rsi_period`: 14 (RSI calculation period)
  - `rsi_min`: 30 (Minimum RSI threshold)
  - `rsi_max`: 70 (Maximum RSI threshold)
  - `ma_short`: 5 (Short-term moving average period)
  - `ma_long`: 20 (Long-term moving average period)
- **Decision Criteria**:
  - Combines RSI analysis with moving average alignment
  - RSI must be between 30-70 (not overbought or oversold)
  - Price must be above both short and long moving averages with bullish alignment
  - Selection Reason Format: "Selected - RSI: {value}, Price: {value}, MA5: {value}, MA20: {value}" or "Not selected - RSI: {value} (range: 30-70), Price: {value}, MA5: {value}, MA20: {value}"

## Technical Indicators Calculated

The system calculates and stores the following technical indicators for each stock:

1. **RSI (Relative Strength Index)**: Measures the speed and change of price movements
   - Formula: Based on average gains and losses over N periods
   - Interpretation: Values above 70 indicate overbought conditions, below 30 indicate oversold

2. **MACD (Moving Average Convergence Divergence)**: Shows the relationship between two moving averages
   - Components: MACD line (12-day EMA - 26-day EMA), Signal line (9-day EMA of MACD line)
   - Interpretation: Bullish crossover when MACD crosses above signal line

3. **Bollinger Bands**: Provides relative definitions of high and low prices
   - Components: Middle band (20-day SMA), Upper band (Middle + 2*standard deviation), Lower band (Middle - 2*standard deviation)
   - Interpretation: Price near upper band indicates overbought, near lower band indicates oversold

4. **Moving Averages**: Simple and exponential moving averages for different periods
   - Types: Simple Moving Average (SMA), Exponential Moving Average (EMA)
   - Interpretation: Bullish alignment when shorter-term MA is above longer-term MA

5. **Stochastic Oscillator**: Compares a particular closing price to a range of prices over time
   - Components: %K line, %D line (3-period moving average of %K)
   - Interpretation: Values above 80 indicate overbought, below 20 indicate oversold

6. **Williams %R**: Measures overbought and oversold levels
   - Range: 0 to -100
   - Interpretation: Values above -20 indicate overbought, below -80 indicate oversold

7. **CCI (Commodity Channel Index)**: Identifies cyclical trends
   - Range: Typically -100 to +100
   - Interpretation: Values above +100 indicate overbought, below -100 indicate oversold

## Database Record Structure

### Agents Collection
- Contains agent definitions with their associated strategies
- The technical analysis agent (技术分析Agent) uses strategies 689d4726db90938e01ab0788, 689d4726db90938e01ab0789, and 689d4726db90938e01ab078a

### Strategies Collection
- Contains detailed strategy definitions with parameters and decision criteria
- Each strategy has a unique ID, name, type, description, and parameters
- Enhanced with clear selection reason formats for better interpretability

### Pool Collection
- Stores the results of strategy executions
- Contains stock selections with technical analysis data
- Records are identified by year-week keys (e.g., "2025-32")
- Each record includes:
  - Selected stocks with their codes and detailed selection reasons
  - Strategy parameters used for selection
  - Technical analysis results for each stock
  - Metadata including selection date, reference date, and timestamps
  - Enhanced structure for better interpretability:
    ```json
    {
      "_id": "TechnicalStockSelector_{strategy_id}_{year}-{week}",
      "agent_name": "TechnicalStockSelector",
      "strategy_id": "{strategy_id}",
      "strategy_name": "{strategy_name}",
      "strategy_parameters": { /* parameters used */ },
      "year": 2025,
      "week": 32,
      "selection_date": "2025-08-10",
      "reference_date": "2025-08-08",
      "stocks": [
        {
          "code": "000001",
          "selection_reason": "Detailed reason for selection"
        }
      ],
      "count": 15,
      "created_at": "2025-08-10T10:30:00Z",
      "updated_at": "2025-08-10T10:30:00Z"
    }
    ```

## Enhanced Selection Reason Format

Each strategy now provides detailed selection reasons in a standardized format:

1. **RSI Strategy**: "Selected - RSI: {value} (range: 30-70)" or "Not selected - RSI: {value} (range: 30-70)"
2. **MACD Strategy**: "Selected - MACD bullish crossover detected (MACD: {value}, Signal: {value})" or "Not selected - No MACD bullish crossover (MACD: {value}, Signal: {value})"
3. **Bollinger Bands Strategy**: "Selected - Price: {value}, Upper: {value}, Middle: {value}, Lower: {value}" or "Not selected - Price: {value}, Upper: {value}, Middle: {value}, Lower: {value}"
4. **Multi-Indicator Strategy**: "Selected - RSI: {value}, Price: {value}, MA5: {value}, MA20: {value}" or "Not selected - RSI: {value} (range: 30-70), Price: {value}, MA5: {value}, MA20: {value}"

## Usage Examples

To execute technical analysis strategies:

1. Call the `/run_agent` API endpoint with the technical analysis agent
2. The system will execute all associated strategies
3. Results are saved to the pool collection with clear labeling and detailed selection reasons
4. Technical analysis data is updated for all stocks in the pool

Example API call:
```bash
curl -X POST http://localhost:8000/run_agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "68993413e3032fe19a7b41ae",
    "params": {
      "date": "2025-08-10"
    }
  }'
```

## Database Record Enhancement Details

### Before Enhancement
- Basic stock selection with minimal reason information
- Limited strategy parameter tracking
- Generic labeling

### After Enhancement
- Detailed selection reasons for each stock with actual values
- Complete strategy parameter tracking in each record
- Clear, standardized labels for different strategies
- Enhanced metadata including execution details and timestamps
- Improved database structure for better interpretability

## Future Improvements

1. Add more sophisticated strategies with configurable parameters
2. Implement strategy combination logic for better filtering
3. Add backtesting capabilities for strategy validation
4. Include visualization tools for technical indicators
5. Add performance tracking for each strategy
6. Implement strategy optimization based on historical performance
7. Add support for custom strategy creation through configuration
8. Enhance database indexing for faster query performance

