# Fundamental Analysis Strategies Documentation

This document provides detailed information about the fundamental analysis strategies implemented in the quant trading system.

## Overview

The system implements fundamental analysis strategies that are used by the `FundamentalStockSelector` agent to filter stocks based on various fundamental indicators. These strategies are stored in the MongoDB `strategies` collection and are executed by the fundamental analysis agent.

## Available Strategies

### 1. Traditional Fundamental Strategy (传统基本面策略)
- **ID**: fundamental_strategy
- **Type**: fundamental
- **Description**: 基于财务报表和财务比率的传统基本面分析策略 (Traditional fundamental analysis strategy based on financial statements and financial ratios)
- **File**: `strategies/fundamental_strategy.py`
- **Class**: `FundamentalStrategy`
- **Parameters**:
  - `min_roe`: 0.1 (Minimum Return on Equity 10%)
  - `max_pe`: 20 (Maximum P/E ratio)
  - `min_current_ratio`: 1.5 (Minimum current ratio)
  - `max_debt_equity`: 0.5 (Maximum debt to equity ratio)
  - `min_revenue_growth`: 0.1 (Minimum revenue growth 10%)
- **Decision Criteria**:
  - Selects stocks with strong profitability (ROE >= 10%)
  - Focuses on financially healthy companies with reasonable debt levels
  - Requires consistent revenue growth
  - Emphasizes liquidity and operational efficiency

### 2. LLM Fundamental Strategy (基于LLM的基本面分析策略)
- **ID**: llm_fundamental_strategy
- **Type**: fundamental
- **Description**: 基于大语言模型的智能基本面分析策略 (Intelligent fundamental analysis strategy based on large language models)
- **File**: `strategies/llm_fundamental_strategy.py`
- **Class**: `LLMFundamentalStrategy`
- **Parameters**:
  - `llm_config_name`: "default" (Name of LLM configuration to use)
- **Decision Criteria**:
  - Uses advanced LLM analysis for comprehensive fundamental evaluation
  - Incorporates financial statements, ratios, industry comparisons, and trend analysis
  - Provides detailed analysis with 0-1 scoring system
  - Implements retry mechanisms for improved reliability

## Fundamental Indicators Calculated

The system calculates and stores the following fundamental indicators for each stock:

1. **P/E Ratio (Price-to-Earnings Ratio)**: Measures a company's current share price relative to its per-share earnings
2. **P/B Ratio (Price-to-Book Ratio)**: Compares a company's market value to its book value
3. **P/S Ratio (Price-to-Sales Ratio)**: Values a company based on its market capitalization relative to its revenues
4. **Debt-to-Equity Ratio**: Indicates the proportion of debt financing relative to equity
5. **Current Ratio**: Measures a company's ability to pay short-term obligations
6. **ROE (Return on Equity)**: Measures a company's profitability relative to shareholders' equity
7. **ROA (Return on Assets)**: Indicates how efficiently a company uses its assets to generate profit
8. **Gross Margin**: Shows the percentage of revenue that exceeds the cost of goods sold
9. **Net Profit Margin**: Indicates how much profit a company makes for each dollar of revenue
10. **Revenue Growth Rate**: Measures the percentage increase in a company's revenue over time
11. **Earnings Growth Rate**: Measures the percentage increase in a company's earnings over time
12. **Dividend Yield**: Shows how much a company pays out in dividends each year relative to its stock price
13. **Dividend Payout Ratio**: Indicates the percentage of earnings paid to shareholders in dividends

## Database Record Structure

### Agents Collection
- Contains agent definitions with their associated strategies
- The fundamental analysis agent (基本面分析Agent) will use fundamental analysis strategies

### Strategies Collection
- Contains detailed strategy definitions with parameters and decision criteria
- Each strategy has a unique ID, name, type, description, and parameters
- Strategies are categorized by fundamental analysis types
- Uses the modern "program" field specification for dynamic loading

### Pool Collection
- Stores the results of strategy executions
- Contains stock selections with fundamental analysis data
- Records are identified by year-week keys (e.g., "2025-32")
- Each record includes:
  - Selected stocks with their codes
  - Fundamental analysis results for each stock
  - Metadata including selection date, reference date, and timestamps

## Usage Examples

To execute fundamental analysis strategies:

1. Call the `/run_agent` API endpoint with the fundamental analysis agent
2. The system will execute all associated strategies
3. Results are saved to the pool collection with clear labeling
4. Fundamental analysis data is updated for all stocks in the pool

## Implementation Details

### Fundamental Data Sources
- Financial statements data (income statement, balance sheet, cash flow statement)
- Market data (stock prices, market capitalization)
- Industry and sector classification data

### Data Processing Pipeline
1. Fetch raw financial data from data sources
2. Calculate fundamental ratios and metrics
3. Apply strategy-specific filters and criteria
4. Score stocks based on strategy parameters
5. Save results to database with proper labeling

### Scoring Methodology
- Each strategy assigns scores to stocks based on how well they meet criteria
- Scores are normalized to 0-1 range for consistency
- Multiple strategies can be combined with weighted scoring
- LLM-based strategies include retry mechanisms for improved reliability

#### Detailed Score Handling
- **Score Range Processing**: LLM strategies explicitly request scores in 0-1 range in their prompts, so no additional normalization is needed
- **Default Score**: When parsing fails or LLM access fails, returns default score of 0.0
- **Score Validation**: Ensures final scores are within 0-1 range, values outside this range are clipped
- **Score Precision**: Scores are rounded to 2 decimal places
- **Retry Impact**: During retries, if any attempt succeeds, the successful result is used; if all fail, default score 0.0 is used

### Error Handling and Retry Logic
- LLM-based strategies implement retry mechanisms with exponential backoff
- When JSON parsing fails or LLM API calls fail, the system retries up to 3 times
- If all retries fail, a default score of 0.0 is returned to ensure continuity
- Exponential backoff (1s, 2s, 4s delays) prevents overwhelming the LLM service

## Future Improvements

1. Add more sophisticated fundamental strategies with configurable parameters
2. Implement strategy combination logic for better filtering
3. Add backtesting capabilities for strategy validation
4. Include visualization tools for fundamental indicators
5. Add performance tracking for each strategy
6. Implement sector-based analysis and benchmarking
7. Add economic moat analysis and competitive advantage assessment
8. Include ESG (Environmental, Social, Governance) factors in analysis
9. Implement predictive fundamental models using machine learning
10. Add international market fundamental data support

