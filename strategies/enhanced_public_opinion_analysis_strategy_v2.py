"""
Enhanced Public Opinion Analysis Strategy V2
舆情分析策略V2 - 增强版本
"""

import json
import re
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import requests

from utils.eastmoney_guba_scraper import scrape_all_guba_data
from strategies.base_strategy import BaseStrategy
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient


class EnhancedPublicOpinionAnalysisStrategyV2(BaseStrategy):
    """
    增强型舆情分析策略V2

    基于多种数据源进行舆情分析，包括：
    - AkShare新闻数据
    - 东方财富股吧数据
    - 专业网站分析
    - 网络搜索结果
    - 千股千评数据
    """

    # 类级别的千股千评数据DataFrame
    _qian_gu_qian_ping_df = None

    # 类级别的资金流数据DataFrame
    _individual_fund_flow_df = None
    _industry_fund_flow_df = None
    _concept_fund_flow_df = None

    def __init__(self, name: str, params: Dict, db_manager: MongoDBManager = None):
        """
        初始化策略

        Args:
            name: 策略名称
            params: 策略参数
            db_manager: 数据库管理器
        """
        super().__init__(name, params)
        self.db_manager = db_manager
        self.akshare_client = AkshareClient()

        # 更换新ip
        self._swith_ip()

        # 在策略初始化时加载千股千评数据
        self._load_qian_gu_qian_ping_data()

        # 在策略初始化时加载资金流数据
        self._load_fund_flow_data()

        # 更换新ip
        self._swith_ip()

    def _swith_ip(self):
        from utils.network_retry_handler import (
            handle_network_error_with_retry,
        )

        # 创建一个模拟的网络错误来触发IP更换
        fake_error = Exception("主动触发IP更换")
        handle_network_error_with_retry(fake_error)

    def _load_qian_gu_qian_ping_data(self):
        """
        加载千股千评数据到类级别的DataFrame
        """
        try:
            # 如果已经加载过，直接返回
            if (
                EnhancedPublicOpinionAnalysisStrategyV2._qian_gu_qian_ping_df
                is not None
            ):
                self.log_info("千股千评数据已加载，跳过重复加载")
                return

            self.log_info("开始加载千股千评数据...")

            # 直接调用akshare的stock_comment_em()函数获取所有股票数据
            import akshare as ak

            try:
                # 调用stock_comment_em()获取所有股票的千股千评数据（不带参数）
                qgqp_data = ak.stock_comment_em()

                if qgqp_data.empty:
                    self.log_warning("获取到的千股千评数据为空")
                    EnhancedPublicOpinionAnalysisStrategyV2._qian_gu_qian_ping_df = (
                        pd.DataFrame()
                    )
                    return

                # 存储完整的DataFrame
                EnhancedPublicOpinionAnalysisStrategyV2._qian_gu_qian_ping_df = (
                    qgqp_data
                )

                self.log_info(f"成功加载千股千评数据，包含 {len(qgqp_data)} 只股票")

            except Exception as e:
                self.log_error(f"调用akshare.stock_comment_em()失败: {e}")
                EnhancedPublicOpinionAnalysisStrategyV2._qian_gu_qian_ping_df = (
                    pd.DataFrame()
                )

        except Exception as e:
            self.log_error(f"加载千股千评数据时出错: {e}")
            EnhancedPublicOpinionAnalysisStrategyV2._qian_gu_qian_ping_df = (
                pd.DataFrame()
            )

    def _load_fund_flow_data(self):
        """
        加载资金流数据到类级别的DataFrame
        """
        try:
            # 如果已经加载过，直接返回
            if (
                EnhancedPublicOpinionAnalysisStrategyV2._individual_fund_flow_df
                is not None
                and EnhancedPublicOpinionAnalysisStrategyV2._industry_fund_flow_df
                is not None
                and EnhancedPublicOpinionAnalysisStrategyV2._concept_fund_flow_df
                is not None
            ):
                self.log_info("资金流数据已加载，跳过重复加载")
                return

            self.log_info("开始加载资金流数据...")

            # 直接调用akshare的函数获取资金流数据
            import akshare as ak

            try:
                # 获取个股资金流排名
                individual_fund_flow = ak.stock_individual_fund_flow_rank("今日")
                if not individual_fund_flow.empty:
                    EnhancedPublicOpinionAnalysisStrategyV2._individual_fund_flow_df = (
                        individual_fund_flow
                    )
                    self.log_info(
                        f"成功加载个股资金流数据，包含 {len(individual_fund_flow)} 只股票"
                    )
                else:
                    self.log_warning("获取到的个股资金流数据为空")
                    EnhancedPublicOpinionAnalysisStrategyV2._individual_fund_flow_df = (
                        pd.DataFrame()
                    )

                # 获取行业资金流排名
                industry_fund_flow = ak.stock_sector_fund_flow_rank(
                    "今日", "行业资金流"
                )
                if not industry_fund_flow.empty:
                    EnhancedPublicOpinionAnalysisStrategyV2._industry_fund_flow_df = (
                        industry_fund_flow
                    )
                    self.log_info(
                        f"成功加载行业资金流数据，包含 {len(industry_fund_flow)} 个行业"
                    )
                else:
                    self.log_warning("获取到的行业资金流数据为空")
                    EnhancedPublicOpinionAnalysisStrategyV2._industry_fund_flow_df = (
                        pd.DataFrame()
                    )

                # 获取概念资金流排名
                concept_fund_flow = ak.stock_sector_fund_flow_rank("今日", "概念资金流")
                if not concept_fund_flow.empty:
                    EnhancedPublicOpinionAnalysisStrategyV2._concept_fund_flow_df = (
                        concept_fund_flow
                    )
                    self.log_info(
                        f"成功加载概念资金流数据，包含 {len(concept_fund_flow)} 个概念"
                    )
                else:
                    self.log_warning("获取到的概念资金流数据为空")
                    EnhancedPublicOpinionAnalysisStrategyV2._concept_fund_flow_df = (
                        pd.DataFrame()
                    )

            except Exception as e:
                self.log_error(f"调用akshare资金流函数失败: {e}")
                # 使用公共网络错误重试函数
                from utils.network_retry_handler import handle_network_error_with_retry

                if not handle_network_error_with_retry(e):
                    print(f"经过重试后仍然失败，跳过")

        except Exception as e:
            self.log_error(f"加载资金流数据时出错: {e}")
            EnhancedPublicOpinionAnalysisStrategyV2._individual_fund_flow_df = (
                pd.DataFrame()
            )
            EnhancedPublicOpinionAnalysisStrategyV2._industry_fund_flow_df = (
                pd.DataFrame()
            )
            EnhancedPublicOpinionAnalysisStrategyV2._concept_fund_flow_df = (
                pd.DataFrame()
            )

    def _get_fund_flow_data_for_stock(
        self, stock_code: str, industry_info: Dict
    ) -> Dict:
        """
        获取指定股票的资金流数据

        Args:
            stock_code: 股票代码
            industry_info: 行业信息字典（包含industry和conception）

        Returns:
            资金流数据字典
        """
        try:
            fund_flow_data = {
                "individual_fund_flow": {},
                "industry_fund_flow": {},
                "concept_fund_flow": {},
            }

            # 获取个股资金流数据
            if (
                EnhancedPublicOpinionAnalysisStrategyV2._individual_fund_flow_df
                is not None
                and not EnhancedPublicOpinionAnalysisStrategyV2._individual_fund_flow_df.empty
            ):
                df = EnhancedPublicOpinionAnalysisStrategyV2._individual_fund_flow_df
                # 查找股票代码匹配的数据
                stock_data = df[df["代码"] == stock_code]
                if not stock_data.empty:
                    # 只提取需要的字段：今日涨跌幅、今日主力净流入-净占比
                    stock_row = stock_data.iloc[0]
                    filtered_individual_data = {
                        "今日涨跌幅": stock_row.get("今日涨跌幅", "N/A"),
                        "今日主力净流入-净占比": stock_row.get(
                            "今日主力净流入-净占比", "N/A"
                        ),
                    }
                    fund_flow_data["individual_fund_flow"] = filtered_individual_data
                    self.log_info(f"从缓存中获取股票 {stock_code} 的个股资金流数据")

            # 获取行业资金流数据
            industry = industry_info.get("industry", "")
            if (
                EnhancedPublicOpinionAnalysisStrategyV2._industry_fund_flow_df
                is not None
                and not EnhancedPublicOpinionAnalysisStrategyV2._industry_fund_flow_df.empty
                and industry
            ):
                df = EnhancedPublicOpinionAnalysisStrategyV2._industry_fund_flow_df
                # 查找行业匹配的数据
                industry_data = df[df["名称"] == industry]
                if not industry_data.empty:
                    # 只提取需要的字段：今日涨跌幅、今日主力净流入-净占比
                    industry_row = industry_data.iloc[0]
                    filtered_industry_data = {
                        "今日涨跌幅": industry_row.get("今日涨跌幅", "N/A"),
                        "今日主力净流入-净占比": industry_row.get(
                            "今日主力净流入-净占比", "N/A"
                        ),
                    }
                    fund_flow_data["industry_fund_flow"] = filtered_industry_data
                    self.log_info(f"从缓存中获取行业 {industry} 的资金流数据")

            # 获取概念资金流数据
            conception = industry_info.get("conception", [])
            if (
                EnhancedPublicOpinionAnalysisStrategyV2._concept_fund_flow_df
                is not None
                and not EnhancedPublicOpinionAnalysisStrategyV2._concept_fund_flow_df.empty
                and conception
            ):
                df = EnhancedPublicOpinionAnalysisStrategyV2._concept_fund_flow_df
                # 查找概念匹配的数据 - conception是一个数组，包含多个概念名称
                concept_flow_data = []
                if isinstance(conception, list):
                    for concept_name in conception:
                        concept_data = df[df["名称"] == concept_name]
                        if not concept_data.empty:
                            # 只提取需要的字段：今日涨跌幅和日主力净流入-净额
                            concept_row = concept_data.iloc[0]
                            filtered_concept_data = {
                                "概念名称": concept_name,
                                "今日涨跌幅": concept_row.get("今日涨跌幅", "N/A"),
                                "今日主力净流入-净占比": concept_row.get(
                                    "今日主力净流入-净占比", "N/A"
                                ),
                            }
                            concept_flow_data.append(filtered_concept_data)
                            self.log_info(
                                f"从缓存中获取概念 {concept_name} 的资金流数据"
                            )
                elif isinstance(conception, str):
                    concept_data = df[df["名称"] == conception]
                    if not concept_data.empty:
                        # 只提取需要的字段：概念名称、今日涨跌幅、今日主力净流入-净占比
                        concept_row = concept_data.iloc[0]
                        filtered_concept_data = {
                            "概念名称": conception,
                            "今日涨跌幅": concept_row.get("今日涨跌幅", "N/A"),
                            "今日主力净流入-净占比": concept_row.get(
                                "今日主力净流入-净占比", "N/A"
                            ),
                        }
                        concept_flow_data.append(filtered_concept_data)
                        self.log_info(f"从缓存中获取概念 {conception} 的资金流数据")

                if concept_flow_data:
                    fund_flow_data["concept_fund_flow"] = concept_flow_data
            self.log_info(f"Fund flow data collected: {fund_flow_data}")
            return fund_flow_data

        except Exception as e:
            self.log_warning(f"获取资金流数据失败: {e}")
            return {
                "individual_fund_flow": {},
                "industry_fund_flow": {},
                "concept_fund_flow": {},
            }

    def _get_qian_gu_qian_ping_data_for_stock(self, stock_code: str) -> Dict:
        """
        从已加载的DataFrame中获取指定股票的千股千评数据

        Args:
            stock_code: 股票代码

        Returns:
            千股千评数据字典
        """
        try:
            # 检查是否已加载数据
            if (
                EnhancedPublicOpinionAnalysisStrategyV2._qian_gu_qian_ping_df is None
                or EnhancedPublicOpinionAnalysisStrategyV2._qian_gu_qian_ping_df.empty
            ):
                self.log_warning("千股千评数据未加载，返回空字典")
                return {}

            # 从DataFrame中查找特定股票的数据
            df = EnhancedPublicOpinionAnalysisStrategyV2._qian_gu_qian_ping_df

            # 查找股票代码匹配的数据
            stock_data = df[df["代码"] == stock_code]

            if stock_data.empty:
                self.log_warning(f"未找到股票 {stock_code} 的千股千评数据")
                return {}

            # 将找到的股票数据转换为字典
            result = stock_data.iloc[0].to_dict()
            self.log_info(f"从缓存中获取股票 {stock_code} 的千股千评数据")
            return result

        except Exception as e:
            self.log_warning(f"从缓存获取千股千评数据失败: {e}")
            return {}

    def _update_pool_immediately(self, stock_result: Dict):
        """
        立即更新pool数据库中的pub字段

        Args:
            stock_result: 股票分析结果
        """
        try:
            if not self.db_manager:
                self.log_warning("没有数据库管理器，无法更新pool")
                return

            # 获取pool集合
            pool_collection = self.db_manager.db["pool"]

            # 找到最新的pool记录
            latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])
            if not latest_pool_record:
                self.log_warning("没有找到pool记录，无法更新")
                return

            # 获取股票代码和策略名称
            stock_code = stock_result.get("code")
            strategy_name = stock_result.get("strategy_name", self.name)

            # 查找该股票在pool中的位置
            stocks = latest_pool_record.get("stocks", [])
            stock_index = -1
            for i, stock in enumerate(stocks):
                if stock.get("code") == stock_code:
                    stock_index = i
                    break

            if stock_index == -1:
                self.log_warning(f"股票 {stock_code} 不在pool中，无法更新")
                return

            # 提取score和value
            score = stock_result.get("score", 0.0)
            value = stock_result.get("value", "")

            # 构建更新操作
            update_field = f"stocks.{stock_index}.pub.{strategy_name}"

            # 更新数据库
            result = pool_collection.update_one(
                {"_id": latest_pool_record["_id"]},
                {
                    "$set": {
                        update_field: {"score": score, "value": value},
                        "pub_at": datetime.now(),
                    }
                },
            )

            if result.modified_count > 0:
                self.log_info(f"成功更新股票 {stock_code} 的pub字段")
            else:
                self.log_info(
                    f"股票 {stock_code} 的pub字段未更新（可能已存在相同数据）"
                )

        except Exception as e:
            self.log_error(f"更新pool数据库时出错: {e}")

    def execute(
        self,
        stock_data: Dict[str, pd.DataFrame],
        agent_name: str = None,
        db_manager: MongoDBManager = None,
    ) -> List[Dict]:
        """
        执行舆情分析策略

        Args:
            stock_data: 股票数据字典
            agent_name: 代理名称
            db_manager: 数据库管理器

        Returns:
            选中的股票列表
        """
        try:
            # 更新数据库管理器
            if db_manager is not None:
                self.db_manager = db_manager

            self.log_info(f"执行 {self.name} 策略，处理 {len(stock_data)} 只股票")
            self.log_info(f"待处理股票列表: {list(stock_data.keys())}")

            selected_stocks = []

            for stock_code in stock_data:
                self.log_info(f"开始处理股票: {stock_code}")

                # 获取股票名称
                stock_name = self._get_stock_name(stock_code)

                # 收集舆情数据
                all_data = self._collect_public_opinion_data(stock_code, stock_name)

                # 进行舆情分析
                sentiment_score, analysis_result = self._analyze_sentiment(
                    stock_code, stock_name, all_data
                )

                # 检查是否满足条件
                sentiment_threshold = self.params.get("sentiment_threshold", 0.0)
                news_count_threshold = self.params.get("news_count_threshold", 1)

                total_info_count = (
                    len(all_data.get("akshare_news", []))
                    + len(all_data.get("guba_data", {}).get("consultations", []))
                    + len(all_data.get("guba_data", {}).get("research_reports", []))
                    + len(all_data.get("guba_data", {}).get("announcements", []))
                    + len(all_data.get("guba_data", {}).get("hot_posts", []))
                    + len(all_data.get("professional_sites_data", []))
                    + len(all_data.get("firecrawl_data", []))
                )

                # 创建详细原因
                if (
                    sentiment_score >= sentiment_threshold
                    and total_info_count >= news_count_threshold
                ):
                    basic_reason = f"符合条件: 舆情 sentiment 分数({sentiment_score:.2f}) >= 阈值({sentiment_threshold}), 相关信息{total_info_count}条"
                else:
                    basic_reason = f"不符合条件: 舆情 sentiment 分数({sentiment_score:.2f}) < 阈值({sentiment_threshold}) 或 相关信息{total_info_count}条 < 阈值({news_count_threshold}条)"

                detailed_value = self._create_detailed_value(
                    basic_reason, all_data, analysis_result
                )

                selected_stocks.append(
                    {
                        "code": stock_code,
                        "score": sentiment_score,
                        "value": detailed_value,
                    }
                )

                self.log_info(
                    f"股票 {stock_code} 分析完成，评分: {sentiment_score:.4f}"
                )

            return selected_stocks

        except Exception as e:
            self.log_error(f"执行策略时出错: {e}")
            return []

    def _get_stock_name(self, stock_code: str) -> str:
        """
        获取股票名称

        Args:
            stock_code: 股票代码

        Returns:
            股票名称
        """
        try:
            # 从数据库获取股票名称
            if self.db_manager:
                stock_info = self.db_manager.stock_codes_collection.find_one(
                    {"code": stock_code}
                )
                if stock_info and "name" in stock_info:
                    return stock_info["name"]
            return stock_code
        except Exception as e:
            self.log_warning(f"获取股票名称失败: {e}")
            return stock_code

    def _collect_public_opinion_data(self, stock_code: str, stock_name: str) -> Dict:
        """
        收集舆情数据

        Args:
            stock_code: 股票代码
            stock_name: 股票名称

        Returns:
            舆情数据字典
        """
        try:
            self.log_info(f"开始舆情分析: {stock_code} ({stock_name})")

            all_data = {
                "stock_info": {"code": stock_code, "name": stock_name},
                "akshare_news": [],
                "industry_info": {},
                "fund_flow_data": {},
                "qian_gu_qian_ping_data": {},
                "detailed_guba_data": {},
                "guba_data": {},
                "professional_sites_data": [],
                "firecrawl_data": [],
            }

            # 收集AkShare新闻数据
            try:
                akshare_news = self.akshare_client.get_stock_news(stock_code, days=5)
                all_data["akshare_news"] = akshare_news
                self.log_info(
                    f"Retrieved {len(akshare_news)} news items from AkShare for {stock_code} within last 5 days"
                )
            except Exception as e:
                self.log_warning(f"获取AkShare新闻数据失败: {e}")

            # 收集行业信息
            try:
                # 从stock数据库中的code数据集获取industry和conception信息
                if self.db_manager:
                    stock_info = self.db_manager.stock_codes_collection.find_one(
                        {"code": stock_code}
                    )
                    if stock_info:
                        industry_info = {
                            "industry": stock_info.get("industry", ""),
                            "conception": stock_info.get("conception", ""),
                        }
                        all_data["industry_info"] = industry_info
                        self.log_info(
                            f"从数据库获取行业和概念信息: {stock_code} - 行业: {industry_info.get('industry', 'N/A')}, 概念: {industry_info.get('conception', 'N/A')}"
                        )
                    else:
                        self.log_warning(f"未找到股票 {stock_code} 的行业和概念信息")
                        all_data["industry_info"] = {}
                else:
                    self.log_warning("没有数据库管理器，无法获取行业和概念信息")
                    all_data["industry_info"] = {}
            except Exception as e:
                self.log_warning(f"获取行业和概念信息失败: {e}")
                all_data["industry_info"] = {}

            # 收集资金流数据
            try:
                fund_flow_data = self._get_fund_flow_data_for_stock(
                    stock_code, all_data["industry_info"]
                )
                all_data["fund_flow_data"] = fund_flow_data
                self.log_info(f"成功获取资金流数据用于 {stock_code}")
            except Exception as e:
                self.log_warning(f"获取资金流数据失败: {e}")
                all_data["fund_flow_data"] = {
                    "individual_fund_flow": {},
                    "industry_fund_flow": {},
                    "concept_fund_flow": {},
                }

            # # 收集千股千评数据 - 从缓存中获取
            try:
                qgqp_data = self._get_qian_gu_qian_ping_data_for_stock(stock_code)
                all_data["qian_gu_qian_ping_data"] = qgqp_data
                self.log_info(f"从缓存中获取千股千评数据用于 {stock_code}")
            except Exception as e:
                self.log_warning(f"获取千股千评数据失败: {e}")

            # # 收集详细Guba数据
            try:
                detailed_guba_data = self._get_detailed_guba_data(stock_code)
                all_data["detailed_guba_data"] = detailed_guba_data
                self.log_info(
                    f"Successfully retrieved detailed Guba data for {stock_code}"
                )
            except Exception as e:
                self.log_warning(f"获取详细Guba数据失败: {e}")

            # 收集Guba数据(股吧数据)
            try:
                guba_data = self._get_guba_data(stock_code)
                all_data["guba_data"] = guba_data
                self.log_info(f"Retrieved Guba data for {stock_code}")

                # 计数，处理8个股票后更换IP
                stock_count = getattr(self, "_stock_count", 0) + 1
                self._stock_count = stock_count

                if stock_count % 8 == 0:
                    self.log_info(f"已处理 {stock_count} 个股票，准备更换IP")
                    from utils.network_retry_handler import (
                        handle_network_error_with_retry,
                    )

                    # 创建一个模拟的网络错误来触发IP更换
                    fake_error = Exception("主动触发IP更换")
                    handle_network_error_with_retry(fake_error)
                # time.sleep(60)
            except Exception as e:
                self.log_warning(f"获取Guba数据失败: {e}")

            self.log_info(f"收集到完整的舆情数据")
            return all_data

        except Exception as e:
            self.log_error(f"收集舆情数据时出错: {e}")
            return all_data

    def _analyze_sentiment(
        self, stock_code: str, stock_name: str, all_data: Dict
    ) -> Tuple[float, Dict]:
        """
        使用LLM进行舆情分析

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            all_data: 所有收集的数据

        Returns:
            sentiment_score: 情感分数
            analysis_result: 分析结果
        """
        try:
            # 格式化数据
            formatted_data = self._format_data_for_llm(all_data)

            # 调用LLM进行分析
            sentiment_score, analysis_details, full_analysis = (
                self._get_llm_sentiment_analysis(stock_code, stock_name, formatted_data)
            )

            return sentiment_score, full_analysis

        except Exception as e:
            self.log_error(f"舆情分析时出错: {e}")
            return 0.5, {}

    def _format_data_for_llm(self, all_data: Dict) -> str:
        """
        格式化收集的数据用于LLM分析

        Args:
            all_data: 所有收集的数据

        Returns:
            格式化后的字符串
        """
        try:
            formatted_text = ""

            # 添加股票信息
            formatted_text += f"股票代码: {all_data['stock_info']['code']}\n"
            formatted_text += f"股票名称: {all_data['stock_info']['name']}\n\n"

            # 添加行业信息
            if all_data["industry_info"]:
                formatted_text += "行业信息:\n"
                industry_info = all_data["industry_info"]
                if "industry" in industry_info:
                    formatted_text += f"  行业: {industry_info['industry']}\n"
                if "conception" in industry_info:
                    formatted_text += f"  概念: {industry_info['conception']}\n"
                formatted_text += "\n"

            # 添加资金流数据
            if all_data.get("fund_flow_data"):
                formatted_text += "资金流数据:\n"
                fund_flow_data = all_data["fund_flow_data"]

                # 添加个股资金流数据
                if fund_flow_data.get("individual_fund_flow"):
                    individual_data = fund_flow_data["individual_fund_flow"]
                    if individual_data:
                        formatted_text += "  个股资金流:\n"
                        # 显示关键资金流指标 - 使用正确的字段名
                        if "今日涨跌幅" in individual_data:
                            formatted_text += f"    今日涨跌幅: {individual_data.get('今日涨跌幅', 'N/A')}%\n"
                        if "今日主力净流入-净占比" in individual_data:
                            formatted_text += f"    今日主力净流入-净占比: {individual_data.get('今日主力净流入-净占比', 'N/A')}%\n"

                # 添加行业资金流数据
                if fund_flow_data.get("industry_fund_flow"):
                    industry_data = fund_flow_data["industry_fund_flow"]
                    if industry_data:
                        formatted_text += "  行业资金流:\n"
                        # 显示关键资金流指标 - 使用正确的字段名
                        if "今日涨跌幅" in industry_data:
                            formatted_text += f"    今日涨跌幅: {industry_data.get('今日涨跌幅', 'N/A')}%\n"
                        if "今日主力净流入-净占比" in industry_data:
                            formatted_text += f"    今日主力净流入-净占比: {industry_data.get('今日主力净流入-净占比', 'N/A')}%\n"

                # 添加概念资金流数据
                if fund_flow_data.get("concept_fund_flow"):
                    concept_data = fund_flow_data["concept_fund_flow"]
                    if concept_data:
                        formatted_text += "  概念资金流:\n"
                        # 显示关键资金流指标 - 显示前5个概念
                        for i, concept in enumerate(concept_data[:5], 1):
                            formatted_text += f"    {i}. {concept.get('概念名称', 'N/A')}: 今日涨跌幅 {concept.get('今日涨跌幅', 'N/A')}%, 主力净流入-净占比 {concept.get('今日主力净流入-净占比', 'N/A')}%\n"

                formatted_text += "\n"

            # 添加千股千评数据
            if all_data.get("qian_gu_qian_ping_data"):
                formatted_text += "千股千评综合数据:\n"
                qgqp_data = all_data["qian_gu_qian_ping_data"]
                for key, value in qgqp_data.items():
                    if key != "_id":  # Skip MongoDB _id field
                        formatted_text += f"  {key}: {value}\n"
                formatted_text += "\n"

            # 添加详细Guba数据
            if all_data.get("detailed_guba_data"):
                formatted_text += "东方财富股吧详细数据:\n"
                detailed_guba = all_data["detailed_guba_data"]

                # 添加用户关注数据（简洁格式）
                if detailed_guba.get("user_focus"):
                    item = detailed_guba["user_focus"]
                    formatted_text += (
                        f"  用户关注指数: {item.get('focus_index', 'N/A')}\n"
                    )

                # 添加机构参与度数据（简洁格式）
                if detailed_guba.get("institutional_participation"):
                    item = detailed_guba["institutional_participation"]
                    formatted_text += (
                        f"  机构参与度: {item.get('participation', 'N/A')}\n"
                    )

                # 添加历史评分数据（简洁格式）
                if detailed_guba.get("historical_rating"):
                    item = detailed_guba["historical_rating"]
                    formatted_text += f"  历史评分: {item.get('rating', 'N/A')}\n"

                # 添加日度参与数据（简洁格式）
                if detailed_guba.get("daily_participation"):
                    item = detailed_guba["daily_participation"]
                    formatted_text += f"  日度市场参与意愿: 当日意愿上升: {item.get('daily_desire_rise', 'N/A')}, 5日平均参与意愿变化: {item.get('avg_participation_change', 'N/A')}\n"

                formatted_text += "\n"

            # 添加AkShare新闻
            if all_data["akshare_news"]:
                formatted_text += "AkShare近5日新闻:\n"
                for i, news in enumerate(all_data["akshare_news"][:10], 1):
                    formatted_text += f"    {i}. {news.get('日期', 'N/A')}：{news.get('摘要', 'N/A')[:60]}...\n"
                formatted_text += "\n"

            # 添加Guba数据
            if all_data["guba_data"]:
                formatted_text += "东方财富股吧信息:\n"
                guba_data = all_data["guba_data"]

                # 添加咨询
                if guba_data.get("consultations"):
                    formatted_text += "  近期咨询:\n"
                    for i, item in enumerate(guba_data["consultations"][:5], 1):
                        formatted_text += f"    {i}. {item.get('title', 'N/A')}\n"

                # 添加研报
                if guba_data.get("research_reports"):
                    formatted_text += "  最新研报:\n"
                    for i, item in enumerate(guba_data["research_reports"][:5], 1):
                        formatted_text += f"    {i}. {item.get('title', 'N/A')}\n"

                # 添加公告
                if guba_data.get("announcements"):
                    formatted_text += "  最新公告:\n"
                    for i, item in enumerate(guba_data["announcements"][:5], 1):
                        formatted_text += f"    {i}. {item.get('title', 'N/A')}\n"

                # 添加热门帖子
                if guba_data.get("hot_posts"):
                    formatted_text += "  热门帖子:\n"
                    for i, item in enumerate(guba_data["hot_posts"][:5], 1):
                        formatted_text += f"    {i}. {item.get('title', 'N/A')}\n"

                formatted_text += "\n"

                formatted_text += "\n"

            # 添加专业网站数据
            if all_data["professional_sites_data"]:
                formatted_text += "专业网站分析:\n"
                for i, item in enumerate(all_data["professional_sites_data"][:5], 1):
                    formatted_text += f"  {i}. 标题: {item.get('title', 'N/A')}\n"
                    formatted_text += (
                        f"     发布时间: {item.get('publishedAt', 'N/A')}\n"
                    )
                    formatted_text += f"     来源: {item.get('source', 'N/A')}\n"
                    formatted_text += (
                        f"     内容摘要: {item.get('content', 'N/A')[:200]}...\n"
                    )
                formatted_text += "\n"

            # 添加FireCrawl数据
            if all_data["firecrawl_data"]:
                formatted_text += "网络搜索结果:\n"
                for i, item in enumerate(all_data["firecrawl_data"][:10], 1):
                    formatted_text += f"  {i}. 标题: {item.get('title', 'N/A')}\n"
                    formatted_text += (
                        f"     发布时间: {item.get('publishedAt', 'N/A')}\n"
                    )
                    formatted_text += (
                        f"     内容摘要: {item.get('content', 'N/A')[:200]}...\n"
                    )
                    formatted_text += f"     来源: {item.get('source', 'N/A')}\n"
                formatted_text += "\n"

            # 记录格式化数据用于调试
            self.log_info(
                f"Formatted data for LLM analysis:\n{formatted_text[:1000]}..."
            )

            return formatted_text

        except Exception as e:
            self.log_error(f"Error formatting data for LLM: {e}")
            return "数据格式化失败"

    def _get_llm_sentiment_analysis(
        self, stock_code: str, stock_name: str, formatted_data: str
    ) -> Tuple[float, str, Dict]:
        """
        使用LLM进行情感分析

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            formatted_data: 格式化后的数据

        Returns:
            sentiment_score: 情感分数
            analysis_details: 分析详情
            full_analysis: 完整分析结果
        """
        try:
            # 创建用户提示词 - 汇总提炼舆情信息
            user_prompt = f"""
请基于以下舆情信息进行量化舆情分析：

## 舆情数据摘要：
{formatted_data}

请严格按照系统提示词的要求输出JSON格式的分析结果。

重要提醒：
1. 请直接输出JSON，不要包含任何思考过程或解释
2. 不要使用<think>标签
3. 基于实际舆情数据计算分数，不要使用示例值
4. 输出必须是严格的JSON格式
"""

            # 在控制台输出完整的用户提示词用于调试
            print(f"\n=== 用户提示词 (股票: {stock_code}) ===")
            print(user_prompt)
            print("=== 用户提示词结束 ===\n")

            # 调用LLM API
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    self.log_info(
                        f"Calling LLM API for sentiment analysis (attempt {attempt})"
                    )
                    self.log_info(f"User prompt length: {len(user_prompt)} characters")

                    # 调用LLM API
                    content = self._call_llm_api(user_prompt)

                    # 在控制台输出LLM响应用于调试
                    print(f"\n=== LLM响应 (股票: {stock_code}) ===")
                    print(f"响应长度: {len(content)} 字符")
                    print(f"响应内容: {content}")
                    print("=== LLM响应结束 ===\n")

                    # 尝试解析JSON响应
                    try:
                        # 记录内容用于调试
                        self.log_info(
                            f"LLM response content length: {len(content)} characters"
                        )
                        self.log_info(
                            f"LLM response content preview: {content[:500]}{'...' if len(content) > 500 else ''}"
                        )

                        # 处理包含<think>标签的情况
                        if "<think>" in content:
                            self.log_warning("LLM响应包含<think>标签，尝试提取JSON部分")

                            # 方法1: 尝试直接在整个内容中查找JSON
                            json_start = content.find("{")
                            json_end = content.rfind("}")

                            if (
                                json_start != -1
                                and json_end != -1
                                and json_end > json_start
                            ):
                                # 提取JSON内容
                                extracted_json = content[json_start : json_end + 1]
                                # 验证提取的JSON是否有效
                                try:
                                    json.loads(extracted_json)
                                    content = extracted_json
                                    self.log_info(
                                        f"从<think>标签中直接提取JSON成功: {content[:200]}..."
                                    )
                                except json.JSONDecodeError:
                                    # 如果直接提取失败，尝试更精确的方法
                                    self.log_warning(
                                        "直接提取的JSON无效，尝试更精确的提取"
                                    )
                                    # 查找</think>标签之后的内容
                                    think_end = content.find("</think>")

                                    if think_end != -1:
                                        # 提取</think>标签之后的内容
                                        after_think_content = content[
                                            think_end + 8 :
                                        ]  # len("</think>") = 8
                                        # 在</think>之后的内容中查找JSON
                                        json_start = after_think_content.find("{")
                                        json_end = after_think_content.rfind("}")
                                        if json_start != -1 and json_end != -1:
                                            content = after_think_content[
                                                json_start : json_end + 1
                                            ]
                                            self.log_info(
                                                f"从</think>标签之后提取的JSON: {content[:200]}..."
                                            )
                                        else:
                                            # 如果仍然找不到完整的JSON，尝试使用robust extraction
                                            sentiment_score = (
                                                self._extract_sentiment_score_robust(
                                                    content
                                                )
                                            )
                                            if sentiment_score is not None:
                                                self.log_info(
                                                    f"使用robust extraction获取sentiment_score: {sentiment_score}"
                                                )
                                                # 返回默认结果但使用提取的分数
                                                default_result = (
                                                    self._get_default_analysis_result()
                                                )
                                                default_result["score"] = (
                                                    sentiment_score
                                                )
                                                default_result["sentiment_score"] = (
                                                    sentiment_score
                                                )
                                                return (
                                                    sentiment_score,
                                                    default_result["analysis_summary"],
                                                    default_result,
                                                )
                                            else:
                                                raise ValueError(
                                                    "无法从</think>标签之后提取JSON"
                                                )
                                    else:
                                        # 如果没有</think>标签，尝试使用robust extraction
                                        sentiment_score = (
                                            self._extract_sentiment_score_robust(
                                                content
                                            )
                                        )
                                        if sentiment_score is not None:
                                            self.log_info(
                                                f"使用robust extraction获取sentiment_score: {sentiment_score}"
                                            )
                                            # 返回默认结果但使用提取的分数
                                            default_result = (
                                                self._get_default_analysis_result()
                                            )
                                            default_result["score"] = sentiment_score
                                            default_result["sentiment_score"] = (
                                                sentiment_score
                                            )
                                            return (
                                                sentiment_score,
                                                default_result["analysis_summary"],
                                                default_result,
                                            )
                                        else:
                                            raise ValueError("无法从内容中提取JSON")
                            else:
                                # 如果找不到JSON结构，尝试使用robust extraction
                                sentiment_score = self._extract_sentiment_score_robust(
                                    content
                                )
                                if sentiment_score is not None:
                                    self.log_info(
                                        f"使用robust extraction获取sentiment_score: {sentiment_score}"
                                    )
                                    # 返回默认结果但使用提取的分数
                                    default_result = self._get_default_analysis_result()
                                    default_result["score"] = sentiment_score
                                    default_result["sentiment_score"] = sentiment_score
                                    return (
                                        sentiment_score,
                                        default_result["analysis_summary"],
                                        default_result,
                                    )
                                else:
                                    raise ValueError("无法从<think>标签中提取JSON")

                        # 处理包含```标签的情况
                        elif "```" in content:
                            self.log_warning("LLM响应包含```标签，尝试提取JSON部分")
                            # 查找```json和```之间的内容
                            json_start_marker = content.find("```json")
                            if json_start_marker != -1:
                                # 从```json之后开始查找
                                json_start = json_start_marker + 7  # len("```json") = 7
                            else:
                                # 查找普通的```标记
                                json_start_marker = content.find("```")
                                json_start = (
                                    json_start_marker + 3
                                    if json_start_marker != -1
                                    else -1
                                )

                            json_end_marker = content.find("```", json_start)

                            if json_start != -1 and json_end_marker != -1:
                                # 提取```标签之间的内容
                                content = content[json_start:json_end_marker].strip()
                                self.log_info(f"提取的JSON内容: {content}")
                            elif json_start != -1:
                                # 如果只有开始标记，提取从开始标记到内容末尾的部分
                                content = content[json_start:].strip()
                                self.log_info(
                                    f"提取的JSON内容(从开始标记到末尾): {content}"
                                )
                            else:
                                # 回退到原来的方法
                                json_start = content.find("{")
                                json_end = content.rfind("}")
                                if json_start != -1 and json_end != -1:
                                    content = content[json_start : json_end + 1]
                                    self.log_info(
                                        f"使用备用方法提取的JSON内容: {content}"
                                    )
                                else:
                                    raise ValueError("无法从```标签中提取JSON")

                        # 解析JSON
                        analysis_result = json.loads(content)

                        # 验证必需字段
                        required_fields = [
                            "score",
                            "reason",
                            "details",
                            "weights",
                            "sentiment_score",
                            "sentiment_trend",
                            "key_events",
                            "market_impact",
                            "confidence_level",
                            "analysis_summary",
                            "recommendation",
                            "risk_factors",
                        ]

                        for field in required_fields:
                            if field not in analysis_result:
                                raise ValueError(f"Missing required field: {field}")

                        # 验证details结构
                        detail_fields = [
                            "policy",
                            "finance",
                            "industry",
                            "price_action",
                            "sentiment",
                        ]
                        for field in detail_fields:
                            if field not in analysis_result["details"]:
                                raise ValueError(f"Missing detail field: {field}")

                        sentiment_score = analysis_result["score"]
                        analysis_details = analysis_result["analysis_summary"]

                        self.log_info(
                            f"Successfully received LLM sentiment analysis response. Sentiment score: {sentiment_score}"
                        )
                        return sentiment_score, analysis_details, analysis_result

                    except json.JSONDecodeError as e:
                        self.log_warning(f"JSON解析失败 (尝试 {attempt}): {e}")
                        # 输出详细的JSON内容用于调试
                        print(f"\n=== JSON解析错误详情 ===")
                        print(f"错误位置: {e.pos}")
                        print(f"错误行: {e.lineno}")
                        print(f"错误列: {e.colno}")
                        print(f"JSON内容: {content}")
                        print("=== JSON解析错误结束 ===\n")

                        if attempt < max_retries:
                            time.sleep(2**attempt)  # 指数退避
                            continue
                        else:
                            raise ValueError(f"LLM响应不是有效的JSON格式: {content}")

                except Exception as e:
                    self.log_warning(f"LLM API调用失败 (尝试 {attempt}): {e}")
                    if attempt < max_retries:
                        time.sleep(2**attempt)  # 指数退避
                        continue
                    else:
                        raise

        except Exception as e:
            self.log_error(f"LLM舆情分析失败: {e}")
            # 返回默认结果
            default_result = self._get_default_analysis_result()
            return (
                default_result["score"],
                default_result["analysis_summary"],
                default_result,
            )

    def _load_system_prompt(self) -> str:
        """
        加载系统提示词

        Returns:
            系统提示词内容
        """
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__), "..", "config", "pub_opinion_prompt.md"
            )
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self.log_warning(f"加载系统提示词失败: {e}")
            # 返回默认系统提示词
            return "你是一个量化交易舆情分析助手。请基于提供的舆情信息进行综合分析，并输出严格的JSON格式结果。"

    def _call_llm_api(self, prompt: str) -> str:
        """
        调用LLM API

        Args:
            prompt: 提示词

        Returns:
            LLM响应内容
        """
        try:
            # 加载系统提示词
            system_prompt = self._load_system_prompt()

            # 获取LLM配置
            llm_config = self._get_llm_config()
            if not llm_config:
                self.log_error("无法获取LLM配置")
                return ""

            # 构建LLM请求
            llm_url = llm_config.get(
                "api_url", "http://192.168.1.177:1234/v1/chat/completions"
            )
            payload = {
                "model": llm_config.get("model", "qwen3-4b-instruct"),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "max_tokens": 8192,
            }

            response = requests.post(llm_url, json=payload, timeout=60)

            if response.status_code == 200:
                response_data = response.json()
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    choice = response_data["choices"][0]
                    if "message" in choice:
                        return choice["message"].get("content", "")

            self.log_warning(f"LLM API调用失败: {response.status_code}")
            return ""

        except Exception as e:
            self.log_warning(f"LLM API调用异常: {e}")
            return ""

    def _get_llm_config(self) -> Dict:
        """
        从数据库获取LLM配置

        Returns:
            LLM配置字典
        """
        try:
            if not self.db_manager:
                self.log_warning("没有数据库管理器，使用默认LLM配置")
                return self._get_default_llm_config()

            # 从strategies集合获取策略配置
            strategy_config = self.db_manager.get_strategy_by_name(self.name)

            if not strategy_config or "parameters" not in strategy_config:
                self.log_warning("无法找到策略配置，使用默认LLM配置")
                return self._get_default_llm_config()

            # 获取LLM名称
            llm_name = strategy_config["parameters"].get("llm_name", "qwen3-4B")

            # 从config集合获取LLM配置
            # 直接查询config集合的第一个文档，因为LLM配置存储在文档的llm_configs字段中
            config_record = self.db_manager.config_collection.find_one()

            if not config_record or "llm_configs" not in config_record:
                self.log_warning("无法找到LLM配置，使用默认LLM配置")
                return self._get_default_llm_config()

            # 查找指定的LLM配置
            llm_configs = config_record["llm_configs"]
            for config_item in llm_configs:
                if config_item.get("name") == llm_name:
                    self.log_info(f"找到LLM配置: {llm_name}")
                    return self._build_llm_config(config_item)

            # 如果没有找到指定的配置，使用第一个可用的配置
            if llm_configs:
                self.log_warning(f"LLM配置 '{llm_name}' 未找到，使用第一个可用配置")
                return self._build_llm_config(llm_configs[0])

            self.log_warning("没有可用的LLM配置，使用默认配置")
            return self._get_default_llm_config()

        except Exception as e:
            self.log_error(f"获取LLM配置时出错: {e}")
            return self._get_default_llm_config()

    def _build_llm_config(self, config_item: Dict) -> Dict:
        """
        构建LLM配置

        Args:
            config_item: 配置项

        Returns:
            构建后的LLM配置
        """
        return {
            "api_url": config_item.get(
                "api_url", "http://192.168.1.177:1234/v1/chat/completions"
            ),
            "model": config_item.get("model", "qwen3-4b-instruct"),
            "provider": config_item.get("provider", "ailibaba"),
            "timeout": config_item.get("timeout", 60),
            "api_key_env_var": config_item.get("api_key_env_var", ""),
        }

    def _get_default_llm_config(self) -> Dict:
        """
        获取默认LLM配置

        Returns:
            默认LLM配置
        """
        return {
            "api_url": "http://192.168.1.177:1234/v1/chat/completions",
            "model": "qwen3-4B",
            "provider": "ailibaba",
            "timeout": 60,
            "api_key_env_var": "",
        }

    def _get_default_analysis_result(self) -> Dict:
        """
        获取默认分析结果

        Returns:
            默认分析结果
        """
        return {
            "score": 0.5,
            "reason": "信息不足，无法进行准确分析",
            "details": {
                "policy": {"score": 0.5, "reason": "信息不足"},
                "finance": {"score": 0.5, "reason": "信息不足"},
                "industry": {"score": 0.5, "reason": "信息不足"},
                "price_action": {"score": 0.5, "reason": "信息不足"},
                "sentiment": {"score": 0.5, "reason": "信息不足"},
            },
            "weights": {
                "finance": 0.30,
                "industry": 0.25,
                "policy": 0.15,
                "price_action": 0.20,
                "sentiment": 0.10,
            },
            "sentiment_score": 0.5,
            "sentiment_trend": "无明显趋势",
            "key_events": [],
            "market_impact": "弱",
            "confidence_level": 0.5,
            "analysis_summary": "由于信息不足，无法进行准确的舆情分析。",
            "recommendation": "观望",
            "risk_factors": ["信息不足"],
        }

    def _extract_sentiment_score_robust(self, content: str) -> Optional[float]:
        """
        从内容中稳健地提取情感分数

        Args:
            content: 内容字符串

        Returns:
            提取的情感分数或None
        """
        try:
            # 方法1: 查找JSON对象
            json_matches = re.findall(r'\{[^{}]*"sentiment_score"[^{}]*\}', content)
            for json_match in json_matches:
                try:
                    analysis_result = json.loads(json_match)
                    if "sentiment_score" in analysis_result:
                        sentiment_score = float(analysis_result["sentiment_score"])
                        return max(0.0, min(1.0, sentiment_score))  # 限制在0-1范围内
                except json.JSONDecodeError:
                    continue

            # 方法2: 标准正则表达式模式
            score_match = re.search(r'"sentiment_score"\s*:\s*(\d+\.?\d*)', content)
            if score_match:
                sentiment_score = float(score_match.group(1))
                return max(0.0, min(1.0, sentiment_score))  # 限制在0-1范围内

            # 方法3: 查找任何看起来像情感分数的数字
            number_matches = re.findall(r"(\d+\.?\d*)", content)
            for match in number_matches:
                try:
                    score = float(match)
                    # 检查是否在有效范围内且有合理的小数位数
                    if 0 <= score <= 1 and len(match.split(".")[-1]) <= 2:
                        return score
                except ValueError:
                    continue

            return None

        except Exception as e:
            self.log_warning(f"Error in robust sentiment score extraction: {e}")
            return None

    def _create_detailed_value(
        self, basic_reason: str, all_data: Dict, full_analysis: Dict = None
    ) -> str:
        """
        创建详细值，包含完整的LLM JSON输出

        Args:
            basic_reason: 基本原因字符串
            all_data: 所有收集的数据
            full_analysis: 完整的LLM分析结果

        Returns:
            用于pool数据的完整LLM JSON字符串
        """
        try:
            # 如果存在完整的LLM分析结果，直接返回JSON字符串
            if full_analysis:
                import json

                # 将完整的LLM分析结果转换为JSON字符串
                json_output = json.dumps(full_analysis, ensure_ascii=False, indent=2)
                return json_output
            else:
                # 如果没有完整的分析结果，返回基本原因
                return basic_reason

        except Exception as e:
            self.log_error(f"创建详细原因时出错: {e}")
            return basic_reason

    def _extract_guba_posts_from_markdown(
        self, firecrawl_data: List[Dict], limit: int = 5
    ) -> List[Dict]:
        """
        从FireCrawl返回的markdown数据中提取股吧帖子数据

        Args:
            firecrawl_data: FireCrawl返回的数据列表
            limit: 提取的条数限制

        Returns:
            帖子数据列表
        """
        try:
            posts = []

            if not firecrawl_data:
                return posts

            # 获取第一个条目的markdown内容
            markdown_content = ""
            for item in firecrawl_data:
                if "markdown" in item:
                    markdown_content = item["markdown"]
                    break

            if not markdown_content:
                return posts

            lines = markdown_content.split("\n")

            # 查找表格开始位置
            table_start = -1
            for i, line in enumerate(lines):
                if "| 阅读  | 评论  | 标题  | 作者  | 最后更新 |" in line:
                    table_start = i
                    break

            if table_start == -1:
                # 尝试其他可能的表头格式
                for i, line in enumerate(lines):
                    if "| 阅读" in line and "| 评论" in line and "| 标题" in line:
                        table_start = i
                        break

            if table_start != -1:
                # 解析表格数据
                for i in range(
                    table_start + 2, min(table_start + 2 + limit * 2, len(lines))
                ):
                    if len(posts) >= limit:
                        break
                    line = lines[i].strip()
                    if line.startswith("|") and line.endswith("|"):
                        # 解析表格行
                        cells = [cell.strip() for cell in line.split("|")[1:-1]]
                        if len(cells) >= 5:
                            read_count = cells[0]
                            comment_count = cells[1]
                            title = cells[2]
                            author = cells[3]
                            last_update = cells[4]

                            # 提取标题中的链接文本
                            import re

                            title_match = re.search(r"\[(.*?)\]", title)
                            if title_match:
                                title_text = title_match.group(1)
                            else:
                                title_text = title

                            posts.append(
                                {
                                    "read_count": read_count,
                                    "comment_count": comment_count,
                                    "title": title_text,
                                    "author": author,
                                    "last_update": last_update,
                                    "type": "table_post",
                                }
                            )

            return posts

        except Exception as e:
            self.log_warning(f"从markdown提取股吧帖子数据失败: {e}")
            return []

    def _get_detailed_guba_data(self, stock_code: str) -> Dict:
        """
        获取东方财富股吧详细数据

        Args:
            stock_code: 股票代码

        Returns:
            详细股吧数据字典，包含：
            - user_focus: 用户关注指数（最新值）
            - institutional_participation: 机构参与度（最新值）
            - historical_rating: 历史评分（最新值）
            - daily_participation: 日度市场参与意愿（最新值）
        """
        try:
            self.log_info(f"开始获取详细股吧数据: {stock_code}")

            detailed_guba_data = {
                "user_focus": None,
                "institutional_participation": None,
                "historical_rating": None,
                "daily_participation": None,
            }

            # 1. 获取用户关注指数（最新值）
            try:
                import akshare as ak

                user_focus_data = ak.stock_comment_detail_scrd_focus_em(
                    symbol=stock_code
                )
                if not user_focus_data.empty:
                    # 获取最新一条数据
                    latest_row = user_focus_data.iloc[-1]
                    # 使用通用数据提取，不依赖特定列名
                    detailed_guba_data["user_focus"] = {
                        "date": latest_row.iloc[0] if len(latest_row) > 0 else "",
                        "focus_index": latest_row.iloc[1]
                        if len(latest_row) > 1
                        else "",
                        "change": latest_row.iloc[2] if len(latest_row) > 2 else "",
                    }
                    self.log_info(
                        f"成功获取用户关注指数最新数据: {detailed_guba_data['user_focus']}"
                    )
            except Exception as e:
                self.log_warning(f"获取用户关注指数失败: {e}")

            # 2. 获取机构参与度（最新值）
            try:
                import akshare as ak

                institutional_data = ak.stock_comment_detail_zlkp_jgcyd_em(
                    symbol=stock_code
                )
                if not institutional_data.empty:
                    # 获取最新一条数据
                    latest_row = institutional_data.iloc[-1]
                    # 使用通用数据提取，不依赖特定列名
                    detailed_guba_data["institutional_participation"] = {
                        "date": latest_row.iloc[0] if len(latest_row) > 0 else "",
                        "participation": latest_row.iloc[1]
                        if len(latest_row) > 1
                        else "",
                        "change": latest_row.iloc[2] if len(latest_row) > 2 else "",
                    }
                    self.log_info(
                        f"成功获取机构参与度最新数据: {detailed_guba_data['institutional_participation']}"
                    )
            except Exception as e:
                self.log_warning(f"获取机构参与度失败: {e}")

            # 3. 获取历史评分（最新值）
            try:
                import akshare as ak

                historical_rating_data = ak.stock_comment_detail_zhpj_lspf_em(
                    symbol=stock_code
                )
                if not historical_rating_data.empty:
                    # 获取最新一条数据
                    latest_row = historical_rating_data.iloc[-1]
                    # 使用通用数据提取，不依赖特定列名
                    detailed_guba_data["historical_rating"] = {
                        "date": latest_row.iloc[0] if len(latest_row) > 0 else "",
                        "rating": latest_row.iloc[1] if len(latest_row) > 1 else "",
                        "trend": latest_row.iloc[2] if len(latest_row) > 2 else "",
                    }
                    self.log_info(
                        f"成功获取历史评分最新数据: {detailed_guba_data['historical_rating']}"
                    )
            except Exception as e:
                self.log_warning(f"获取历史评分失败: {e}")

            # 4. 获取日度市场参与意愿（最新值）
            try:
                import akshare as ak

                daily_participation_data = ak.stock_comment_detail_scrd_desire_daily_em(
                    symbol=stock_code
                )
                if not daily_participation_data.empty:
                    # 获取最新一条数据
                    latest_row = daily_participation_data.iloc[-1]
                    # 使用通用数据提取，不依赖特定列名
                    detailed_guba_data["daily_participation"] = {
                        "date": latest_row.iloc[0] if len(latest_row) > 0 else "",
                        "daily_desire_rise": latest_row.iloc[1]
                        if len(latest_row) > 1
                        else "",
                        "avg_participation_change": latest_row.iloc[2]
                        if len(latest_row) > 2
                        else "",
                    }
                    self.log_info(
                        f"成功获取日度市场参与意愿最新数据: {detailed_guba_data['daily_participation']}"
                    )
            except Exception as e:
                self.log_warning(f"获取日度市场参与意愿失败: {e}")

            self.log_info(
                f"详细股吧数据收集完成: 用户关注指数({detailed_guba_data['user_focus'] is not None}), 机构参与度({detailed_guba_data['institutional_participation'] is not None}), 历史评分({detailed_guba_data['historical_rating'] is not None}), 日度参与意愿({detailed_guba_data['daily_participation'] is not None})"
            )
            return detailed_guba_data

        except Exception as e:
            self.log_error(f"获取详细股吧数据时出错: {e}")
            return {
                "user_focus": None,
                "institutional_participation": None,
                "historical_rating": None,
                "daily_participation": None,
            }

    def _get_firecrawl_config(self) -> Dict:
        """
        从数据库获取FireCrawl配置

        Returns:
            FireCrawl配置字典
        """
        try:
            if not self.db_manager:
                self.log_warning("没有数据库管理器，无法获取FireCrawl配置")
                return {}

            # 从strategies集合获取策略配置
            strategy_config = self.db_manager.get_strategy_by_name(self.name)

            if not strategy_config or "parameters" not in strategy_config:
                self.log_warning("无法找到策略配置，无法获取FireCrawl配置")
                return {}

            # 获取FireCrawl配置
            parameters = strategy_config["parameters"]
            firecrawl_config = parameters.get("firecrawl_config", {})

            if not firecrawl_config:
                self.log_warning("策略配置中没有FireCrawl配置")
                return {}

            self.log_info(
                f"成功获取FireCrawl配置: {firecrawl_config.get('api_url', 'N/A')}"
            )
            return firecrawl_config

        except Exception as e:
            self.log_warning(f"获取FireCrawl配置失败: {e}")
            return {}

    def _call_firecrawl_api(self, url: str, firecrawl_config: Dict) -> List[Dict]:
        """
        调用FireCrawl API爬取数据

        Args:
            url: 要爬取的URL
            firecrawl_config: FireCrawl配置

        Returns:
            爬取到的数据列表
        """
        try:
            import requests
            import json

            # 如果没有配置，直接返回空列表
            if not firecrawl_config:
                self.log_warning("FireCrawl配置为空，无法调用API")
                return []

            api_url = firecrawl_config.get("api_url")
            if not api_url:
                self.log_warning("FireCrawl配置中没有API URL")
                return []

            max_retries = firecrawl_config.get("max_retries", 3)
            timeout = firecrawl_config.get("timeout", 30)

            # 构建FireCrawl v1 API请求
            # FireCrawl v1 API格式：https://docs.firecrawl.dev/api-reference/scrape
            # 使用最基本的字段，避免不支持的字段
            payload = {"url": url, "formats": ["markdown"], "onlyMainContent": True}

            # 重试机制
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        f"{api_url}/scrape", json=payload, timeout=timeout
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            # 直接返回FireCrawl数据，让调用方处理解析
                            return [data]
                        else:
                            self.log_warning(
                                f"FireCrawl API返回失败: {data.get('error', 'Unknown error')}"
                            )
                            return []
                    else:
                        self.log_warning(
                            f"FireCrawl API调用失败 (状态码 {response.status_code}): {response.text}"
                        )

                except Exception as e:
                    self.log_warning(f"FireCrawl API调用异常 (尝试 {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        import time

                        time.sleep(firecrawl_config.get("retry_delay", 1))
                        continue

            return []

        except Exception as e:
            self.log_warning(f"调用FireCrawl API失败: {e}")
            return []

    def _extract_guba_posts_from_markdown(
        self, firecrawl_data: List[Dict], limit: int = 5
    ) -> List[Dict]:
        """
        从FireCrawl返回的markdown数据中提取股吧帖子数据

        Args:
            firecrawl_data: FireCrawl返回的数据列表
            limit: 提取的条数限制

        Returns:
            帖子数据列表
        """
        try:
            posts = []

            if not firecrawl_data:
                return posts

            # 获取第一个条目的markdown内容
            markdown_content = ""
            for item in firecrawl_data:
                if "markdown" in item:
                    markdown_content = item["markdown"]
                    break

            if not markdown_content:
                return posts

            lines = markdown_content.split("\n")

            # 查找表格开始位置
            table_start = -1
            for i, line in enumerate(lines):
                if "| 阅读  | 评论  | 标题  | 作者  | 最后更新 |" in line:
                    table_start = i
                    break

            if table_start == -1:
                # 尝试其他可能的表头格式
                for i, line in enumerate(lines):
                    if "| 阅读" in line and "| 评论" in line and "| 标题" in line:
                        table_start = i
                        break

            if table_start != -1:
                # 解析表格数据
                for i in range(
                    table_start + 2, min(table_start + 2 + limit * 2, len(lines))
                ):
                    if len(posts) >= limit:
                        break
                    line = lines[i].strip()
                    if line.startswith("|") and line.endswith("|"):
                        # 解析表格行
                        cells = [cell.strip() for cell in line.split("|")[1:-1]]
                        if len(cells) >= 5:
                            read_count = cells[0]
                            comment_count = cells[1]
                            title = cells[2]
                            author = cells[3]
                            last_update = cells[4]

                            # 提取标题中的链接文本
                            import re

                            title_match = re.search(r"\[(.*?)\]", title)
                            if title_match:
                                title_text = title_match.group(1)
                            else:
                                title_text = title

                            posts.append(
                                {
                                    "read_count": read_count,
                                    "comment_count": comment_count,
                                    "title": title_text,
                                    "author": author,
                                    "last_update": last_update,
                                    "type": "table_post",
                                }
                            )

            return posts

        except Exception as e:
            self.log_warning(f"从markdown提取股吧帖子数据失败: {e}")
            return []

    def _scrape_with_firecrawl(self, url: str, data_type: str) -> List[Dict]:
        """
        使用FireCrawl爬取股吧数据

        Args:
            url: 要爬取的URL
            data_type: 数据类型（用于日志）

        Returns:
            爬取到的数据列表
        """
        try:
            # 获取FireCrawl配置
            firecrawl_config = self._get_firecrawl_config()
            if not firecrawl_config:
                self.log_warning(f"无法获取FireCrawl配置，无法爬取{data_type}数据")
                return []

            # 使用FireCrawl爬取数据
            firecrawl_data = self._call_firecrawl_api(url, firecrawl_config)
            if firecrawl_data:
                self.log_info(f"成功使用FireCrawl爬取{data_type}数据")
                return firecrawl_data
            else:
                self.log_warning(f"FireCrawl爬取{data_type}数据为空")
                return []

        except Exception as e:
            self.log_warning(f"使用FireCrawl爬取{data_type}数据失败: {e}")
            return []

    def _get_guba_data(self, stock_code: str) -> Dict:
        """
        获取东方财富股吧基础数据

        Args:
            stock_code: 股票代码

        Returns:
            基础股吧数据字典，包含：
            - consultations: 近期咨询
            - research_reports: 最新研报
            - announcements: 最新公告
            - hot_posts: 热门帖子
        """
        try:
            self.log_info(f"开始获取基础股吧数据: {stock_code}")

            # 获取FireCrawl配置
            firecrawl_config = self._get_firecrawl_config()
            if not firecrawl_config:
                self.log_warning("无法获取FireCrawl配置，返回空数据")
                return {
                    "consultations": [],
                    "research_reports": [],
                    "announcements": [],
                    "hot_posts": [],
                }

            # 使用公共函数爬取所有类型的股吧数据
            all_guba_data = scrape_all_guba_data(
                stock_code, firecrawl_config, limit_per_type=5
            )

            self.log_info(
                f"基础股吧数据收集完成: 近期咨询({len(all_guba_data['consultations'])}), 最新研报({len(all_guba_data['research_reports'])}), 最新公告({len(all_guba_data['announcements'])}), 热门帖子({len(all_guba_data['hot_posts'])})"
            )
            return all_guba_data

        except Exception as e:
            self.log_error(f"获取基础股吧数据时出错: {e}")
            return {
                "consultations": [],
                "research_reports": [],
                "announcements": [],
                "hot_posts": [],
            }

    def _get_professional_sites_data(
        self, stock_code: str, stock_name: str
    ) -> List[Dict]:
        """
        获取专业网站数据

        Args:
            stock_code: 股票代码
            stock_name: 股票名称

        Returns:
            专业网站数据列表
        """
        try:
            self.log_info(f"开始获取专业网站数据: {stock_code} ({stock_name})")

            professional_data = []

            # 模拟专业网站数据
            # 在实际实现中，这里应该调用实际的API或爬取专业网站

            # 示例数据 - 模拟从专业网站获取的分析文章
            sample_articles = [
                {
                    "title": f"{stock_name}近期业绩分析报告",
                    "publishedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "专业财经网站",
                    "content": f"{stock_name}近期业绩表现稳定，公司基本面良好，具备长期投资价值。",
                },
                {
                    "title": f"{stock_name}行业地位分析",
                    "publishedAt": (datetime.now() - timedelta(days=1)).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "source": "专业投资平台",
                    "content": f"{stock_name}在所属行业中具有较强竞争力，市场份额稳步提升。",
                },
                {
                    "title": f"{stock_name}技术面分析",
                    "publishedAt": (datetime.now() - timedelta(days=2)).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "source": "专业技术分析平台",
                    "content": f"{stock_name}技术指标显示短期存在调整压力，但中长期趋势向好。",
                },
            ]

            professional_data.extend(sample_articles)

            self.log_info(f"成功获取 {len(professional_data)} 条专业网站数据")
            return professional_data

        except Exception as e:
            self.log_warning(f"获取专业网站数据失败: {e}")
            return []

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号（舆情分析策略不需要生成传统交易信号）

        Args:
            data: 输入数据DataFrame

        Returns:
            包含信号的DataFrame
        """
        try:
            # 舆情分析策略主要进行舆情分析，不生成传统交易信号
            # 返回一个空的DataFrame或包含基本信息的DataFrame
            if data.empty:
                return pd.DataFrame()

            # 创建一个包含基本信息的DataFrame
            signals_df = pd.DataFrame(
                {
                    "date": data.index
                    if hasattr(data.index, "name") and data.index.name == "date"
                    else data.index,
                    "signal": "HOLD",  # 舆情分析策略默认持有
                    "strength": 0.0,  # 信号强度
                    "reason": "舆情分析策略",  # 原因
                }
            )

            return signals_df

        except Exception as e:
            self.log_error(f"生成信号时出错: {e}")
            return pd.DataFrame()

    def calculate_position_size(
        self, signal: str, portfolio_value: float, price: float
    ) -> float:
        """
        计算仓位大小

        Args:
            signal: 交易信号
            portfolio_value: 当前投资组合价值
            price: 当前资产价格

        Returns:
            仓位大小
        """
        try:
            # 舆情分析策略的仓位计算逻辑
            # 基于信号强度计算建议仓位

            # 默认仓位比例
            position_ratio = 0.0

            # 根据信号类型调整仓位比例
            if signal == "BUY":
                position_ratio = 0.1  # 10%仓位
            elif signal == "STRONG_BUY":
                position_ratio = 0.2  # 20%仓位
            elif signal == "HOLD":
                position_ratio = 0.0  # 不建仓
            elif signal == "SELL":
                position_ratio = -0.1  # 减仓10%
            elif signal == "STRONG_SELL":
                position_ratio = -0.2  # 减仓20%

            # 计算股数
            position_value = portfolio_value * position_ratio
            shares = position_value / price if price > 0 else 0

        except Exception as e:
            self.log_error(f"计算仓位大小时出错: {e}")
            return 0.0

    def _get_firecrawl_data(self, stock_code: str, stock_name: str) -> List[Dict]:
        """
        获取FireCrawl数据 - 爬取真实网站内容

        Args:
            stock_code: 股票代码
            stock_name: 股票名称

        Returns:
            FireCrawl数据列表
        """
        try:
            self.log_info(f"开始获取FireCrawl数据: {stock_code} ({stock_name})")

            firecrawl_data = []

            # 专业网站列表 - 硬编码配置
            professional_sites = [
                "同花顺财经",
                "东方财富网",
                "雪球网",
                "新浪财经",
                "腾讯财经",
            ]

            # 构建要爬取的URL列表
            urls_to_crawl = []

            # 根据股票代码和名称构建搜索URL
            search_queries = [
                f"{stock_name} {stock_code} 最新消息",
                f"{stock_name} 股票分析",
                f"{stock_name} 业绩报告",
                f"{stock_name} 行业动态",
            ]

            # 为每个专业网站构建URL
            for site in professional_sites:
                for query in search_queries:
                    # 这里应该根据实际的网站URL模式构建
                    if site == "东方财富网":
                        url = f"https://so.eastmoney.com/web?q={query}"
                    elif site == "同花顺财经":
                        url = f"https://www.10jqka.com.cn/search.php?q={query}"
                    elif site == "雪球网":
                        url = f"https://xueqiu.com/k?q={query}"
                    elif site == "新浪财经":
                        url = (
                            f"https://finance.sina.com.cn/search/index.d.html?q={query}"
                        )
                    elif site == "腾讯财经":
                        url = f"https://finance.qq.com/search.htm?q={query}"
                    else:
                        continue

                    urls_to_crawl.append({"url": url, "site": site, "query": query})

            self.log_info(f"准备爬取 {len(urls_to_crawl)} 个URL")

            # 实际调用FireCrawl API爬取数据
            for url_info in urls_to_crawl:
                url = url_info["url"]
                site = url_info["site"]
                query = url_info["query"]

                self.log_info(f"使用FireCrawl爬取: {site} - {query}")

                # 使用FireCrawl爬取数据
                scraped_data = self._scrape_with_firecrawl(url, f"{site}数据")

                if scraped_data:
                    # 为每条数据添加来源信息
                    for item in scraped_data:
                        item["source"] = site
                        item["query"] = query

                    firecrawl_data.extend(scraped_data)
                    self.log_info(f"成功从 {site} 爬取 {len(scraped_data)} 条数据")
                else:
                    self.log_warning(f"从 {site} 爬取数据失败")

            # 如果没有爬取到任何数据，返回空列表
            if not firecrawl_data:
                self.log_warning("FireCrawl爬取数据为空，返回空列表")

            self.log_info(f"成功获取 {len(firecrawl_data)} 条FireCrawl数据")
            return firecrawl_data

        except Exception as e:
            self.log_warning(f"获取FireCrawl数据失败: {e}")
            return []
