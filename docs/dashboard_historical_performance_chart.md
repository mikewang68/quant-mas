# Dashboard Historical Performance Chart

## Overview

The Dashboard Historical Performance Chart is a comprehensive visualization tool that displays account asset performance compared to benchmark indices over time. This feature provides investors with detailed insights into their portfolio performance relative to market benchmarks.

## Features

### 1. Dual Y-Axis Display
- **Left Y-Axis**: Shows real benchmark index values
- **Right Y-Axis**: Shows account assets in 万 (10,000) units
- Both axes are properly scaled and labeled for clear comparison

### 2. Data Sources
- **Account Data**: Retrieved from MongoDB accounts collection
- **Order Data**: Historical trading records from orders collection
- **Stock Prices**: Real-time and historical data via AkShare API
- **Index Data**: Benchmark index data via AkShare API

### 3. Benchmark Selection
Users can select from multiple benchmark indices:
- 上证50 (SSE 50)
- 沪深300 (CSI 300) - Default
- 中证500 (CSI 500)

### 4. Chart Styling
- **Grid Lines**: Dark theme (#333) for better visual clarity
- **Asset Curve**: Yellow (#ffff00) line representing account assets
- **Index Curve**: White (#ffffff) line representing benchmark index
- **Legend**: Color-coded text matching curve colors

### 5. Synchronized Starting Points
Both curves start from the same visual point at the account's first stock purchase date, enabling accurate performance comparison from the moment of initial investment.

### 6. Interactive Features
- **Zoom Controls**: Default view shows last 1 year of data
- **Slider Control**: Bottom slider for easy time range selection
- **Tooltip**: Comprehensive hover information
- **Resize Support**: Responsive chart that adapts to window size changes

## Tooltip Information

The tooltip provides detailed information when hovering over data points:

### Basic Information
- Date of the data point
- Account asset value (in 万 units)
- Benchmark index value

### Detailed Asset Information
- **Date**: Specific date of the data point
- **Cash**: Available cash in the account
- **Portfolio Value**: Total value of stock holdings
- **Total Assets**: Sum of cash and portfolio value

### Stock Holdings (if any)
For each held stock:
- **Stock Code**: Trading symbol
- **Quantity**: Number of shares held
- **Current Price**: Market price at that date
- **Cost Price**: Average purchase price
- **Market Value**: Current market value of holdings
- **Total Cost**: Total cost basis of holdings
- **Profit/Loss**: Gain/loss amount and percentage with color coding
  - Green for profits
  - Red for losses

## Technical Implementation

### Data Flow
1. **Account Selection**: User selects account from dropdown
2. **Order Retrieval**: System fetches all orders for the selected account
3. **Date Range Calculation**: Determines date range from first purchase to present
4. **Stock Data Fetching**: Retrieves historical price data for all traded stocks
5. **Index Data Fetching**: Gets benchmark index data for comparison
6. **Asset Calculation**: Computes daily asset values considering:
   - Cash changes from trades
   - Stock quantity changes from buys/sells
   - Market value changes from price movements
7. **Chart Rendering**: Displays dual-axis chart with synchronized starting points

### API Endpoints
- `/api/akshare/index-data`: Fetches historical index data
- `/api/akshare/stock-data`: Fetches historical stock price data
- `/api/accounts`: Retrieves account information
- `/api/orders`: Gets trading order history

### Key Functions
- `loadPortfolioPerformance()`: Main function to load and display chart
- `calculateHistoricalAssetData()`: Orchestrates data fetching and calculation
- `fetchIndexData()`: Retrieves benchmark index data
- `fetchStockPriceData()`: Gets stock price history
- `calculateDailyAssetValues()`: Computes daily portfolio values
- `createDualAxisChart()`: Renders the ECharts visualization

## Usage

1. **Select Account**: Choose an account from the dropdown menu
2. **Choose Benchmark**: Select desired benchmark index for comparison
3. **View Performance**: Chart automatically displays with last 1 year visible
4. **Interact**: Use zoom controls, hover for details, adjust time range
5. **Analyze**: Compare account performance against benchmark over time

## Benefits

- **Performance Tracking**: Visual comparison of portfolio vs. market performance
- **Risk Assessment**: Understand portfolio volatility relative to benchmarks
- **Investment Analysis**: Evaluate the effectiveness of trading strategies
- **Historical Context**: See how external market conditions affected portfolio
- **Detailed Insights**: Comprehensive tooltip information for thorough analysis

## Future Enhancements

Potential improvements could include:
- Additional benchmark indices
- Performance metrics calculation (Sharpe ratio, alpha, beta)
- Export functionality for charts and data
- Multiple account comparison
- Sector-specific benchmark comparisons
- Risk-adjusted return calculations

