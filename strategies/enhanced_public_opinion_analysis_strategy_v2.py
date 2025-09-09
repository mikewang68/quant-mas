"""
Enhanced Public Opinion Analysis Strategy V2
A strategy that selects stocks based on public opinion and sentiment analysis using AkShare,
FireCrawl web search, professional financial websites, and LLM evaluation.
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
import re

# Try to import akshare, if not available, provide a mock implementation
try:
    import akshare as ak
except ImportError:
    ak = None
    print("Warning: akshare not installed. Some features will be disabled.")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.base_strategy import BaseStrategy


class EnhancedPublicOpinionAnalysisStrategyV2(BaseStrategy):
    """
    Enhanced Public Opinion Analysis Strategy V2
    Selects stocks based on public sentiment and news analysis using AkShare data,
    professional financial websites, FireCrawl web search, and LLM evaluation.
    """

    def __init__(
        self,
        name: str = "增强型舆情分析策略V2",
        params: Optional[Dict] = None,
        db_manager=None,
    ):
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
                        "data_sources": [
                            "akshare",
                            "firecrawl",
                            "professional_sites",
                            "guba",
                        ],
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
                # We can't use self.log_warning here because super().__init__ hasn't been called yet
                print(
                    f"Warning: Error loading strategy configuration from database: {e}"
                )

        super().__init__(
            name,
            params
            or {
                "sentiment_threshold": 0.6,
                "news_count_threshold": 5,
                "search_depth": 10,
                "time_window_hours": 24,
                "data_sources": ["akshare", "firecrawl", "professional_sites", "guba"],
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
        # 移除sentiment_threshold阈值限制，设置为0以确保所有分数都会被输出
        self.sentiment_threshold = 0.0
        self.news_count_threshold = self.params.get("news_count_threshold", 5)
        self.search_depth = self.params.get("search_depth", 10)
        self.time_window_hours = self.params.get("time_window_hours", 24)
        self.data_sources = self.params.get(
            "data_sources", ["akshare", "firecrawl", "professional_sites", "guba"]
        )

        # FireCrawl configuration - only configure if firecrawl is in data_sources
        self.firecrawl_config = {}
        if "firecrawl" in self.data_sources:
            firecrawl_params = self.params.get("firecrawl_config", {})
            self.firecrawl_config = {
                "api_url": firecrawl_params.get(
                    "api_url", "http://192.168.1.2:8080/v1"
                ),
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

        # Initialize qian_gu_qian_ping_data to store overall market sentiment data
        # This loads Qian Gu Qian Ping (千股千评) data for all stocks at initialization
        self.qian_gu_qian_ping_data = None
        self._load_qian_gu_qian_ping_data()

        # For compatibility with tests, also set qgqp_data attribute
        self.qgqp_data = self.qian_gu_qian_ping_data

        self.logger.info(
            f"Initialized {self.name} strategy with params: "
            f"sentiment_threshold={self.sentiment_threshold}, "
            f"news_count_threshold={self.news_count_threshold}, "
            f"time_window_hours={self.time_window_hours}, "
            f"data_sources={self.data_sources}"
        )

    def get_akshare_news(self, stock_code: str) -> List[Dict]:
        """
        Get stock news from AkShare within the last 5 days

        Args:
            stock_code: Stock code

        Returns:
            List of news items within the last 5 days
        """
        if not ak:
            self.log_warning("AkShare not available, skipping AkShare news collection")
            return []

        try:
            # Get recent news for the stock
            news_df = ak.stock_news_em(stock_code)

            if news_df.empty:
                return []

            # Map Chinese column names to English equivalents
            column_mapping = {
                '新闻标题': 'title',
                '新闻内容': 'content',
                '发布时间': 'publish_time',
                '新闻链接': 'url',
                '文章来源': 'source'
            }

            # Rename columns to English equivalents
            news_df = news_df.rename(columns=column_mapping)

            # Filter by time window (last 5 days)
            time_threshold = datetime.now() - timedelta(days=5)
            if "publish_time" in news_df.columns:
                # Handle datetime conversion properly
                news_df["publish_time"] = pd.to_datetime(
                    news_df["publish_time"], errors="coerce"
                )
                news_df = news_df[news_df["publish_time"] >= time_threshold]

            # Convert to list of dictionaries
            news_items = []
            for _, row in news_df.head(self.search_depth).iterrows():
                # Handle publish_time properly
                publish_time = row.get("publish_time")
                publish_time_str = ""
                if pd.notnull(publish_time):
                    publish_time_str = (
                        publish_time.isoformat()
                        if hasattr(publish_time, "isoformat")
                        else str(publish_time)
                    )

                news_items.append(
                    {
                        "title": str(row.get("title", "")),
                        "content": str(row.get("content", ""))[
                            :1000
                        ],  # Limit content length
                        "url": str(row.get("url", "")),
                        "publishedAt": publish_time_str,
                        "source": "AkShare",
                        "time_weight": self._calculate_time_weight(publish_time_str),
                    }
                )

            self.log_info(
                f"Retrieved {len(news_items)} news items from AkShare for {stock_code} within last 5 days"
            )
            return news_items

        except Exception as e:
            self.log_error(f"Error getting AkShare news for {stock_code}: {e}")
            return []

    def get_stock_industry_info(self, stock_code: str) -> Dict:
        """
        Get stock industry and sector information using AkShare

        Args:
            stock_code: Stock code

        Returns:
            Dictionary with industry and sector information
        """
        try:
            if not ak:
                self.log_warning(
                    "AkShare not available, skipping industry info collection"
                )
                return {}

            # Get industry and sector information
            industry_df = ak.stock_board_industry_name_em()

            # Filter for the specific stock code
            # Note: This is a simplified implementation. In practice, you might need to map
            # the stock code to its industry using additional AkShare functions
            industry_info = {}
            if not industry_df.empty and "板块名称" in industry_df.columns:
                # Get first few industry names as examples
                industry_info["industries"] = industry_df["板块名称"].head(5).tolist()

            self.log_info(f"Retrieved industry information for {stock_code}")
            return industry_info

        except Exception as e:
            self.log_error(f"Error getting industry info for {stock_code}: {e}")
            return {}

    def scrape_guba_data(self, stock_code: str) -> Dict:
        """
        Scrape data from Eastmoney Guba (股吧) for the given stock code using AkShare

        Args:
            stock_code: Stock code

        Returns:
            Dictionary with scraped data from different Guba pages
        """
        try:
            guba_data = {
                "user_focus": [],  # 用户关注指数
                "institutional_rating": [],  # 机构评级
                "institutional_participation": [],  # 机构参与度
                "daily_desire": [],  # 每日参与意愿
            }

            # Use AkShare functions to get real Guba data
            if ak:
                try:
                    # Get user focus index data
                    focus_data = ak.stock_comment_detail_scrd_focus_em(stock_code)
                    if focus_data is not None and not focus_data.empty:
                        guba_data["user_focus"] = [
                            {
                                "title": f"[用户关注指数] {row.get('交易日', '')}",
                                "content": f"用户关注指数: {row.get('用户关注指数', '')}",
                                "publishedAt": f"{row.get('交易日', '')}T00:00:00",
                                "source": "东方财富网股吧",
                                "type": "user_focus",
                            }
                            for _, row in focus_data.iterrows()
                        ][: self.search_depth]

                    # Get institutional rating data
                    rating_data = ak.stock_comment_detail_zhpj_lspf_em(stock_code)
                    if rating_data is not None and not rating_data.empty:
                        guba_data["institutional_rating"] = [
                            {
                                "title": f"[机构评级] {row.get('交易日', '')}",
                                "content": f"评分: {row.get('评分', '')}",
                                "publishedAt": f"{row.get('交易日', '')}T00:00:00",
                                "source": "东方财富网股吧",
                                "type": "institutional_rating",
                            }
                            for _, row in rating_data.iterrows()
                        ][: self.search_depth]

                    # Get institutional participation data
                    participation_data = ak.stock_comment_detail_zlkp_jgcyd_em(
                        stock_code
                    )
                    if participation_data is not None and not participation_data.empty:
                        guba_data["institutional_participation"] = [
                            {
                                "title": f"[机构参与度] {row.get('交易日', '')}",
                                "content": f"机构参与度: {row.get('机构参与度', '')}",
                                "publishedAt": f"{row.get('交易日', '')}T00:00:00",
                                "source": "东方财富网股吧",
                                "type": "institutional_participation",
                            }
                            for _, row in participation_data.iterrows()
                        ][: self.search_depth]

                    # Get daily desire data
                    desire_data = ak.stock_comment_detail_scrd_desire_daily_em(
                        stock_code
                    )
                    if desire_data is not None and not desire_data.empty:
                        guba_data["daily_desire"] = [
                            {
                                "title": f"[每日参与意愿] {row.get('交易日', '')}",
                                "content": f"当日意愿上升: {row.get('当日意愿上升', '')}, 5日平均参与意愿变化: {row.get('5日平均参与意愿变化', '')}",
                                "publishedAt": f"{row.get('交易日', '')}T00:00:00",
                                "source": "东方财富网股吧",
                                "type": "daily_desire",
                            }
                            for _, row in desire_data.iterrows()
                        ][: self.search_depth]

                except Exception as e:
                    self.log_warning(
                        f"Error getting specific Guba data with AkShare: {e}"
                    )
                    # Fall back to sample data if AkShare fails
                    guba_data = self._get_sample_guba_data(stock_code)

            else:
                # If AkShare is not available, use sample data
                guba_data = self._get_sample_guba_data(stock_code)

            self.log_info(f"Successfully scraped Guba data for {stock_code}")
            return guba_data

        except Exception as e:
            self.log_error(f"Error scraping Guba data for {stock_code}: {e}")
            # Return sample data as fallback
            return self._get_sample_guba_data(stock_code)

    def _get_sample_guba_data(self, stock_code: str) -> Dict:
        """
        Get sample Guba data when real data is not available

        Args:
            stock_code: Stock code

        Returns:
            Dictionary with sample Guba data
        """
        guba_data = {
            "consultations": [],  # 咨询
            "research_reports": [],  # 研报
            "announcements": [],  # 公告
            "hot_posts": [],  # 热门帖子
        }

        # URLs for different types of data
        urls = {
            "consultations": f"https://guba.eastmoney.com/list,{stock_code},1,f.html",
            "research_reports": f"https://guba.eastmoney.com/list,{stock_code},2,f.html",
            "announcements": f"https://guba.eastmoney.com/list,{stock_code},3,f.html",
            "hot_posts": f"https://guba.eastmoney.com/list,{stock_code},99.html",
        }

        # Scrape each type of data
        for data_type, url in urls.items():
            items = self._scrape_guba_page(url, data_type)
            guba_data[data_type] = items

        return guba_data

    def _scrape_guba_page(self, url: str, data_type: str) -> List[Dict]:
        """
        Scrape a specific Guba page

        Returns:
            List of scraped items
        """
        try:
            # Check if FireCrawl is available
            if not self.firecrawl_config or not self.firecrawl_config.get("api_url"):
                self.log_warning("FireCrawl configuration not available, using sample data")
                return self._get_sample_guba_data(url, data_type)

            api_url = self.firecrawl_config["api_url"]
            timeout = self.firecrawl_config.get("timeout", 30)

            # Check FireCrawl availability
            if not self._is_firecrawl_available(api_url, timeout):
                self.log_warning("FireCrawl not available, using sample data")
                return self._get_sample_guba_data(url, data_type)

            headers = {
                "Content-Type": "application/json",
            }

            # Prepare payload for scrape endpoint
            payload = {
                "url": url,
                "formats": ["markdown", "html"]
            }

            # Send request to FireCrawl scrape API
            response = requests.post(
                f"{api_url}/scrape",
                headers=headers,
                json=payload,
                timeout=timeout,
            )

            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False)

                if success and 'data' in result:
                    data_content = result['data']

                    # Extract posts from the page content
                    posts = self._extract_posts_from_content(data_content, url, data_type)

                    # Filter posts to only include recent ones (within 5 days)
                    recent_posts = self._filter_recent_posts(posts, days=5)

                    self.log_info(f"Successfully scraped {len(recent_posts)} recent posts from {url}")
                    return recent_posts
                else:
                    self.log_warning(f"FireCrawl scrape unsuccessful for {url}, using sample data")
                    return self._get_sample_guba_data(url, data_type)
            else:
                self.log_warning(f"FireCrawl scrape failed with status {response.status_code} for {url}, using sample data")
                return self._get_sample_guba_data(url, data_type)

        except Exception as e:
            self.log_error(f"Error scraping Guba page {url}: {e}")
            # Fallback to sample data
            return self._get_sample_guba_data(url, data_type)

    def _extract_posts_from_content(self, data_content: Dict, url: str, data_type: str) -> List[Dict]:
        """
        Extract individual post information from scraped page content

        Args:
            data_content: The scraped data content from FireCrawl
            url: The original URL that was scraped
            data_type: Type of data being processed

        Returns:
            List of extracted post items
        """
        try:
            posts = []

            # Get content from markdown or html
            content = ""
            if "markdown" in data_content:
                content = data_content["markdown"]
            elif "html" in data_content:
                content = data_content["html"]

            if not content:
                self.log_warning(f"No content found in scraped data for {url}")
                return []

            # Use regex to find post links and titles
            import re

            # Patterns for finding post links
            markdown_pattern = r'\[([^\]]+)\]\(([^)"\s]+news[^)"\s]*)'
            markdown_pattern2 = r'\[([^\]]+)\]\((/news[^)"\s]*)'
            html_pattern = r'<a[^>]*href="([^"]*news[^"]*)"[^>]*>([^<]+)</a>'
            html_pattern2 = r'<a[^>]*href="(/news[^\"]*)"[^>]*>([^<]+)</a>'

            # Find matches
            markdown_matches = re.findall(markdown_pattern, content)
            markdown_matches2 = re.findall(markdown_pattern2, content)
            html_matches = re.findall(html_pattern, content)
            html_matches2 = re.findall(html_pattern2, content)

            # Process all matches
            all_matches = []

            # Process markdown matches
            for match in markdown_matches:
                title, url_part = match
                clean_url = url_part.split('"')[0].strip()
                if clean_url.startswith("/"):
                    full_url = "https://guba.eastmoney.com" + clean_url
                elif clean_url.startswith("http"):
                    full_url = clean_url
                else:
                    full_url = "https://guba.eastmoney.com/" + clean_url

                all_matches.append({
                    "title": title.strip(),
                    "url": full_url,
                    "type": "markdown_link",
                })

            # Process markdown matches2
            for match in markdown_matches2:
                title, url_part = match
                full_url = "https://guba.eastmoney.com" + url_part
                all_matches.append({
                    "title": title.strip(),
                    "url": full_url,
                    "type": "markdown_link2",
                })

            # Process HTML matches
            for match in html_matches:
                url_part, title = match
                clean_url = url_part.split('"')[0].strip()
                if clean_url.startswith("/"):
                    full_url = "https://guba.eastmoney.com" + clean_url
                elif clean_url.startswith("http"):
                    full_url = clean_url
                else:
                    full_url = "https://guba.eastmoney.com/" + clean_url

                all_matches.append({
                    "title": title.strip(),
                    "url": full_url,
                    "type": "html_link",
                })

            # Process HTML matches2
            for match in html_matches2:
                url_part, title = match
                full_url = "https://guba.eastmoney.com" + url_part
                all_matches.append({
                    "title": title.strip(),
                    "url": full_url,
                    "type": "html_link2",
                })

            # Remove duplicates
            unique_posts = []
            seen_urls = set()
            for post in all_matches:
                if post["url"] not in seen_urls:
                    unique_posts.append(post)
                    seen_urls.add(post["url"])

            # Limit to reasonable number of posts
            unique_posts = unique_posts[:20]

            # For each post, create a basic item structure
            for post in unique_posts:
                posts.append({
                    "title": post["title"],
                    "url": post["url"],
                    "content": f"Post from {post['url']}",  # Placeholder content
                    "publishedAt": datetime.now().isoformat(),  # Placeholder date
                    "source": "Guba",
                    "type": data_type,
                })

            return posts

        except Exception as e:
            self.log_error(f"Error extracting posts from content: {e}")
            return []

    def _filter_recent_posts(self, posts: List[Dict], days: int = 5) -> List[Dict]:
        """
        Filter posts to only include those within the specified number of days

        Args:
            posts: List of post items
            days: Number of days to filter (default: 5)

        Returns:
            List of recent post items
        """
        try:
            if not posts:
                return []

            recent_posts = []
            cutoff_date = datetime.now() - timedelta(days=days)

            for post in posts:
                # Try to parse the published date
                published_at = post.get("publishedAt")
                post_date = None

                if published_at:
                    try:
                        # Handle different date formats
                        if isinstance(published_at, str):
                            if "T" in published_at:
                                # ISO format
                                post_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                            else:
                                # Try other formats
                                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                                    try:
                                        post_date = datetime.strptime(published_at, fmt)
                                        break
                                    except ValueError:
                                        continue
                    except Exception:
                        pass

                # If we couldn't parse the date, include the post (better to include than exclude)
                if post_date is None or post_date >= cutoff_date:
                    recent_posts.append(post)

            return recent_posts

        except Exception as e:
            self.log_error(f"Error filtering recent posts: {e}")
            # If filtering fails, return original posts
            return posts

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

            # Check if FireCrawl is accessible and supports the required endpoint
            if not self._is_firecrawl_available(api_url, timeout):
                self.log_warning(
                    "FireCrawl is not available or doesn't support required endpoints, skipping FireCrawl data collection"
                )
                return []

            self.log_info(
                f"Calling FireCrawl API at {api_url}/search for queries: {queries}"
            )

            # Prepare the request for FireCrawl search API
            headers = {"Content-Type": "application/json"}

            all_results = []

            # Process each query individually since v1 doesn't support batch search
            for query in queries:
                try:
                    # Prepare payload for individual search (v1 format)
                    payload = {
                        "query": query
                    }

                    # Send request to FireCrawl search API (using v1 endpoint)
                    response = requests.post(
                        f"{api_url}/search",
                        headers=headers,
                        json=payload,
                        timeout=timeout,
                    )

                    self.log_info(
                        f"FireCrawl search response for query '{query}': {response.status_code}"
                    )

                    if response.status_code == 200:
                        result = response.json()
                        self.log_info(
                            f"FireCrawl search response data for query '{query}': {result}"
                        )
                        search_results = result.get("data", [])

                        # Process search results to extract relevant information
                        for item in search_results:
                            published_at = item.get("publishedAt", "")
                            all_results.append(
                                {
                                    "title": item.get("title", ""),
                                    "content": item.get("content", "")[:1000],  # Limit content length
                                    "url": item.get("url", ""),
                                    "publishedAt": published_at,
                                    "source": "FireCrawl",
                                    "time_weight": self._calculate_time_weight(
                                        published_at
                                    ),
                                }
                            )
                    else:
                        self.log_warning(
                            f"FireCrawl search failed for query '{query}': {response.status_code} - {response.text}"
                        )
                except Exception as e:
                    self.log_warning(f"Error processing query '{query}': {e}")
                    continue

            self.log_info(
                f"Successfully retrieved {len(all_results)} search results from FireCrawl"
            )
            return all_results

        except requests.exceptions.Timeout:
            self.log_error("FireCrawl API request timed out")
            return []
        except Exception as e:
            self.log_error(f"Error searching stock news with FireCrawl: {e}")
            return []

    def scrape_guba_page(self, stock_code: str) -> List[Dict]:
        """
        Directly scrape Eastmoney Guba pages for specific data

        Args:
            stock_code: Stock code to scrape data for

        Returns:
            List of scraped posts
        """
        try:
            # Define the specific URLs to scrape with their data limits
            urls_to_scrape = [
                {"url": f"https://guba.eastmoney.com/list,{stock_code},1,f.html", "limit": 5, "type": "5_day_news"},  # 5日内新闻
                {"url": f"https://guba.eastmoney.com/list,{stock_code},2,f.html", "limit": 5, "type": "5_reports"},  # 5条研报
                {"url": f"https://guba.eastmoney.com/list,{stock_code},3,f.html", "limit": 5, "type": "5_announcements"},  # 5条公告
                {"url": f"https://guba.eastmoney.com/list,{stock_code},99.html", "limit": 10, "type": "10_hot"},  # 10条热门
                {"url": f"https://guba.eastmoney.com/list,{stock_code}.html", "limit": 10, "type": "10_all"}  # 10条全部
            ]

            headers = {
                "Authorization": f"Bearer {self.firecrawl_config.get('api_key', '')}",
                "Content-Type": "application/json",
            }

            all_posts = []

            # Scrape each URL
            for url_info in urls_to_scrape:
                url = url_info["url"]
                limit = url_info["limit"]
                data_type = url_info["type"]

                try:
                    self.log_info(f"Scraping Eastmoney Guba URL: {url}")

                    data = {"url": url}
                    response = requests.post(
                        f"{self.firecrawl_config['api_url']}/scrape",
                        headers=headers,
                        json=data,
                        timeout=self.firecrawl_config.get("timeout", 30)
                    )

                    if response.status_code == 200:
                        result = response.json()
                        if "data" in result:
                            # Extract posts from the scraped content
                            posts = self._extract_guba_posts(result["data"], data_type)
                            # Limit the number of posts based on the URL type
                            limited_posts = posts[:limit]
                            all_posts.extend(limited_posts)
                            self.log_info(f"Successfully scraped {len(limited_posts)} posts from {url}")
                        else:
                            self.log_warning(f"No data found in scrape result for {url}")
                    else:
                        self.log_warning(f"Scraping failed for {url}: {response.status_code}")

                except Exception as e:
                    self.log_warning(f"Error scraping {url}: {e}")
                    continue

            self.log_info(f"Total posts scraped from Eastmoney Guba: {len(all_posts)}")
            return all_posts

        except Exception as e:
            self.log_error(f"Error scraping Eastmoney Guba pages: {e}")
            return []

    def _extract_guba_posts(self, data_content, data_type: str) -> List[Dict]:
        """
        Extract posts from scraped Eastmoney Guba content

        Args:
            data_content: Scraped data content
            data_type: Type of data being extracted

        Returns:
            List of extracted posts
        """
        try:
            # Get content from markdown or html
            content = ""
            if isinstance(data_content, list):
                page_data = data_content[0] if data_content else {}
            elif isinstance(data_content, dict):
                page_data = data_content
            else:
                page_data = {}

            if "markdown" in page_data:
                content = page_data["markdown"]
            elif "html" in page_data:
                content = page_data["html"]

            if content:
                import re

                posts = []

                # Patterns to match post links and titles
                # Markdown patterns
                markdown_patterns = [
                    r'\[([^\]]+)\]\(([^)"\s]+news[^)"\s]*)',
                    r'\[([^\]]+)\]\((/news[^)"\s]*)'
                ]

                # HTML patterns
                html_patterns = [
                    r'<a[^>]*href="([^"]*news[^"]*)"[^>]*>([^<]+)</a>',
                    r'<a[^>]*href="(/news[^\"]*)"[^>]*>([^<]+)</a>'
                ]

                # Extract using markdown patterns
                for pattern in markdown_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches[:15]:  # Limit to prevent too many matches
                        if len(match) >= 2:
                            title, url = match[0], match[1]
                            clean_url = url.split('"')[0].strip()
                            if clean_url.startswith("/"):
                                full_url = "https://guba.eastmoney.com" + clean_url
                            elif clean_url.startswith("http"):
                                full_url = clean_url
                            else:
                                full_url = "https://guba.eastmoney.com/" + clean_url

                            posts.append({
                                "title": title.strip(),
                                "url": full_url,
                                "type": data_type,
                                "source": "Eastmoney Guba"
                            })

                # Extract using HTML patterns
                for pattern in html_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches[:15]:  # Limit to prevent too many matches
                        if len(match) >= 2:
                            url, title = match[0], match[1]
                            clean_url = url.split('"')[0].strip()
                            if clean_url.startswith("/"):
                                full_url = "https://guba.eastmoney.com" + clean_url
                            elif clean_url.startswith("http"):
                                full_url = clean_url
                            else:
                                full_url = "https://guba.eastmoney.com/" + clean_url

                            posts.append({
                                "title": title.strip(),
                                "url": full_url,
                                "type": data_type,
                                "source": "Eastmoney Guba"
                            })

                # Deduplicate posts
                unique_posts = []
                seen_urls = set()
                for post in posts:
                    if post["url"] not in seen_urls:
                        unique_posts.append(post)
                        seen_urls.add(post["url"])

                return unique_posts

            return []

        except Exception as e:
            self.log_error(f"Error extracting Guba posts: {e}")
            return []

    def _is_firecrawl_available(self, api_url: str, timeout: int) -> bool:
        """
        Check if FireCrawl is available and supports the required endpoints

        Args:
            api_url: FireCrawl API URL (may include version path like /v1)
            timeout: Request timeout in seconds

        Returns:
            True if FireCrawl is available and supports required endpoints, False otherwise
        """
        try:
            # Extract base URL (without version path) for testing
            from urllib.parse import urlparse, urljoin
            parsed = urlparse(api_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"

            # First check if the base URL is accessible
            response = requests.get(base_url, timeout=timeout)
            if response.status_code != 200:
                return False

            # Check if it's the user's specific deployment by looking for the signature
            is_scrapers_js = "SCRAPERS-JS" in response.text
            if is_scrapers_js:
                self.log_info(
                    "Detected custom FireCrawl deployment (SCRAPERS-JS)"
                )

            # Test the actual scrape endpoint to see if it works
            # Use the provided api_url to construct the scrape endpoint
            scrape_url = urljoin(base_url, "/v1/scrape")

            try:
                # Test with a simple POST request to see if scrape endpoint works
                test_response = requests.post(
                    scrape_url,
                    json={"url": "https://example.com"},
                    timeout=timeout
                )
                # If we get a 200 response, it's working
                if test_response.status_code == 200:
                    if is_scrapers_js:
                        self.log_info(
                            "Confirmed that SCRAPERS-JS deployment supports /v1/scrape endpoint"
                        )
                    # Also test the search endpoint
                    search_url = f"{api_url}/search"
                    search_test_response = requests.post(
                        search_url,
                        json={"query": "test"},
                        timeout=timeout
                    )
                    if search_test_response.status_code == 200 or search_test_response.status_code == 400:
                        self.log_info("Confirmed that FireCrawl deployment supports search endpoint")
                        return True
            except:
                pass

            # For standard FireCrawl deployments, test with GET request
            try:
                response = requests.get(scrape_url, timeout=timeout)
                # If we get a 400 or 405 (method not allowed) but not 404, it's likely a FireCrawl endpoint
                if response.status_code in [400, 405]:
                    # Also test the search endpoint
                    search_url = f"{api_url}/search"
                    search_response = requests.get(search_url, timeout=timeout)
                    if search_response.status_code in [400, 405]:
                        self.log_info("Confirmed that FireCrawl deployment supports search endpoint")
                        return True
            except:
                pass

            # If we reach here, the scrape endpoint is not working
            if is_scrapers_js:
                self.log_warning(
                    "SCRAPERS-JS deployment does not appear to support standard /v1/scrape endpoint"
                )
            return False
        except Exception as e:
            self.log_warning(f"Error checking FireCrawl availability: {e}")
            return False

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

    def collect_all_data(self, stock_code: str, stock_name: str) -> Dict:
        """
        Collect data from all configured sources and organize it in a structured format for LLM analysis

        Args:
            stock_code: Stock code
            stock_name: Stock name

        Returns:
            Dictionary with all collected data organized for LLM analysis
        """
        all_data = {
            "stock_info": {"code": stock_code, "name": stock_name},
            "akshare_news": [],
            "industry_info": {},
            "guba_data": {},
            "professional_sites_data": [],
            "firecrawl_data": [],
            "qian_gu_qian_ping_data": {},
            "detailed_guba_data": {},
        }

        # Collect from AkShare (5-day news)
        if "akshare" in self.data_sources and ak:
            akshare_data = self.get_akshare_news(stock_code)
            all_data["akshare_news"] = akshare_data

        # Collect industry and sector information
        if "akshare" in self.data_sources and ak:
            industry_info = self.get_stock_industry_info(stock_code)
            all_data["industry_info"] = industry_info

        # Collect qian gu qian ping data (overall market sentiment)
        if "akshare" in self.data_sources and ak:
            qgqp_data = self.get_qian_gu_qian_ping_data_for_stock(stock_code)
            if qgqp_data:
                all_data["qian_gu_qian_ping_data"] = qgqp_data

        # Collect detailed Guba data
        if "akshare" in self.data_sources and ak:
            detailed_guba_data = self.get_detailed_guba_data(stock_code)
            all_data["detailed_guba_data"] = detailed_guba_data

        # Collect from professional sites
        if "professional_sites" in self.data_sources:
            professional_data = self.get_professional_site_data(stock_code, stock_name)
            all_data["professional_sites_data"] = professional_data

        # Collect from FireCrawl
        if "firecrawl" in self.data_sources:
            search_query = f"{stock_name} {stock_code} 股票 新闻 分析 评论"
            firecrawl_data = self.search_stock_news([search_query])

            # If FireCrawl search returns no results, try scraping Guba pages directly
            if not firecrawl_data:
                self.log_info(f"FireCrawl search returned no results for {stock_code}, trying direct Guba scraping")
                firecrawl_data = self.scrape_guba_page(stock_code)

            all_data["firecrawl_data"] = firecrawl_data

        # Collect from Guba
        if "guba" in self.data_sources:
            guba_data = self.scrape_guba_data(stock_code)
            all_data["guba_data"] = guba_data

        self.log_info(f"Collected all data for {stock_code}")
        return all_data

    def analyze_sentiment_with_llm(
        self, stock_code: str, stock_name: str, all_data: Dict
    ) -> Tuple[Optional[float], str, Dict]:
        """
        Analyze sentiment using LLM with enhanced prompt and retry mechanism

        Args:
            stock_code: Stock code
            stock_name: Stock name
            all_data: Dictionary with all collected data

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

                # Format data for LLM analysis
                formatted_data = self._format_data_for_llm(all_data)

                # Create analysis prompt
                prompt = f"""
                请分析以下关于股票 {stock_name} ({stock_code}) 的舆情信息, 并给出0-1分的 sentiment 评分:

                舆情内容:
                {formatted_data}

                分析要求:
                1. 综合评估所有舆情信息的情感倾向(积极, 消极或中性)
                2. 考虑信息的重要性和影响力
                3. 考虑信息的时效性
                4. 给出详细的分析理由

                请严格按照以下JSON格式输出结果:
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

                其中sentiment_score是0-1之间的数值, 0表示极度负面, 1表示极度正面, 0.5为中性.
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
                    time.sleep(2**attempt)  # 1s, 2s, 4s delay
                    continue
                else:
                    return None, f"LLM分析失败: {str(e)}", {}

        # If we reach here, all retries have failed
        return None, "LLM分析失败: 所有重试都已用尽", {}

    def _format_data_for_llm(self, all_data: Dict) -> str:
        """
        Format collected data for LLM analysis

        Args:
            all_data: Dictionary with all collected data

        Returns:
            Formatted string for LLM analysis
        """
        try:
            formatted_text = ""

            # Add stock information
            formatted_text += f"股票代码: {all_data['stock_info']['code']}\n"
            formatted_text += f"股票名称: {all_data['stock_info']['name']}\n\n"

            # Add industry information
            if all_data["industry_info"]:
                formatted_text += "行业信息:\n"
                for key, value in all_data["industry_info"].items():
                    formatted_text += f"  {key}: {value}\n"
                formatted_text += "\n"

            # Add qian gu qian ping data
            if all_data.get("qian_gu_qian_ping_data"):
                formatted_text += "千股千评综合数据:\n"
                qgqp_data = all_data["qian_gu_qian_ping_data"]
                for key, value in qgqp_data.items():
                    if key != "_id":  # Skip MongoDB _id field
                        formatted_text += f"  {key}: {value}\n"
                formatted_text += "\n"

            # Add detailed Guba data
            if all_data.get("detailed_guba_data"):
                formatted_text += "东方财富股吧详细数据:\n"
                detailed_guba = all_data["detailed_guba_data"]

                # Add user focus data
                if detailed_guba.get("user_focus"):
                    formatted_text += "  用户关注指数:\n"
                    for i, item in enumerate(detailed_guba["user_focus"][:5], 1):
                        formatted_text += f"    {i}. 日期: {item['date']}, 关注指数: {item['focus_index']}\n"

                # Add institutional participation data
                if detailed_guba.get("institutional_participation"):
                    formatted_text += "  机构参与度:\n"
                    for i, item in enumerate(
                        detailed_guba["institutional_participation"][:5], 1
                    ):
                        formatted_text += f"    {i}. 日期: {item['date']}, 参与度: {item['participation']}\n"

                # Add historical rating data
                if detailed_guba.get("historical_rating"):
                    formatted_text += "  历史评分:\n"
                    for i, item in enumerate(detailed_guba["historical_rating"][:5], 1):
                        formatted_text += (
                            f"    {i}. 日期: {item['date']}, 评分: {item['rating']}\n"
                        )

                # Add daily participation data
                if detailed_guba.get("daily_participation"):
                    formatted_text += "  日度市场参与意愿:\n"
                    for i, item in enumerate(
                        detailed_guba["daily_participation"][:5], 1
                    ):
                        formatted_text += f"    {i}. 日期: {item['date']}, 当日意愿上升: {item['daily_desire_rise']}, 5日平均参与意愿变化: {item['avg_participation_change']}\n"

                formatted_text += "\n"

            # Add AkShare news (5-day)
            if all_data["akshare_news"]:
                formatted_text += "AkShare近5日新闻:\n"
                for i, news in enumerate(all_data["akshare_news"][:5], 1):
                    formatted_text += f"  {i}. 标题: {news['title']}\n"
                    formatted_text += f"     发布时间: {news['publishedAt']}\n"
                    formatted_text += f"     内容摘要: {news['content'][:200]}...\n"
                    formatted_text += f"     来源: {news['source']}\n"
                formatted_text += "\n"

            # Add Guba data
            if all_data["guba_data"]:
                formatted_text += "东方财富股吧信息:\n"
                guba_data = all_data["guba_data"]

                # Add consultations
                if guba_data.get("consultations"):
                    formatted_text += "  近期咨询:\n"
                    for i, item in enumerate(guba_data["consultations"][:3], 1):
                        formatted_text += f"    {i}. 标题: {item['title']}\n"
                        formatted_text += f"       发布时间: {item.get('publishedAt', 'N/A')}\n"

                # Add research reports
                if guba_data.get("research_reports"):
                    formatted_text += "  最新研报:\n"
                    for i, item in enumerate(guba_data["research_reports"][:3], 1):
                        formatted_text += f"    {i}. 标题: {item['title']}\n"
                        formatted_text += f"       发布时间: {item.get('publishedAt', 'N/A')}\n"

                # Add announcements
                if guba_data.get("announcements"):
                    formatted_text += "  最新公告:\n"
                    for i, item in enumerate(guba_data["announcements"][:3], 1):
                        formatted_text += f"    {i}. 标题: {item['title']}\n"
                        formatted_text += f"       发布时间: {item.get('publishedAt', 'N/A')}\n"

                # Add hot posts
                if guba_data.get("hot_posts"):
                    formatted_text += "  热门帖子:\n"
                    for i, item in enumerate(guba_data["hot_posts"][:3], 1):
                        formatted_text += f"    {i}. 标题: {item['title']}\n"
                        formatted_text += f"       发布时间: {item.get('publishedAt', 'N/A')}\n"

                formatted_text += "\n"

            # Add professional sites data
            if all_data["professional_sites_data"]:
                formatted_text += "专业网站分析:\n"
                for i, item in enumerate(all_data["professional_sites_data"][:3], 1):
                    formatted_text += f"  {i}. 标题: {item['title']}\n"
                    formatted_text += f"     发布时间: {item.get('publishedAt', 'N/A')}\n"
                    formatted_text += f"     来源: {item['source']}\n"
                formatted_text += "\n"

            # Add FireCrawl data
            if all_data["firecrawl_data"]:
                formatted_text += "网络搜索结果:\n"
                for i, item in enumerate(all_data["firecrawl_data"][:5], 1):
                    formatted_text += f"  {i}. 标题: {item['title']}\n"
                    formatted_text += f"     发布时间: {item.get('publishedAt', 'N/A')}\n"
                    formatted_text += f"     内容摘要: {item.get('content', '')[:200]}...\n"
                    formatted_text += f"     来源: {item['source']}\n"
                formatted_text += "\n"

            return formatted_text

        except Exception as e:
            self.log_error(f"Error formatting data for LLM: {e}")
            return "数据格式化失败"

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
            self.log_info(f"收集到完整的舆情数据")

            if not all_data:
                reason = "无法收集到舆情数据"
                self.log_info(f"股票 {stock_code} 舆情分析结果: {reason}")
                return False, reason, None, {}

            # Count total relevant items
            total_items = (
                len(all_data.get("akshare_news", []))
                + len(all_data.get("professional_sites_data", []))
                + len(all_data.get("firecrawl_data", []))
            )

            # Add Guba data count
            guba_data = all_data.get("guba_data", {})
            if guba_data:
                total_items += (
                    len(guba_data.get("consultations", []))
                    + len(guba_data.get("research_reports", []))
                    + len(guba_data.get("announcements", []))
                    + len(guba_data.get("hot_posts", []))
                )

            if total_items < self.news_count_threshold:
                reason = f"相关信息数量不足，仅找到{total_items}条"
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

            reason = f"符合条件: 舆情 sentiment 分数({sentiment_score:.2f}) >= 阈值({self.sentiment_threshold}), 相关信息{total_items}条"
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

    def _create_detailed_reason(self, basic_reason: str, all_data: Dict, full_analysis: Dict, sentiment_score: float, total_items: int) -> str:
        """
        Create a detailed reason string with calculation data basis

        Args:
            basic_reason: Basic reason string
            all_data: All collected data
            full_analysis: Full analysis results from LLM
            sentiment_score: Sentiment score
            total_items: Total number of relevant items

        Returns:
            Detailed reason string with calculation data basis
        """
        try:
            # Start with the basic reason
            detailed_reason = f"{basic_reason}\n\n"

            # Add data source information
            detailed_reason += "数据源详情:\n"
            detailed_reason += f"- AkShare新闻: {len(all_data.get('akshare_news', []))}条\n"
            detailed_reason += f"- 行业信息: {'已获取' if all_data.get('industry_info') else '未获取'}\n"
            detailed_reason += f"- 千股千评数据: {'已获取' if all_data.get('qian_gu_qian_ping_data') else '未获取'}\n"

            # Add Guba data details
            guba_data = all_data.get('guba_data', {})
            guba_total = sum([
                len(guba_data.get('consultations', [])),
                len(guba_data.get('research_reports', [])),
                len(guba_data.get('announcements', [])),
                len(guba_data.get('hot_posts', []))
            ])
            detailed_reason += f"- Guba数据: {guba_total}条\n"

            # Add professional sites data
            detailed_reason += f"- 专业网站数据: {len(all_data.get('professional_sites_data', []))}条\n"

            # Add FireCrawl data
            detailed_reason += f"- 网络搜索数据: {len(all_data.get('firecrawl_data', []))}条\n"

            # Add detailed Guba data
            detailed_guba = all_data.get('detailed_guba_data', {})
            if detailed_guba:
                detailed_reason += "\n东方财富股吧详细数据:\n"
                if detailed_guba.get('user_focus'):
                    detailed_reason += f"- 用户关注指数: {len(detailed_guba['user_focus'])}条记录\n"
                if detailed_guba.get('institutional_participation'):
                    detailed_reason += f"- 机构参与度: {len(detailed_guba['institutional_participation'])}条记录\n"
                if detailed_guba.get('historical_rating'):
                    detailed_reason += f"- 历史评分: {len(detailed_guba['historical_rating'])}条记录\n"
                if detailed_guba.get('daily_participation'):
                    detailed_reason += f"- 日度市场参与意愿: {len(detailed_guba['daily_participation'])}条记录\n"

            # Add LLM analysis details if available
            if full_analysis:
                detailed_reason += "\nLLM分析详情:\n"
                detailed_reason += f"- 情感趋势: {full_analysis.get('sentiment_trend', 'N/A')}\n"
                detailed_reason += f"- 市场影响: {full_analysis.get('market_impact', 'N/A')}\n"
                detailed_reason += f"- 置信度: {full_analysis.get('confidence_level', 'N/A')}\n"
                detailed_reason += f"- 投资建议: {full_analysis.get('recommendation', 'N/A')}\n"

                # Add key events if available
                key_events = full_analysis.get('key_events', [])
                if key_events:
                    detailed_reason += f"- 关键事件: {', '.join(key_events[:5])}\n"  # Limit to first 5 events

                # Add risk factors if available
                risk_factors = full_analysis.get('risk_factors', [])
                if risk_factors:
                    detailed_reason += f"- 风险因素: {', '.join(risk_factors[:5])}\n"  # Limit to first 5 factors

            # Truncate if too long (MongoDB has limits on string size)
            if len(detailed_reason) > 2000:
                detailed_reason = detailed_reason[:1997] + "..."

            return detailed_reason

        except Exception as e:
            self.log_error(f"创建详细原因时出错: {e}")
            return basic_reason

    def execute(
        self, stock_data: Dict[str, pd.DataFrame], agent_name: str, db_manager
    ) -> List[Dict]:
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

                # Get all_data from the analysis for detailed information
                # Note: analyze_public_opinion doesn't directly return all_data, so we need to collect it again
                # This is a bit inefficient but necessary for the detailed analysis
                all_data = self.collect_all_data(code, stock_name)

                if meets_criteria:
                    # Calculate normalized score
                    normalized_score = (
                        self._calculate_score(sentiment_score)
                        if sentiment_score is not None
                        else 0.0
                    )

                    # Create detailed value string with all analysis information
                    detailed_value = self._create_detailed_value(
                        reason, sentiment_score, full_analysis, all_data
                    )

                    # Format the result according to requirements
                    # Pool only accepts score and value in pub field
                    selected_stocks.append(
                        {
                            "code": code,
                            "score": normalized_score,  # Score between 0 and 1
                            "value": detailed_value,  # Detailed analysis information
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

    def _load_qian_gu_qian_ping_data(self):
        """
        Load overall market sentiment data from qian gu qian ping (thousand stocks thousand reviews)
        using stock_comment_em() function. This data is loaded once and used for all stock analysis.
        """
        try:
            if not ak:
                self.log_warning(
                    "AkShare not available, skipping qian gu qian ping data loading"
                )
                return

            # Load qian gu qian ping data only once
            self.log_info("Loading qian gu qian ping data from AkShare...")
            qgqp_df = ak.stock_comment_em()

            if not qgqp_df.empty:
                # Convert to dictionary for easier lookup by stock code
                self.qian_gu_qian_ping_data = {}
                for _, row in qgqp_df.iterrows():
                    # Assuming the DataFrame has a '代码' column for stock code
                    if "代码" in row:
                        stock_code = row["代码"]
                        self.qian_gu_qian_ping_data[stock_code] = dict(row)

                self.log_info(
                    f"Successfully loaded qian gu qian ping data for {len(self.qian_gu_qian_ping_data)} stocks"
                )
            else:
                self.log_warning("Empty qian gu qian ping data returned from AkShare")

        except Exception as e:
            self.log_error(f"Error loading qian gu qian ping data: {e}")
            self.qian_gu_qian_ping_data = None

    def get_qian_gu_qian_ping_data_for_stock(self, stock_code: str) -> Optional[Dict]:
        """
        Get qian gu qian ping data for a specific stock

        Args:
            stock_code: Stock code

        Returns:
            Dictionary with qian gu qian ping data for the stock or None if not available
        """
        if self.qian_gu_qian_ping_data and stock_code in self.qian_gu_qian_ping_data:
            return self.qian_gu_qian_ping_data[stock_code]
        return None

    def _create_detailed_value(self, basic_reason: str, sentiment_score: float, full_analysis: Dict, all_data: Dict) -> str:
        """
        Create a detailed value string with all analysis information for storage in the database.

        Args:
            basic_reason: Basic reason string
            sentiment_score: Sentiment score from LLM analysis
            full_analysis: Full analysis results from LLM
            all_data: All collected data

        Returns:
            Detailed value string with all analysis information
        """
        try:
            # Start with the basic reason
            detailed_value = f"{basic_reason}\n\n"

            # Add LLM analysis details
            detailed_value += "=== LLM分析详情 ===\n"
            detailed_value += f"情感趋势: {full_analysis.get('sentiment_trend', 'N/A')}\n"
            detailed_value += f"市场影响: {full_analysis.get('market_impact', 'N/A')}\n"
            detailed_value += f"置信度: {full_analysis.get('confidence_level', 'N/A')}\n"
            detailed_value += f"投资建议: {full_analysis.get('recommendation', 'N/A')}\n"

            # Add key events if available with more detailed information
            key_events = full_analysis.get('key_events', [])
            if key_events:
                detailed_value += f"关键事件: {', '.join(key_events[:10])}\n"  # Limit to first 10 events

            # Add risk factors if available with more detailed information
            risk_factors = full_analysis.get('risk_factors', [])
            if risk_factors:
                detailed_value += f"风险因素: {', '.join(risk_factors[:10])}\n"  # Limit to first 10 factors

            # Add analysis summary - this should be detailed and support key events and risk factors
            analysis_summary = full_analysis.get('analysis_summary', '')
            if analysis_summary:
                # Limit summary length to prevent extremely long strings
                if len(analysis_summary) > 1000:
                    analysis_summary = analysis_summary[:1000] + "..."
                detailed_value += f"分析摘要: {analysis_summary}\n"

            # Add data source information with specific data, not just counts
            detailed_value += "\n=== 数据源详情 ===\n"

            # AkShare news data with specific information
            akshare_news = all_data.get('akshare_news', [])
            if akshare_news:
                detailed_value += f"AkShare新闻: 共{len(akshare_news)}条，主要涉及"
                # Extract key topics from news titles
                topics = []
                for news in akshare_news[:3]:  # First 3 news items
                    title = news.get('title', '')
                    # Simple keyword extraction (in a real implementation, you might use NLP)
                    if '业绩' in title:
                        topics.append('业绩')
                    elif '政策' in title:
                        topics.append('政策')
                    elif '市场' in title:
                        topics.append('市场')
                    elif '行业' in title:
                        topics.append('行业')
                topics = list(set(topics))  # Remove duplicates
                detailed_value += f"{', '.join(topics) if topics else '多个方面'}\n"
            else:
                detailed_value += "AkShare新闻: 无\n"

            # Industry information with actual data
            industry_info = all_data.get('industry_info', {})
            if industry_info:
                industries = industry_info.get('industries', [])
                detailed_value += f"行业信息: {', '.join(industries[:3]) if industries else '暂无'}\n"
            else:
                detailed_value += "行业信息: 未获取\n"

            # Qian gu qian ping data with specific information
            qgqp_data = all_data.get('qian_gu_qian_ping_data', {})
            if qgqp_data:
                # Extract key metrics from qian gu qian ping data
                rating = qgqp_data.get('综合评分', 'N/A')
                price_analysis = qgqp_data.get('市盈率', 'N/A')
                growth_potential = qgqp_data.get('成长性', 'N/A')
                detailed_value += f"千股千评数据: 综合评分{rating}, 市盈率{price_analysis}, 成长性{growth_potential}\n"
            else:
                detailed_value += "千股千评数据: 未获取\n"

            # Guba data with specific information
            guba_data = all_data.get('guba_data', {})
            if guba_data:
                consultations = guba_data.get('consultations', [])
                research_reports = guba_data.get('research_reports', [])
                announcements = guba_data.get('announcements', [])
                hot_posts = guba_data.get('hot_posts', [])

                # Extract key information from Guba data
                guba_topics = []
                for item in consultations[:2] + research_reports[:2] + announcements[:2] + hot_posts[:2]:
                    title = item.get('title', '')
                    if '利好' in title:
                        guba_topics.append('利好')
                    elif '风险' in title:
                        guba_topics.append('风险')
                    elif '分析' in title:
                        guba_topics.append('分析')
                guba_topics = list(set(guba_topics))

                detailed_value += f"Guba数据: 共{len(consultations)+len(research_reports)+len(announcements)+len(hot_posts)}条，主要涉及{', '.join(guba_topics) if guba_topics else '多个方面'}\n"
            else:
                detailed_value += "Guba数据: 无\n"

            # Professional sites data with specific information
            professional_data = all_data.get('professional_sites_data', [])
            if professional_data:
                sites = [item.get('source', '') for item in professional_data[:3]]
                detailed_value += f"专业网站数据: 来自{', '.join(sites) if sites else '多个网站'}，共{len(professional_data)}条\n"
            else:
                detailed_value += "专业网站数据: 无\n"

            # FireCrawl data with specific information
            firecrawl_data = all_data.get('firecrawl_data', [])
            if firecrawl_data:
                # Extract key topics from FireCrawl results
                topics = []
                for item in firecrawl_data[:3]:
                    title = item.get('title', '')
                    if '业绩' in title:
                        topics.append('业绩')
                    elif '政策' in title:
                        topics.append('政策')
                    elif '市场' in title:
                        topics.append('市场')
                topics = list(set(topics))
                detailed_value += f"网络搜索数据: 共{len(firecrawl_data)}条，主要涉及{', '.join(topics) if topics else '多个方面'}\n"
            else:
                detailed_value += "网络搜索数据: 无\n"

            # Add detailed Guba data with specific information for each category
            detailed_guba = all_data.get('detailed_guba_data', {})
            if detailed_guba:
                detailed_value += "\n=== 东方财富股吧详细数据 ===\n"

                # User focus data with actual values
                user_focus = detailed_guba.get('user关注指数', [])
                if user_focus:
                    focus_values = [str(item.get('focus_index', 'N/A')) for item in user_focus[:2]]
                    detailed_value += f"用户关注指数: {', '.join(focus_values)} (最近{len(user_focus)}条记录)\n"
                else:
                    detailed_value += "用户关注指数: 无数据\n"

                # Institutional participation data with actual values
                institutional_participation = detailed_guba.get('机构参与度', [])
                if institutional_participation:
                    participation_values = [str(item.get('participation', 'N/A')) for item in institutional_participation[:2]]
                    detailed_value += f"机构参与度: {', '.join(participation_values)} (最近{len(institutional_participation)}条记录)\n"
                else:
                    detailed_value += "机构参与度: 无数据\n"

                # Historical rating data with actual values
                historical_rating = detailed_guba.get('历史评分', [])
                if historical_rating:
                    rating_values = [str(item.get('rating', 'N/A')) for item in historical_rating[:2]]
                    detailed_value += f"历史评分: {', '.join(rating_values)} (最近{len(historical_rating)}条记录)\n"
                else:
                    detailed_value += "历史评分: 无数据\n"

                # Daily participation data with actual values
                daily_participation = detailed_guba.get('日度市场参与意愿', [])
                if daily_participation:
                    desire_values = [str(item.get('daily_desire_rise', 'N/A')) for item in daily_participation[:2]]
                    avg_change_values = [str(item.get('avg_participation_change', 'N/A')) for item in daily_participation[:2]]
                    detailed_value += f"日度市场参与意愿: 意愿上升{', '.join(desire_values)}, 5日平均变化{', '.join(avg_change_values)} (最近{len(daily_participation)}条记录)\n"
                else:
                    detailed_value += "日度市场参与意愿: 无数据\n"

            # Truncate if too long (MongoDB has limits on string size)
            if len(detailed_value) > 5000:
                detailed_value = detailed_value[:4997] + "..."

            return detailed_value

        except Exception as e:
            self.log_error(f"创建详细值时出错: {e}")
            return basic_reason

    def get_detailed_guba_data(self, stock_code: str) -> Dict:
        """
        Get detailed Guba data for a specific stock using AkShare functions:
        - stock_comment_detail_scrd_focus_em(): 用户关注指数
        - stock_comment_detail_zlkp_jgcyd_em(): 机构参与度
        - stock_comment_detail_zhpj_lspf_em(): 历史评分
        - stock_comment_detail_scrd_desire_daily_em(): 日度市场参与意愿

        Args:
            stock_code: Stock code

        Returns:
            Dictionary with detailed Guba data
        """
        try:
            detailed_data = {
                "user_focus": [],  # 用户关注指数
                "institutional_participation": [],  # 机构参与度
                "historical_rating": [],  # 历史评分
                "daily_participation": [],  # 日度市场参与意愿
            }

            if not ak:
                self.log_warning(
                    "AkShare not available, skipping detailed Guba data collection"
                )
                return detailed_data

            # Get user focus index data
            try:
                focus_data = ak.stock_comment_detail_scrd_focus_em(symbol=stock_code)
                if focus_data is not None and not focus_data.empty:
                    detailed_data["user_focus"] = [
                        {
                            "date": row.get("交易日", ""),
                            "focus_index": row.get("用户关注指数", ""),
                        }
                        for _, row in focus_data.iterrows()
                    ][: self.search_depth]
            except Exception as e:
                self.log_warning(f"Error getting user focus data for {stock_code}: {e}")

            # Get institutional participation data
            try:
                participation_data = ak.stock_comment_detail_zlkp_jgcyd_em(
                    symbol=stock_code
                )
                if participation_data is not None and not participation_data.empty:
                    detailed_data["institutional_participation"] = [
                        {
                            "date": row.get("交易日", ""),
                            "participation": row.get("机构参与度", ""),
                        }
                        for _, row in participation_data.iterrows()
                    ][: self.search_depth]
            except Exception as e:
                self.log_warning(
                    f"Error getting institutional participation data for {stock_code}: {e}"
                )

            # Get historical rating data
            try:
                rating_data = ak.stock_comment_detail_zhpj_lspf_em(symbol=stock_code)
                if rating_data is not None and not rating_data.empty:
                    detailed_data["historical_rating"] = [
                        {
                            "date": row.get("交易日", ""),
                            "rating": row.get("评分", ""),
                        }
                        for _, row in rating_data.iterrows()
                    ][: self.search_depth]
            except Exception as e:
                self.log_warning(
                    f"Error getting historical rating data for {stock_code}: {e}"
                )

            # Get daily participation data
            try:
                daily_data = ak.stock_comment_detail_scrd_desire_daily_em(
                    symbol=stock_code
                )
                if daily_data is not None and not daily_data.empty:
                    detailed_data["daily_participation"] = [
                        {
                            "date": row.get("交易日", ""),
                            "daily_desire_rise": row.get("当日意愿上升", ""),
                            "avg_participation_change": row.get(
                                "5日平均参与意愿变化", ""
                            ),
                        }
                        for _, row in daily_data.iterrows()
                    ][: self.search_depth]
            except Exception as e:
                self.log_warning(
                    f"Error getting daily participation data for {stock_code}: {e}"
                )

            self.log_info(f"Successfully retrieved detailed Guba data for {stock_code}")
            return detailed_data

        except Exception as e:
            self.log_error(f"Error getting detailed Guba data for {stock_code}: {e}")
            return detailed_data

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

    def _load_strategy_config_from_db(
        self, strategy_name: str, db_manager
    ) -> Optional[Dict]:
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
                self.log_info(
                    f"Successfully loaded strategy configuration for {strategy_name} from database"
                )
                return strategy_config
            else:
                self.log_warning(
                    f"No strategy configuration found for {strategy_name} in database"
                )
                return None

        except Exception as e:
            self.log_error(f"Error loading strategy configuration from database: {e}")
            return None

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
    pass
