"""
Public Opinion Analysis Strategy
A strategy that selects stocks based on public opinion and sentiment analysis using FireCrawl web search and LLM evaluation.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import sys
import os
import requests
import json
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.base_strategy import BaseStrategy
from utils.strategy_utils import calculate_position_from_score

class PublicOpinionAnalysisStrategy(BaseStrategy):
    """
    Public Opinion Analysis Strategy
    Selects stocks based on public sentiment and news analysis using FireCrawl web search and LLM evaluation.
    """

    def __init__(self, name: str = "舆情分析策略", params: Optional[Dict] = None):
        """
        Initialize the public opinion analysis strategy

        Args:
            name: Strategy name
            params: Strategy parameters
                - llm_name: Name of the LLM configuration to use from database
                - sentiment_threshold: Minimum sentiment score (default: 0.6)
                - news_count_threshold: Minimum number of relevant news items (default: 3)
                - search_depth: Number of search results to analyze (default: 5)
                - firecrawl_config: FireCrawl configuration
        """
        super().__init__(name, params or {
            'llm_name': 'gemini-2.0-flash',
            'sentiment_threshold': 0.6,
            'news_count_threshold': 3,
            'search_depth': 5,
            'firecrawl_config': {
                'api_url': 'http://192.168.1.2:8080/v1',
                'timeout': 30
            }
        })

        # Strategy parameters
        self.sentiment_threshold = self.params.get('sentiment_threshold', 0.6)
        self.news_count_threshold = self.params.get('news_count_threshold', 3)
        self.search_depth = self.params.get('search_depth', 5)

        # Get LLM configuration name from strategy parameters
        llm_config_name = self.params.get('llm_name', 'gemini-2.0-flash')

        # Load LLM configuration from database
        self.llm_config = self._load_llm_config_from_db(llm_config_name)

        # FireCrawl configuration
        firecrawl_params = self.params.get('firecrawl_config', {})
        self.firecrawl_config = {
            'api_url': firecrawl_params.get('api_url', 'http://192.168.1.2:8080/v1'),
            'timeout': firecrawl_params.get('timeout', 30)
        }

        self.logger.info(f"Initialized {self.name} strategy with params: "
                        f"sentiment_threshold={self.sentiment_threshold}, "
                        f"news_count_threshold={self.news_count_threshold}, "
                        f"firecrawl_api={self.firecrawl_config['api_url']}, "
                        f"llm_api={self.llm_config['api_url']}")

    def search_stock_news(self, query: str) -> List[Dict]:
        """
        Search for stock-related news using FireCrawl

        Args:
            query: Search query

        Returns:
            List of news items with title and content
        """
        try:
            api_url = self.firecrawl_config['api_url']
            timeout = self.firecrawl_config['timeout']

            self.log_info(f"Calling FireCrawl API at {api_url} for query: {query}")

            # Prepare the request for FireCrawl search API
            headers = {"Content-Type": "application/json"}

            # Prepare payload for search
            payload = {
                "query": query,
                "pageOptions": {
                    "onlyMainContent": True,
                    "fetchPageContent": True,
                    "includeHtml": False
                },
                "searchOptions": {
                    "limit": self.search_depth
                }
            }

            # Send request to FireCrawl search API
            response = requests.post(
                f"{api_url}/search",
                headers=headers,
                json=payload,
                timeout=timeout
            )

            if response.status_code == 200:
                result = response.json()
                search_results = result.get("data", [])

                # Process search results to extract relevant information
                processed_results = []
                for item in search_results:
                    processed_results.append({
                        "title": item.get("title", ""),
                        "content": item.get("content", "")[:1000],  # Limit content length
                        "url": item.get("url", ""),
                        "publishedAt": item.get("publishedAt", "")
                    })

                self.log_info(f"Successfully retrieved {len(processed_results)} search results")
                return processed_results
            else:
                self.log_error(f"FireCrawl API error: {response.status_code} - {response.text}")
                return []

        except requests.exceptions.Timeout:
            self.log_error("FireCrawl API request timed out")
            return []
        except Exception as e:
            self.log_error(f"Error searching stock news: {e}")
            return []

    def analyze_sentiment_with_llm(self, stock_code: str, stock_name: str, news_items: List[Dict]) -> Tuple[Optional[float], str]:
        """
        Analyze sentiment using LLM

        Args:
            stock_code: Stock code
            stock_name: Stock name
            news_items: List of news items

        Returns:
            Tuple of (sentiment_score, analysis_details)
        """
        try:
            # LLM Configuration details
            api_url = self.llm_config["api_url"]
            api_key = self.llm_config["api_key"]
            model = self.llm_config["model"]
            timeout = self.llm_config["timeout"]

            self.log_info(f"Calling LLM API at {api_url} for sentiment analysis")

            # Prepare the request for LLM API
            headers = {"Content-Type": "application/json"}

            # Prepare payload based on provider
            provider = self.llm_config.get("provider", "google")

            # Add authorization header if API key is provided
            if api_key:
                if provider == "deepseek":
                    headers["Authorization"] = f"Bearer {api_key}"
                else:
                    # For Google Gemini, API key is in query parameter
                    pass

            # Combine news content for analysis
            news_content = "\n".join([
                f"标题: {item['title']}\n内容: {item['content']}\n发布时间: {item.get('publishedAt', '未知')}"
                for item in news_items[:self.search_depth]
            ])

            # Create analysis prompt
            prompt = f"""
            请分析以下关于股票 {stock_name} ({stock_code}) 的新闻舆情，并给出0-1分的 sentiment 评分：

            新闻内容：
            {news_content}

            分析要求：
            1. 综合评估所有新闻的情感倾向（积极、消极或中性）
            2. 考虑新闻的重要性和影响力
            3. 考虑新闻的时效性
            4. 给出详细的分析理由

            请严格按照以下JSON格式输出结果：
            {{
                "score": 0.75,
                "value": "详细的分析理由..."
            }}

            其中score是0-1之间的数值，0表示极度负面，1表示极度正面，0.5为中性。
            value是详细的分析理由。
            """

            # Prepare payload based on provider
            if provider == "google":  # Gemini API
                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "text": '你是一位专业的舆情分析师，请根据提供的新闻信息进行舆情 sentiment 分析。你需要严格按照以下JSON格式输出结果：{"score": 0.75, "value": "详细的分析理由..."}。其中score是0-1之间的数值，表示舆情 sentiment 评分，0为最低（极度负面），1为最高（极度正面）；value是详细的分析理由。' + '\n\n' + prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1500,
                    }
                }
                api_url_with_key = f"{api_url}?key={api_key}"
            elif provider == "deepseek":  # DeepSeek API
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": '你是一位专业的舆情分析师，请根据提供的新闻信息进行舆情 sentiment 分析。你需要严格按照以下JSON格式输出结果：{"score": 0.75, "value": "详细的分析理由..."}。其中score是0-1之间的数值，表示舆情 sentiment 评分，0为最低（极度负面），1为最高（极度正面）；value是详细的分析理由。',
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1500,
                }
                api_url_with_key = api_url
            else:
                # Default to DeepSeek format for backward compatibility
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": '你是一位专业的舆情分析师，请根据提供的新闻信息进行舆情 sentiment 分析。你需要严格按照以下JSON格式输出结果：{"score": 0.75, "value": "详细的分析理由..."}。其中score是0-1之间的数值，表示舆情 sentiment 评分，0为最低（极度负面），1为最高（极度正面）；value是详细的分析理由。',
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1500,
                }
                api_url_with_key = api_url

            # Send request to LLM API
            if provider == "google":
                response = requests.post(
                    api_url_with_key,
                    headers=headers,
                    json=payload,
                    timeout=timeout,
                )
            else:
                response = requests.post(
                    api_url_with_key,
                    headers=headers,
                    json=payload,
                    timeout=timeout,
                )

            if response.status_code == 200:
                result = response.json()

                # Extract content based on provider
                if provider == "google":
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                else:  # Default to DeepSeek format
                    content = (
                        result.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "{}")
                    )

                # Try to parse the JSON response
                try:
                    # Handle case where response is wrapped in a code block
                    if content.startswith("```json"):
                        # Extract JSON from code block
                        content = content[7:]  # Remove ```json
                        if content.endswith("```"):
                            content = content[:-3]  # Remove ```

                    # Also handle case where response is wrapped in just ```
                    elif content.startswith("```"):
                        # Extract content from code block
                        content = content[3:]  # Remove ```
                        if content.endswith("```"):
                            content = content[:-3]  # Remove ```

                    analysis_result = json.loads(content)
                    sentiment_score = float(analysis_result.get("score", 0.5))
                    analysis_details = analysis_result.get("value", content)

                    self.log_info("Successfully received LLM sentiment analysis response")
                    return sentiment_score, analysis_details
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract score from content
                    self.log_warning("Failed to parse LLM JSON response, extracting score from content")
                    # Simple extraction of score from content
                    import re
                    score_match = re.search(r'"score"\s*:\s*(\d+\.?\d*)', content)
                    if score_match:
                        sentiment_score = float(score_match.group(1))
                        sentiment_score = max(0.0, min(1.0, sentiment_score))  # Clamp to 0-1 range
                        return sentiment_score, content
                    else:
                        return 0.5, content  # Default neutral score
            else:
                self.log_error(f"LLM API error: {response.status_code} - {response.text}")
                return None, f"LLM分析失败: HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            self.log_error("LLM API request timed out")
            return None, "LLM分析失败: 请求超时"
        except Exception as e:
            self.log_error(f"Error getting LLM sentiment analysis: {e}")
            return None, f"LLM分析失败: {str(e)}"
        except Exception as e:
            self.log_error(f"Error getting LLM sentiment analysis: {e}")
            return None, f"LLM分析失败: {str(e)}"

    def analyze_public_opinion(self, stock_code: str, stock_name: str) -> Tuple[bool, str, Optional[float]]:
        """
        Analyze public opinion for a stock using FireCrawl and LLM

        Args:
            stock_code: Stock code
            stock_name: Stock name

        Returns:
            Tuple of (meets_criteria, analysis_reason, sentiment_score)
        """
        try:
            # Search for stock-related news and information
            search_query = f"{stock_name} {stock_code} 股票 新闻 分析 评论"
            search_results = self.search_stock_news(search_query)

            if not search_results or len(search_results) < self.news_count_threshold:
                return False, f"相关新闻数量不足，仅找到{len(search_results)}条", None

            # Analyze sentiment using LLM
            sentiment_score, analysis_details = self.analyze_sentiment_with_llm(
                stock_code, stock_name, search_results
            )

            if sentiment_score is None:
                return False, "无法分析舆情 sentiment", None

            # Check if sentiment meets threshold
            if sentiment_score < self.sentiment_threshold:
                return False, f"舆情 sentiment 分数({sentiment_score:.2f})未达到阈值({self.sentiment_threshold})", None

            reason = f"符合条件: 舆情 sentiment 分数({sentiment_score:.2f}) >= 阈值({self.sentiment_threshold}), 相关新闻{len(search_results)}条"

            return True, reason, sentiment_score

        except Exception as e:
            self.log_error(f"舆情分析错误: {e}")
            return False, f"舆情分析错误: {e}", None

    def analyze(self, data: pd.DataFrame, stock_code: str, stock_name: str) -> Tuple[bool, str, Optional[float]]:
        """
        Analyze stock data and public opinion

        Args:
            data: DataFrame with stock data including OHLCV columns
            stock_code: Stock code
            stock_name: Stock name

        Returns:
            Tuple of (meets_criteria, selection_reason, score)
        """
        if data.empty:
            return False, "数据为空", None

        try:
            # Perform public opinion analysis
            meets_criteria, reason, sentiment_score = self.analyze_public_opinion(stock_code, stock_name)

            return meets_criteria, reason, sentiment_score

        except Exception as e:
            self.log_error(f"分析错误: {e}")
            return False, f"分析错误: {e}", None

    def _calculate_score(self, sentiment_score: float) -> float:
        """
        Calculate selection score based on sentiment

        Args:
            sentiment_score: Sentiment score from LLM analysis

        Returns:
            Normalized score between 0 and 1
        """
        try:
            # For public opinion strategy, sentiment score is already normalized
            return max(0.0, min(1.0, sentiment_score))

        except Exception as e:
            self.log_warning(f"计算分数时出错: {e}")
            return 0.0

    def execute(self, stock_data: Dict[str, pd.DataFrame],
                agent_name: str, db_manager) -> List[Dict]:
        """
        Execute the strategy on provided stock data and automatically save results

        Args:
            stock_data: Dictionary mapping stock codes to their data DataFrames
            agent_name: Name of the agent executing this strategy
            db_manager: Database manager instance

        Returns:
            List of selected stocks with analysis results
        """
        from datetime import datetime
        start_time = datetime.now()
        self.log_info(f"执行 {self.name} 策略，处理 {len(stock_data)} 只股票")

        selected_stocks = []

        # Get stock names from database if available
        stock_names = {}
        try:
            if db_manager:
                # Try to get stock names from a stocks collection or similar
                stocks_collection = db_manager.db.get_collection("stocks", None)
                if stocks_collection is not None:
                    for code in stock_data.keys():
                        stock_record = stocks_collection.find_one({"code": code})
                        if stock_record and "name" in stock_record:
                            stock_names[code] = stock_record["name"]
        except Exception as e:
            self.log_warning(f"获取股票名称时出错: {e}")

        # Analyze each stock
        for code, data in stock_data.items():
            try:
                # Get stock name or use code as fallback
                stock_name = stock_names.get(code, code)

                meets_criteria, reason, sentiment_score = self.analyze(data, code, stock_name)

                if meets_criteria:
                    # Calculate normalized score
                    normalized_score = self._calculate_score(sentiment_score) if sentiment_score is not None else 0.0

                    # Add public opinion analysis data
                    public_opinion_analysis = {
                        'sentiment_score': float(sentiment_score) if sentiment_score is not None else 0.0,
                        'analysis_reason': reason
                    }

                    # Calculate position based on score
                    position = calculate_position_from_score(normalized_score)

                    selected_stocks.append({
                        'code': code,
                        'selection_reason': reason,
                        'score': normalized_score,
                        'position': position,  # Add position field based on score
                        'strategy_name': self.name,  # Add strategy name
                        'public_opinion_analysis': public_opinion_analysis
                    })

            except Exception as e:
                self.log_warning(f"处理股票 {code} 时出错: {e}")
                continue

        self.log_info(f"选中 {len(selected_stocks)} 只股票")

        # Automatically save results to pool collection
        if selected_stocks:
            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')

            # 记录策略运行结束时间
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            save_success = self.save_to_pool(
                db_manager=db_manager,
                agent_name=agent_name,
                stocks=selected_stocks,
                date=current_date,
                strategy_params=self.params,
                additional_metadata={
                    'strategy_execution_time': execution_time,
                    'selected_stocks_count': len(selected_stocks)
                }
            )

            if save_success:
                self.log_info("策略结果已自动保存到池中")
            else:
                self.log_error("保存策略结果到池中失败")

        return selected_stocks

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on input data.

        Args:
            data: Input data DataFrame with required columns

        Returns:
            DataFrame with signals
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 'HOLD'
        signals['position'] = 0.0

        # For public opinion strategy, we don't generate continuous signals
        # This would require continuous sentiment analysis which is beyond scope

        return signals

    def calculate_position_size(self, signal: str, portfolio_value: float,
                              price: float) -> float:
        """
        Calculate position size based on signal and portfolio value.

        Args:
            signal: Trading signal ('BUY', 'SELL', 'HOLD')
            portfolio_value: Current portfolio value
            price: Current asset price

        Returns:
            Position size (number of shares/contracts)
        """
        # For this strategy, we'll use a fixed position size based on signal strength
        if signal == 'BUY':
            # Use a moderate position size for buy signals
            return 100.0
        elif signal == 'SELL':
            return -100.0  # Sell 100 shares
        else:
            return 0.0  # Hold position

# Example usage
if __name__ == "__main__":
    # This is just an example - in practice, this would be called by an agent
    pass

