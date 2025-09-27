# Public Opinion Analysis Strategy Documentation

## Overview

The Public Opinion Analysis Strategy is a stock selection strategy that leverages public sentiment and news analysis to identify potentially favorable investment opportunities. It uses FireCrawl for web search and LLM (Large Language Model) evaluation to assess public opinion about stocks.

There are two versions of this strategy:
1. **PublicOpinionAnalysisStrategy**: The original strategy that uses FireCrawl for web search
2. **EnhancedPublicOpinionAnalysisStrategyV2**: An enhanced version with additional data sources including AkShare and Eastmoney Guba

## Strategy Structure

### Class Inheritance
- `PublicOpinionAnalysisStrategy` inherits from `BaseStrategy` base class
- Follows the unified interface and specifications of other strategies in the system

### Core Components

#### Initialization Method
- `__init__`: Initializes strategy parameters and configurations
  - Strategy parameters: sentiment threshold, news count threshold, search depth
  - FireCrawl configuration: API address, timeout
  - LLM configuration: API address, API key (read from environment variables), model, timeout

#### Core Analysis Methods
- `search_stock_news`: Uses FireCrawl to search for stock-related news
- `analyze_sentiment_with_llm`: Uses LLM to analyze news sentiment and provide a 0-1 score
- `analyze_public_opinion`: Integrates news search and sentiment analysis processes
- `analyze`: Main analysis method that calls `analyze_public_opinion`
- `_calculate_score`: Normalizes the sentiment score
- `execute`: Main strategy execution method that processes multiple stocks and automatically saves results
- `generate_signals`: Generates trading signals (not actually used in this strategy)
- `calculate_position_size`: Calculates position size (uses fixed values in this strategy)

## Execution Logic

### 1. Initialization Phase
1. Set strategy parameters:
   - `sentiment_threshold`: Sentiment score threshold, default 0.6
   - `news_count_threshold`: Minimum number of relevant news items, default 3
   - `search_depth`: Search result analysis depth, default 5
2. Configure FireCrawl and LLM service connection parameters

### 2. Execution Phase
When the strategy is executed, the process flows as follows:

1. **Batch Processing of Stock Data**:
   - Iterate through the provided stock data dictionary
   - Retrieve stock names from the database (if available)

2. **Individual Stock Analysis Process**:
   - Call the `analyze` method to begin analysis
   - Within `analyze`, call the `analyze_public_opinion` method

3. **Core Public Opinion Analysis Process**:
   - Construct search query terms (stock name + code + keywords)
   - Call `search_stock_news` method to search for relevant news via FireCrawl
   - Check if the number of search results meets the threshold requirements
   - Call `analyze_sentiment_with_llm` method to analyze news sentiment
   - Check if the sentiment score meets the threshold requirements

4. **LLM Sentiment Analysis Process**:
   - Consolidate the searched news content
   - Construct analysis prompts, requiring the LLM to output results in a specified JSON format
   - Send request to LLM API
   - Parse the LLM response and extract sentiment scores and analysis details
   - Handle JSON parsing failures with fallback regex extraction

5. **Result Processing**:
   - Calculate normalized scores for stocks that meet the criteria
   - Calculate position sizes
   - Construct result data structures

6. **Result Saving**:
   - Save selected stocks to the database pool
   - Record execution time and other metadata

### 3. Output Results
After strategy execution, it returns a list of qualifying stocks, each containing:
- Stock code
- Selection reason
- Normalized score (between 0-1)
- Position size
- Strategy name
- Public opinion analysis details (sentiment score and analysis rationale)

## Strategy Features

### 1. External Service Dependencies:
- Depends on FireCrawl for web search
- Depends on LLM service for sentiment analysis
- Flexible configuration supporting different API addresses and models

### 2. Dual Threshold Screening Mechanism:
- News count threshold: Ensures sufficient news for analysis
- Sentiment score threshold: Ensures public sentiment positivity meets requirements

### 3. Error Handling Mechanism:
- Handles network request timeouts
- Provides fallback for LLM result parsing failures
- Ensures individual stock analysis errors don't affect processing of other stocks

### 4. Automatic Saving Mechanism:
- Automatically saves results to the database after strategy execution
- Records execution time and other metadata information

The strategy combines web sentiment search with large language model analysis to provide decision-making basis for stock selection based on public sentiment.

