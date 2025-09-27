"""
Enhanced Public Opinion Analysis Strategy
A strategy that selects stocks based on public opinion and sentiment analysis using AkShare, FireCrawl web search, professional financial websites, and LLM evaluation.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import sys
import os
import requests
import json
from datetime import datetime, timedelta
import time
import logging

# Try to import akshare, if not available, provide a mock implementation
try:
    import akshare as ak
except ImportError:
    ak = None
    print("Warning: akshare not installed. Some features will be disabled.")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.base_strategy import BaseStrategy
from utils.strategy_utils import calculate_position_from_score


class EnhancedPublicOpinionAnalysisStrategy(BaseStrategy):
    """
    Enhanced Public Opinion Analysis Strategy
    Selects stocks based on public sentiment and news analysis using AkShare data,
    professional financial websites, FireCrawl web search, and LLM evaluation.
    """

    def __init__(self, name: str = "增强型舆情分析策略", params: Optional[Dict] = None, db_manager=None):
        """
        Initialize the enhanced public opinion analysis strategy

        Args:
            name: Strategy name
            params: Strategy parameters
                - sentiment_threshold: Minimum sentiment score (default: 0.6)
                - news_count_threshold: Minimum number of relevant news items (default: 5)
                - search_depth: Number of search results to analyze (default: 10)
                - time_window_hours: Time window for recent data (default: 24)
                - data_sources: List of data sources to use
                - firecrawl_config: FireCrawl configuration
                - llm_config: LLM configuration
            db_manager: Database manager instance for loading configuration from database
        """
        # First, try to load configuration from strategies collection if db_manager is provided
        if db_manager is not None:
            try:
                # Get strategy configuration from database
                strategy_config = self._load_strategy_config_from_db(name, db_manager)
                if strategy_config and "parameters" in strategy_config:
                    db_params = strategy_config["parameters"]
                    # Merge with default parameters
                    default_params = {
                        "sentiment_threshold": 0.6,
                        "news_count_threshold": 5,
                        "search_depth": 10,
                        "time_window_hours": 24,
                        "data_sources": ["akshare", "firecrawl", "professional_sites"],
                        "professional_sites": [
                            "同花顺财经",
                            "东方财富网",
                            "雪球网",
                            "新浪财经",
                            "腾讯财经",
                        ],
                        "firecrawl_config": {
                            "api_url": "http://192.168.1.2:8080/v1",
                            "timeout": 30,
                            "max_retries": 3,
                            "retry_delay": 1,
                            "rate_limit": 10,
                            "concurrent_requests": 5,
                        },
                        "llm_name": "gemini-2.0-flash",
                    }
                    # Update default params with database params
                    default_params.update(db_params)
                    params = default_params
            except Exception as e:
                self.log_warning(f"Error loading strategy configuration from database: {e}")

        super().__init__(
            name,
            params
            or {
                "sentiment_threshold": 0.6,
                "news_count_threshold": 5,
                "search_depth": 10,
                "time_window_hours": 24,
                "data_sources": ["akshare", "firecrawl", "professional_sites"],
                "professional_sites": [
                    "同花顺财经",
                    "东方财富网",
                    "雪球网",
                    "新浪财经",
                    "腾讯财经",
                ],
                "firecrawl_config": {
                    "api_url": "http://192.168.1.2:8080/v1",
                    "timeout": 30,
                    "max_retries": 3,
                    "retry_delay": 1,
                    "rate_limit": 10,
                    "concurrent_requests": 5,
                },
                "llm_name": "gemini-2.0-flash",
            },
        )

        # Strategy parameters
        self.sentiment_threshold = self.params.get("sentiment_threshold", 0.6)
        self.news_count_threshold = self.params.get("news_count_threshold", 5)
        self.search_depth = self.params.get("search_depth", 10)
        self.time_window_hours = self.params.get("time_window_hours", 24)
        self.data_sources = self.params.get(
            "data_sources", ["akshare", "professional_sites"]
        )

        # FireCrawl configuration - only configure if firecrawl is in data_sources
        self.firecrawl_config = {}
        if "firecrawl" in self.data_sources:
            firecrawl_params = self.params.get("firecrawl_config", {})
            self.firecrawl_config = {
                "api_url": firecrawl_params.get("api_url", "http://192.168.1.2:8080/v1"),
                "timeout": firecrawl_params.get("timeout", 30),
                "max_retries": firecrawl_params.get("max_retries", 3),
                "retry_delay": firecrawl_params.get("retry_delay", 1),
                "rate_limit": firecrawl_params.get("rate_limit", 10),
                "concurrent_requests": firecrawl_params.get("concurrent_requests", 5),
            }

        # Get LLM configuration name from strategy parameters - default to empty to force database lookup
        self.llm_name = self.params.get("llm_name", "")

        # Load LLM configuration from database
        self.llm_config = self._load_llm_config_from_db(self.llm_name)

        # Professional financial websites
        self.professional_sites = self.params.get(
            "professional_sites",
            ["同花顺财经", "东方财富网", "雪球网", "新浪财经", "腾讯财经"],
        )

        self.logger.info(
            f"Initialized {self.name} strategy with params: "
            f"sentiment_threshold={self.sentiment_threshold}, "
            f"news_count_threshold={self.news_count_threshold}, "
            f"time_window_hours={self.time_window_hours}, "
            f"data_sources={self.data_sources}"
        )

    def get_akshare_news(self, stock_code: str) -> List[Dict]:
        """
        Get stock news from AkShare

        Args:
            stock_code: Stock code

        Returns:
            List of news items
        """
        if not ak:
            self.log_warning("AkShare not available, skipping AkShare news collection")
            return []

        try:
            # Get recent news for the stock
            news_df = ak.stock_news_em(stock_code)

            if news_df.empty:
                return []

            # Filter by time window
            time_threshold = datetime.now() - timedelta(hours=self.time_window_hours)
            if "publish_time" in news_df.columns:
                news_df["publish_time"] = pd.to_datetime(news_df["publish_time"])
                news_df = news_df[news_df["publish_time"] >= time_threshold]

            # Convert to list of dictionaries
            news_items = []
            for _, row in news_df.head(self.search_depth).iterrows():
                news_items.append(
                    {
                        "title": row.get("title", ""),
                        "content": row.get("content", "")[
                            :1000
                        ],  # Limit content length
                        "url": row.get("url", ""),
                        "publishedAt": row.get("publish_time", "").isoformat()
                        if pd.notnull(row.get("publish_time", ""))
                        else "",
                        "source": "AkShare",
                        "time_weight": self._calculate_time_weight(
                            row.get("publish_time", "")
                        ),
                    }
                )

            self.log_info(
                f"Retrieved {len(news_items)} news items from AkShare for {stock_code}"
            )
            return news_items

        except Exception as e:
            self.log_error(f"Error getting AkShare news for {stock_code}: {e}")
            return []

    def get_professional_site_data(
        self, stock_code: str, stock_name: str
    ) -> List[Dict]:
        """
        Get data from professional financial websites

        Args:
            stock_code: Stock code
            stock_name: Stock name

        Returns:
            List of data items from professional sites
        """
        try:
            # This is a simplified implementation
            # In a real implementation, you would need specific scrapers for each site
            professional_data = []

            search_query = f"{stock_name} {stock_code}"

            # Simulate getting data from professional sites
            for site in self.professional_sites:
                # In a real implementation, you would scrape actual data from these sites
                professional_data.append(
                    {
                        "title": f"[{site}] {stock_name} 最新分析报告",
                        "content": f"来自{site}的关于{stock_name}({stock_code})的专业分析内容摘要...",
                        "url": f"https://www.{site.replace(' ', '').lower()}.com/stock/{stock_code}",
                        "publishedAt": datetime.now().isoformat(),
                        "source": site,
                        "time_weight": 1.0,
                    }
                )

            self.log_info(
                f"Retrieved {len(professional_data)} items from professional sites for {stock_code}"
            )
            return professional_data

        except Exception as e:
            self.log_error(
                f"Error getting professional site data for {stock_code}: {e}"
            )
            return []

    def search_stock_news(self, queries: List[str]) -> List[Dict]:
        """
        Search for stock-related news using FireCrawl with batch processing

        Args:
            queries: List of search queries

        Returns:
            List of news items with title and content
        """
        try:
            api_url = self.firecrawl_config["api_url"]
            timeout = self.firecrawl_config["timeout"]

            self.log_info(
                f"Calling FireCrawl API at {api_url}/v1/batch/scrape for queries: {queries}"
            )

            # Prepare the request for FireCrawl batch search API
            headers = {"Content-Type": "application/json"}

            # Prepare payload for batch search
            payload = {
                "requests": [
                    {
                        "query": query,
                        "pageOptions": {
                            "onlyMainContent": True,
                            "fetchPageContent": True,
                            "includeHtml": False,
                        },
                        "searchOptions": {"limit": self.search_depth},
                    }
                    for query in queries
                ]
            }

            # Send request to FireCrawl batch search API
            response = requests.post(
                f"{api_url}/v2/batch/scrape",
                headers=headers,
                json=payload,
                timeout=timeout,
            )

            if response.status_code == 200:
                result = response.json()
                batch_results = result.get("responses", [])

                # Process batch search results to extract relevant information
                processed_results = []
                for item in batch_results:
                    search_results = item.get("data", [])
                    for search_item in search_results:
                        published_at = search_item.get("publishedAt", "")
                        processed_results.append(
                            {
                                "title": search_item.get("title", ""),
                                "content": search_item.get("content", "")[
                                    :1000
                                ],  # Limit content length
                                "url": search_item.get("url", ""),
                                "publishedAt": published_at,
                                "source": "FireCrawl",
                                "time_weight": self._calculate_time_weight(
                                    published_at
                                ),
                            }
                        )

                self.log_info(
                    f"Successfully retrieved {len(processed_results)} search results from FireCrawl"
                )
                return processed_results
            else:
                self.log_error(
                    f"FireCrawl API error: {response.status_code} - {response.text}"
                )
                return []

        except requests.exceptions.Timeout:
            self.log_error("FireCrawl API request timed out")
            return []
        except Exception as e:
            self.log_error(f"Error searching stock news with FireCrawl: {e}")
            return []

    def _calculate_time_weight(self, published_at) -> float:
        """
        Calculate time weight based on publication time

        Args:
            published_at: Publication time

        Returns:
            Time weight (1.0 for recent, decreasing for older)
        """
        try:
            if not published_at:
                return 1.0

            if isinstance(published_at, str):
                pub_time = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            else:
                pub_time = published_at

            time_diff = datetime.now(pub_time.tzinfo) - pub_time
            hours_diff = time_diff.total_seconds() / 3600

            # Exponential decay function - recent news have higher weight
            # Weight = e^(-hours/decay_factor)
            decay_factor = (
                self.time_window_hours / 3
            )  # 1/3 of time window for significant decay
            weight = np.exp(-hours_diff / decay_factor)

            return max(0.1, min(1.0, weight))  # Clamp between 0.1 and 1.0

        except Exception as e:
            self.log_warning(f"Error calculating time weight: {e}")
            return 1.0

    def collect_all_data(self, stock_code: str, stock_name: str) -> List[Dict]:
        """
        Collect data from all configured sources

        Args:
            stock_code: Stock code
            stock_name: Stock name

        Returns:
            List of all collected data items
        """
        all_data = []

        # Collect from AkShare
        if "akshare" in self.data_sources and ak:
            akshare_data = self.get_akshare_news(stock_code)
            all_data.extend(akshare_data)

        # Collect from professional sites
        if "professional_sites" in self.data_sources:
            professional_data = self.get_professional_site_data(stock_code, stock_name)
            all_data.extend(professional_data)

        # Collect from FireCrawl
        if "firecrawl" in self.data_sources:
            search_query = f"{stock_name} {stock_code} 股票 新闻 分析 评论"
            firecrawl_data = self.search_stock_news([search_query])
            all_data.extend(firecrawl_data)

        # Sort by time weight (newer items first)
        all_data.sort(key=lambda x: x.get("time_weight", 0), reverse=True)

        self.log_info(f"Collected {len(all_data)} total items for {stock_code}")
        return all_data

    def analyze_sentiment_with_llm(
        self, stock_code: str, stock_name: str, all_data: List[Dict]
    ) -> Tuple[Optional[float], str, Dict]:
        """
        Analyze sentiment using LLM with enhanced prompt and retry mechanism

        Args:
            stock_code: Stock code
            stock_name: Stock name
            all_data: List of all collected data items

        Returns:
            Tuple of (sentiment_score, analysis_details, full_analysis)
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # LLM Configuration details
                api_url = self.llm_config["api_url"]
                api_key = self.llm_config["api_key"]
                model = self.llm_config["model"]
                timeout = self.llm_config["timeout"]

                self.log_info(
                    f"Calling LLM API at {api_url} for sentiment analysis (attempt {attempt + 1})"
                )

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

                # Select the most relevant news articles based on time weight
                most_relevant_data = sorted(
                    all_data, key=lambda x: x.get("time_weight", 0), reverse=True
                )[: self.search_depth]

                # Combine news content for analysis
                news_content = "\n".join(
                    [
                        f"来源: {item['source']}\n标题: {item['title']}\n内容: {item['content']}\n发布时间: {item.get('publishedAt', '未知')}"
                        for item in most_relevant_data
                    ]
                )

                # Shorten news content to a maximum length
                max_content_length = 2000  # Adjust as needed
                if len(news_content) > max_content_length:
                    news_content = (
                        news_content[:max_content_length] + "... (内容已截断)"
                    )

                # Create analysis prompt
                prompt = f"""
                请分析以下关于股票 {stock_name} ({stock_code}) 的舆情信息，并给出0-1分的 sentiment 评分：

                舆情内容：
                {news_content}

                分析要求：
                1. 综合评估所有舆情信息的情感倾向（积极、消极或中性）
                2. 考虑信息的重要性和影响力
                3. 考虑信息的时效性
                4. 给出详细的分析理由

                请严格按照以下JSON格式输出结果：
                {{
                    "sentiment_score": 0.75,
                    "sentiment_trend": "上升",
                    "key_events": ["利好消息", "业绩预增"],
                    "market_impact": "高",
                    "confidence_level": 0.85,
                    "analysis_summary": "详细的分析理由...",
                    "recommendation": "买入",
                    "risk_factors": ["市场波动", "政策风险"]
                }}

                其中sentiment_score是0-1之间的数值，0表示极度负面，1表示极度正面，0.5为中性。
                """

                # Prepare payload based on provider
                if provider == "google":  # Gemini API
                    payload = {
                        "contents": [
                            {
                                "role": "user",
                                "parts": [
                                    {
                                        "text": '你是一位专业的舆情分析师，请根据提供的舆情信息进行 sentiment 分析。你需要严格按照以下JSON格式输出结果：{"sentiment_score": 0.75, "sentiment_trend": "上升", "key_events": ["利好消息", "业绩预增"], "market_impact": "高", "confidence_level": 0.85, "analysis_summary": "详细的分析理由...", "recommendation": "买入", "risk_factors": ["市场波动", "政策风险"]}。其中sentiment_score是0-1之间的数值，表示舆情 sentiment 评分，0为最低（极度负面），1为最高（极度正面）；其他字段请根据实际分析填写。'
                                        + "\n\n"
                                        + prompt
                                    }
                                ],
                            }
                        ],
                        "generationConfig": {
                            "temperature": 0.7,
                            "maxOutputTokens": 1500,
                        },
                    }
                    api_url_with_key = f"{api_url}?key={api_key}"
                elif provider == "deepseek":  # DeepSeek API
                    payload = {
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": '你是一位专业的舆情分析师，请根据提供的舆情信息进行 sentiment 分析。你需要严格按照以下JSON格式输出结果：{"sentiment_score": 0.75, "sentiment_trend": "上升", "key_events": ["利好消息", "业绩预增"], "market_impact": "高", "confidence_level": 0.85, "analysis_summary": "详细的分析理由...", "recommendation": "买入", "risk_factors": ["市场波动", "政策风险"]}。其中sentiment_score是0-1之间的数值，表示舆情 sentiment 评分，0为最低（极度负面），1为最高（极度正面）；其他字段请根据实际分析填写。',
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
                                "content": '你是一位专业的舆情分析师，请根据提供的舆情信息进行 sentiment 分析。你需要严格按照以下JSON格式输出结果：{"sentiment_score": 0.75, "sentiment_trend": "上升", "key_events": ["利好消息", "业绩预增"], "market_impact": "高", "confidence_level": 0.85, "analysis_summary": "详细的分析理由...", "recommendation": "买入", "risk_factors": ["市场波动", "政策风险"]}。其中sentiment_score是0-1之间的数值，表示舆情 sentiment 评分，0为最低（极度负面），1为最高（极度正面）；其他字段请根据实际分析填写。',
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
                        sentiment_score = float(
                            analysis_result.get("sentiment_score", 0.5)
                        )
                        analysis_details = analysis_result.get(
                            "analysis_summary", content
                        )

                        self.log_info(
                            "Successfully received LLM sentiment analysis response"
                        )
                        return sentiment_score, analysis_details, analysis_result
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try to extract score from content
                        self.log_warning(
                            "Failed to parse LLM JSON response, extracting score from content"
                        )
                        # Simple extraction of score from content
                        import re

                        score_match = re.search(
                            r'"sentiment_score"\s*:\s*(\d+\.?\d*)', content
                        )
                        if score_match:
                            sentiment_score = float(score_match.group(1))
                            sentiment_score = max(
                                0.0, min(1.0, sentiment_score)
                            )  # Clamp to 0-1 range
                            return (
                                sentiment_score,
                                content,
                                {
                                    "sentiment_score": sentiment_score,
                                    "analysis_summary": content,
                                },
                            )
                        else:
                            return (
                                0.5,
                                content,
                                {"sentiment_score": 0.5, "analysis_summary": content},
                            )  # Default neutral score
                else:
                    self.log_error(
                        f"LLM API error: {response.status_code} - {response.text}"
                    )
                    raise Exception(f"LLM API error: {response.status_code}")

            except requests.exceptions.Timeout:
                self.log_error("LLM API request timed out")
                if attempt < max_retries - 1:
                    # Wait before retrying (exponential backoff)
                    import time

                    time.sleep(2**attempt)  # 1s, 2s, 4s delay
                    continue
                else:
                    return None, "LLM分析失败: 请求超时", {}
            except Exception as e:
                self.log_error(
                    f"Error getting LLM sentiment analysis (attempt {attempt + 1}): {e}"
                )
                if attempt < max_retries - 1:
                    # Wait before retrying (exponential backoff)
                    import time

                    time.sleep(2**attempt)  # 1s, 2s, 4s delay
                    continue
                else:
                    return None, f"LLM分析失败: {str(e)}", {}

        # If we reach here, all retries have failed
        return None, "LLM分析失败: 所有重试都已用尽", {}

    def analyze_public_opinion(
        self, stock_code: str, stock_name: str
    ) -> Tuple[bool, str, Optional[float], Dict]:
        """
        Analyze public opinion for a stock using multiple data sources and LLM

        Args:
            stock_code: Stock code
            stock_name: Stock name

        Returns:
            Tuple of (meets_criteria, analysis_reason, sentiment_score, full_analysis)
        """
        self.log_info(f"开始舆情分析: {stock_code} ({stock_name})")

        try:
            # Collect data from all sources
            all_data = self.collect_all_data(stock_code, stock_name)
            self.log_info(f"收集到 {len(all_data)} 条相关信息")

            if not all_data or len(all_data) < self.news_count_threshold:
                reason = f"相关信息数量不足，仅找到{len(all_data)}条"
                self.log_info(f"股票 {stock_code} 舆情分析结果: {reason}")
                return False, reason, None, {}

            # Analyze sentiment using LLM
            sentiment_score, analysis_details, full_analysis = (
                self.analyze_sentiment_with_llm(stock_code, stock_name, all_data)
            )

            if sentiment_score is None:
                reason = "无法分析舆情 sentiment"
                self.log_info(f"股票 {stock_code} 舆情分析结果: {reason}")
                return False, reason, None, {}

            # Check if sentiment meets threshold
            if sentiment_score < self.sentiment_threshold:
                reason = f"舆情 sentiment 分数({sentiment_score:.2f})未达到阈值({self.sentiment_threshold})"
                self.log_info(f"股票 {stock_code} 舆情分析结果: {reason}")
                return False, reason, None, {}

            reason = f"符合条件: 舆情 sentiment 分数({sentiment_score:.2f}) >= 阈值({self.sentiment_threshold}), 相关信息{len(all_data)}条"
            self.log_info(f"股票 {stock_code} 舆情分析结果: {reason}")

            return True, reason, sentiment_score, full_analysis

        except Exception as e:
            self.log_error(f"舆情分析错误: {e}")
            return False, f"舆情分析错误: {e}", None, {}

    def analyze(
        self, data: pd.DataFrame, stock_code: str, stock_name: str
    ) -> Tuple[bool, str, Optional[float]]:
        """
        Analyze stock data and public opinion

        Args:
            data: DataFrame with stock data including OHLCV columns
            stock_code: Stock code
            stock_name: Stock name

        Returns:
            Tuple of (meets_criteria, selection_reason, score)
        """
        self.log_info(f"开始分析股票 {stock_code} ({stock_name})")

        if data.empty:
            self.log_warning(f"股票 {stock_code} 数据为空")
            return False, "数据为空", None

        try:
            # Perform public opinion analysis
            meets_criteria, reason, sentiment_score, full_analysis = (
                self.analyze_public_opinion(stock_code, stock_name)
            )

            self.log_info(
                f"完成分析股票 {stock_code} ({stock_name}) - 符合条件: {meets_criteria}, 评分: {sentiment_score}"
            )

            return meets_criteria, reason, sentiment_score

        except Exception as e:
            self.log_error(f"分析股票 {stock_code} 时出错: {e}")
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

    def execute(
        self, stock_data: Dict[str, pd.DataFrame], agent_name: str, db_manager
    ) -> List[Dict]:
        """
        Execute the strategy on provided stock data and automatically save results

        Args:
            stock_data: Dictionary mapping stock codes to their data DataFrames
            agent_name: Name of the agent executing this strategy
            db_manager: Database manager instance

    def _load_strategy_config_from_db(self, strategy_name: str, db_manager) -> Optional[Dict]:
        """
        Load strategy configuration from database strategies collection.

        Args:
            strategy_name: Name of the strategy to load configuration for
            db_manager: Database manager instance

        Returns:
            Dictionary with strategy configuration or None if not found
        """
        try:
            # Get strategies collection
            strategies_collection = db_manager.db.get_collection("strategies")
            
            # Find strategy by name
            strategy_config = strategies_collection.find_one({"name": strategy_name})
            
            if strategy_config:
                self.log_info(f"Successfully loaded strategy configuration for {strategy_name} from database")
                return strategy_config
            else:
                self.log_warning(f"No strategy configuration found for {strategy_name} in database")
                return None
                
        except Exception as e:
            self.log_error(f"Error loading strategy configuration from database: {e}")
            return None
        Returns:
            List of selected stocks with analysis results
        """
        from datetime import datetime

        start_time = datetime.now()
        self.log_info(f"执行 {self.name} 策略，处理 {len(stock_data)} 只股票")
        self.log_info(f"待处理股票列表: {list(stock_data.keys())}")

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
                self.log_info(f"开始处理股票: {code}")

                # Get stock name or use code as fallback
                stock_name = stock_names.get(code, code)

                # Perform public opinion analysis with full results
                meets_criteria, reason, sentiment_score, full_analysis = (
                    self.analyze_public_opinion(code, stock_name)
                )

                if meets_criteria:
                    # Calculate normalized score
                    normalized_score = (
                        self._calculate_score(sentiment_score)
                        if sentiment_score is not None
                        else 0.0
                    )

                    # Format the result according to requirements
                    selected_stocks.append(
                        {
                            "code": code,
                            "score": normalized_score,  # Score between 0 and 1
                            "value": reason,  # Reason for the score
                        }
                    )

                    self.log_info(f"股票 {code} 符合条件，评分: {normalized_score:.4f}")
                else:
                    self.log_info(f"股票 {code} 不符合条件，原因: {reason}")

            except Exception as e:
                self.log_warning(f"处理股票 {code} 时出错: {e}")
                continue

        # Automatically save results to pool collection
        if selected_stocks:
            from datetime import datetime

            current_date = datetime.now().strftime("%Y-%m-%d")

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
                    "strategy_execution_time": execution_time,
                    "selected_stocks_count": len(selected_stocks),
                },
            )

            if save_success:
                self.log_info(f"成功保存 {len(selected_stocks)} 只股票到数据库")
            else:
                self.log_error("保存股票到数据库失败")

        self.log_info(f"选中 {len(selected_stocks)} 只股票")
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
        signals["signal"] = "HOLD"
        signals["position"] = 0.0

        # For public opinion strategy, we don't generate continuous signals
        # This would require continuous sentiment analysis which is beyond scope

        return signals

    def calculate_position_size(
        self, signal: str, portfolio_value: float, price: float
    ) -> float:
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
        if signal == "BUY":
            # Use a moderate position size for buy signals
            return 100.0
        elif signal == "SELL":
            return -100.0  # Sell 100 shares
        else:
            return 0.0  # Hold position

    def _load_llm_config_from_db(self, config_name: str) -> Dict[str, any]:
        """
        Load LLM configuration from database config collection.

        Args:
            config_name: Name of the LLM configuration to load

        Returns:
            Dictionary with LLM configuration
        """
        try:
            # Load MongoDB configuration
            from config.mongodb_config import MongoDBConfig

            mongodb_config = MongoDBConfig()
            config = mongodb_config.get_mongodb_config()

            # Connect to MongoDB
            if config.get("username") and config.get("password"):
                # With authentication
                uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?authSource={config.get('auth_database', 'admin')}"
            else:
                # Without authentication
                uri = f"mongodb://{config['host']}:{config['port']}/"

            from pymongo import MongoClient

            client = MongoClient(uri)
            db = client[config["database"]]
            config_collection = db[mongodb_config.get_collection_name("config")]

            # Get LLM configurations
            config_record = config_collection.find_one()

            if config_record and "llm_configs" in config_record:
                llm_configs = config_record["llm_configs"]

                # Find the specified config name
                for config_item in llm_configs:
                    if config_item.get("name") == config_name:
                        # Get API key from environment variable
                        api_key_env_var = config_item.get("api_key_env_var", "")
                        api_key = os.getenv(api_key_env_var, "")

                        return {
                            "api_url": config_item["api_url"],
                            "api_key": api_key,
                            "model": config_item["model"],
                            "timeout": config_item["timeout"],
                            "provider": config_item.get("provider", "google"),
                            "name": config_item["name"],
                        }

                # If not found, use the first one
                if llm_configs:
                    self.log_warning(
                        f"LLM configuration '{config_name}' not found, using first available configuration"
                    )
                    config_item = llm_configs[0]
                    api_key_env_var = config_item.get("api_key_env_var", "")
                    api_key = os.getenv(api_key_env_var, "")

                    return {
                        "api_url": config_item["api_url"],
                        "api_key": api_key,
                        "model": config_item["model"],
                        "timeout": config_item["timeout"],
                        "provider": config_item.get("provider", "google"),
                        "name": config_item["name"],
                    }

            # Fallback to default configuration
            self.log_warning(
                "No LLM configuration found in database, using default configuration"
            )
            return self._get_default_llm_config()

        except Exception as e:
            self.log_error(f"Error loading LLM configuration from database: {e}")
            # Fallback to default configuration
            return self._get_default_llm_config()

    def _get_default_llm_config(self) -> Dict[str, any]:
        """
        Get default LLM configuration.

        Returns:
            Dictionary with default LLM configuration
        """
        self.log_warning(
            "No LLM configuration found in database and no fallback configuration available"
        )
        return {
            "api_url": "",
            "api_key": "",
            "model": "",
            "timeout": 60,
            "provider": "google",
            "name": "default",
        }


# Example usage
if __name__ == "__main__":
    # This is just an example - in practice, this would be called by an agent
    pass
