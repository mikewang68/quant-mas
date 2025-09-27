# Enhanced Public Opinion Analysis Strategy Documentation

## Overview

The Enhanced Public Opinion Analysis Strategy is an advanced stock selection strategy that leverages public sentiment and news analysis to identify potentially favorable investment opportunities. It integrates multiple data sources including AkShare financial data, professional financial websites, FireCrawl web search, and LLM (Large Language Model) evaluation to provide a comprehensive assessment of public opinion about stocks.

## Strategy Structure

### Class Inheritance
- `EnhancedPublicOpinionAnalysisStrategy` inherits from `BaseStrategy` base class
- Follows the unified interface and specifications of other strategies in the system

### Core Components

#### Initialization Method
- `__init__`: Initializes strategy parameters and configurations
  - Strategy parameters: sentiment threshold, news count threshold, search depth, time window
  - Data sources configuration: akshare, firecrawl, professional sites
  - FireCrawl configuration: API address, timeout
  - LLM configuration: API address, API key (read from environment variables), model, timeout

#### Core Analysis Methods
- `get_akshare_news`: Retrieves stock news from AkShare financial data API
- `get_professional_site_data`: Collects data from professional financial websites
- `search_stock_news`: Uses FireCrawl to search for stock-related news
- `collect_all_data`: Aggregates data from all configured sources
- `_calculate_time_weight`: Calculates time decay weights for information时效性
- `analyze_sentiment_with_llm`: Uses LLM to analyze sentiment with enhanced multi-source prompt and retry mechanism
- `analyze_public_opinion`: Integrates multi-source data collection and sentiment analysis
- `analyze`: Main analysis method that calls `analyze_public_opinion`
- `_calculate_score`: Normalizes the sentiment score
- `execute`: Main strategy execution method that processes multiple stocks and returns results without saving to database
- `generate_signals`: Generates trading signals (not actually used in this strategy)
- `calculate_position_size`: Calculates position size (uses fixed values in this strategy)

## Execution Logic

### 1. Initialization Phase
1. Set strategy parameters:
   - `sentiment_threshold`: Sentiment score threshold, default 0.6
   - `news_count_threshold`: Minimum number of relevant information items, default 5
   - `search_depth`: Search result analysis depth, default 10
   - `time_window_hours`: Time window for recent data, default 24 hours
   - `data_sources`: List of data sources to use ['akshare', 'firecrawl', 'professional_sites']
2. Configure data sources:
   - Professional financial websites: 同花顺财经, 东方财富网, 雪球网, 新浪财经, 腾讯财经
3. Configure FireCrawl and LLM service connection parameters

### 2. Execution Phase
When the strategy is executed, the process flows as follows:

1. **Batch Processing of Stock Data**:
   - Iterate through the provided stock data dictionary
   - Retrieve stock names from the database (if available)
   - Check existing scores in the pool database to skip stocks with non-zero scores

2. **Individual Stock Analysis Process**:
   - Skip stocks that already have non-zero scores in the pool's pub field
   - Call the `analyze` method to begin analysis
   - Within `analyze`, call the `analyze_public_opinion` method

3. **Multi-Source Data Collection Process**:
   - Collect data from AkShare financial news API
   - Collect data from professional financial websites
   - Collect data from FireCrawl web search
   - Apply time decay weights to all collected information
   - Aggregate and sort all data by recency and importance

4. **Enhanced LLM Sentiment Analysis Process with Retry Mechanism**:
   - Group data by source type for better organization
   - Construct comprehensive analysis prompts with source information
   - Send request to LLM API with enhanced prompt
   - Retry up to 3 times with exponential backoff (1s, 2s, 4s) on network timeouts
   - Parse the LLM response and extract sentiment scores and detailed analysis
   - Handle JSON parsing failures with fallback extraction

5. **Result Processing**:
   - Calculate normalized scores for stocks that meet the criteria
   - Construct result data structures with score and comprehensive analysis details

### 3. Output Results
After strategy execution, it returns a list of qualifying stocks, each containing:
- Stock code
- Normalized score (between 0-1)
- Value: Comprehensive analysis details including sentiment trend, key events, market impact, confidence level, analysis summary, recommendation, and risk factors

## Strategy Features

### 1. Multi-Source Data Integration:
- **AkShare Financial Data**: Professional financial news and announcements
- **Professional Financial Websites**: 同花顺财经, 东方财富网, 雪球网, 新浪财经, 腾讯财经
- **FireCrawl Web Search**: General web search for additional information
- **Time Decay Weighting**: Recent information has higher weights in analysis

### 2. Enhanced Analysis Capabilities:
- **Comprehensive Data Collection**: Aggregates information from multiple authoritative sources
- **Source-Based Weighting**: Different data sources have different authority levels
- **Time Sensitivity**: Recent information is weighted more heavily
- **Detailed LLM Analysis**: Enhanced prompt engineering for more comprehensive analysis

### 3. Error Handling Mechanism:
- **LLM Retry Mechanism**: Up to 3 retries with exponential backoff for network timeouts
- Handles network request timeouts
- Provides fallback for LLM result parsing failures
- Ensures individual stock analysis errors don't affect processing of other stocks
- Graceful degradation when certain data sources are unavailable

### 4. Efficient Processing:
- **Smart Skipping**: Skips stocks that already have non-zero scores in the pool's pub field
- **No Automatic Database Saving**: Strategy only returns results; database saving is handled by the public opinion agent
- **Optimized Resource Usage**: Avoids redundant analysis of already scored stocks

### 5. Configurable Data Sources:
- Can enable/disable specific data sources based on requirements
- Flexible configuration for different market environments

## Integration with Public Opinion Agent

The strategy is designed to work with the Public Opinion Agent, which:
- Handles database operations for saving results
- Updates only the pub field in the pool collection
- Preserves all other stock data unchanged
- Updates the pub_at timestamp with the current execution time
- Only modifies stocks that were analyzed by the strategy

The enhanced strategy combines multiple authoritative data sources with advanced LLM analysis and robust error handling to provide more comprehensive and accurate decision-making basis for stock selection based on public sentiment.

