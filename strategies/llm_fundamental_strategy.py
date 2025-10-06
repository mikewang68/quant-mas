import akshare as ak

"""
LLM Fundamental Strategy
Based on large language models for fundamental analysis of stocks.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
import logging
from strategies.base_strategy import BaseStrategy
import akshare as ak
import json
import requests
import os
from pymongo import MongoClient
from config.mongodb_config import MongoDBConfig

# Configure logger
logger = logging.getLogger(__name__)


class LLMFundamentalStrategy(BaseStrategy):
    """
    LLM Fundamental Strategy - Uses large language models for fundamental analysis
    """

    def __init__(
        self, name: str = "基于LLM的基本面分析策略", params: Optional[Dict] = None
    ):
        """
        Initialize the LLM fundamental strategy.

        Args:
            name: Name of the strategy
            params: Strategy parameters
        """
        super().__init__(name, params)

        # Get LLM configuration name from strategy parameters
        llm_config_name = None

        # First, try to get LLM config name from params passed to constructor
        if params and "llm_config_name" in params:
            llm_config_name = params.get("llm_config_name")
        elif params and "llm_name" in params:
            llm_config_name = params.get("llm_name")
        # If not found, try to get it from database strategy parameters
        elif params and "strategy_name" in params:
            strategy_params = self._load_strategy_params_from_db(
                params["strategy_name"]
            )
            if strategy_params and "llm_name" in strategy_params:
                llm_config_name = strategy_params.get("llm_name")
        else:
            llm_config_name = None

        # Load LLM configuration from database
        self.llm_config = self._load_llm_config_from_db(llm_config_name)

        # Data fetcher will be set by the agent when executing the strategy
        self.data_fetcher = None

        self.log_info(
            f"Initialized LLM Fundamental Strategy with API: {self.llm_config['api_url']}"
        )

    def _load_strategy_params_from_db(self, strategy_name: str) -> Optional[Dict]:
        """
        Load strategy parameters from database strategies collection.

        Args:
            strategy_name: Name of the strategy

        Returns:
            Dictionary with strategy parameters or None if not found
        """
        try:
            # Load MongoDB configuration
            mongodb_config = MongoDBConfig()
            config = mongodb_config.get_mongodb_config()

            # Connect to MongoDB
            if config.get("username") and config.get("password"):
                # With authentication
                uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?authSource={config.get('auth_database', 'admin')}"
            else:
                # Without authentication
                uri = f"mongodb://{config['host']}:{config['port']}/"

            client = MongoClient(uri)
            db = client[config["database"]]
            strategies_collection = db[mongodb_config.get_collection_name("strategies")]

            # Find strategy by name
            strategy_record = strategies_collection.find_one({"name": strategy_name})

            if strategy_record and "parameters" in strategy_record:
                return strategy_record["parameters"]

            self.log_warning(f"No parameters found for strategy: {strategy_name}")
            return None

        except Exception as e:
            self.log_error(f"Error loading strategy parameters from database: {e}")
            return None

    def _load_system_prompt(self) -> Dict[str, Any]:
        """
        Load system prompt from config file and convert to LLM-compatible JSON format.

        Returns:
            Dictionary with system prompt in JSON format
        """
        try:
            import os
            # Try multiple possible paths
            possible_paths = [
                "config/fund_sys_prompt.md",
                "../config/fund_sys_prompt.md",
                os.path.join(os.path.dirname(__file__), "../config/fund_sys_prompt.md"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "config/fund_sys_prompt.md")
            ]

            system_prompt_content = None
            for prompt_file_path in possible_paths:
                try:
                    with open(prompt_file_path, 'r', encoding='utf-8') as f:
                        system_prompt_content = f.read()
                        self.log_info(f"Successfully loaded system prompt from: {prompt_file_path}")
                        break
                except FileNotFoundError:
                    continue

            if system_prompt_content is None:
                raise FileNotFoundError("Could not find fund_sys_prompt.md in any of the expected locations")

            # Convert to JSON format for LLM
            system_prompt = {
                "role": "system",
                "content": system_prompt_content
            }

            self.log_info("Successfully loaded system prompt from config file and converted to JSON format")
            return system_prompt
        except Exception as e:
            self.log_error(f"Error loading system prompt from config file: {e}")
            # Fallback to default system prompt in JSON format
            return {
                "role": "system",
                "content": "你是一个专业的股票基本面分析师，请根据提供的财务数据进行详细分析。"
            }

    def _load_llm_config_from_db(
        self, config_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load LLM configuration from database config collection.

        Args:
            config_name: Name of the LLM configuration to load

        Returns:
            Dictionary with LLM configuration
        """
        try:
            # Load MongoDB configuration
            mongodb_config = MongoDBConfig()
            config = mongodb_config.get_mongodb_config()

            # Connect to MongoDB
            if config.get("username") and config.get("password"):
                # With authentication
                uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?authSource={config.get('auth_database', 'admin')}"
            else:
                # Without authentication
                uri = f"mongodb://{config['host']}:{config['port']}/"

            client = MongoClient(uri)
            db = client[config["database"]]
            config_collection = db[mongodb_config.get_collection_name("config")]

            # Get LLM configurations
            config_record = config_collection.find_one()

            if config_record and "llm_configs" in config_record:
                llm_configs = config_record["llm_configs"]

                # If a specific config name is provided, find it
                if config_name:
                    for config_item in llm_configs:
                        if config_item.get("name") == config_name:
                            return self._build_llm_config(config_item)

                # If no specific config name or not found, use the first one
                if llm_configs:
                    self.log_warning(
                        f"LLM configuration '{config_name}' not found, using first available configuration"
                    )
                    return self._build_llm_config(llm_configs[0])

            # Fallback to default configuration
            self.log_warning(
                "No LLM configuration found in database, using default configuration"
            )
            return self._get_default_llm_config()

        except Exception as e:
            self.log_error(f"Error loading LLM configuration from database: {e}")
            # Fallback to default configuration
            return self._get_default_llm_config()

    def _build_llm_config(self, config_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build LLM configuration from config item.

        Args:
            config_item: Configuration item from database

        Returns:
            Dictionary with LLM configuration
        """
        try:
            # Get API key from environment variable
            api_key_env_var = config_item.get("api_key_env_var", "")
            api_key = os.getenv(api_key_env_var, "")

            return {
                "api_url": config_item["api_url"],
                "api_key": api_key,
                "model": config_item["model"],
                "timeout": config_item["timeout"],
                "provider": config_item["provider"],
                "name": config_item["name"],
            }
        except Exception as e:
            self.log_error(f"Error building LLM configuration: {e}")
            return self._get_default_llm_config()

    def _get_default_llm_config(self) -> Dict[str, Any]:
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
            "timeout": 120,  # Increased timeout for qwen3-4B
            "provider": "",
            "name": "default",
        }

    def analyze_stock_fundamentals(self, stock_code: str) -> Dict[str, Any]:
        """
        Analyze stock fundamentals using LLM and data sources with retry mechanism.

        Args:
            stock_code: Stock code to analyze

        Returns:
            Dictionary with analysis results
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Get stock information using akshare
                stock_info = self.get_stock_info(stock_code)

                # Get financial data
                financial_data = self.get_financial_data(stock_code)

                # Calculate financial ratios
                financial_ratios = self.calculate_financial_ratios(financial_data)

                # Get industry information for comparison
                industry_info = self.get_industry_info(stock_code)

                # Combine all data for LLM analysis
                analysis_prompt = self.create_analysis_prompt(
                    stock_info, financial_data, financial_ratios, industry_info
                )

                # Get LLM analysis with increased timeout
                llm_result = self.get_llm_analysis(analysis_prompt)

                return llm_result

            except Exception as e:
                self.log_warning(
                    f"Attempt {attempt + 1} failed for stock {stock_code}: {e}"
                )
                if attempt < max_retries - 1:
                    # Wait before retrying (exponential backoff)
                    import time

                    time.sleep(2**attempt)  # 1s, 2s, 4s delay
                    continue
                else:
                    self.log_error(
                        f"All {max_retries} attempts failed for stock {stock_code}: {e}"
                    )
                    # Return a fallback analysis result instead of just error message
                    return self._create_fallback_analysis(stock_code, financial_ratios, industry_info)

    def get_stock_info(self, stock_code: str) -> Dict[str, Any]:
        """
        Get basic stock information using akshare.

        Args:
            stock_code: Stock code

        Returns:
            Dictionary with stock information
        """
        try:
            # Get stock name and basic info
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            info_dict = {}
            if not stock_info.empty:
                for _, row in stock_info.iterrows():
                    info_dict[row["item"]] = row["value"]

            return info_dict
        except Exception as e:
            self.log_warning(f"Error getting stock info for {stock_code}: {e}")
            return {}

    def get_financial_data(self, stock_code: str) -> Dict[str, Any]:
        """
        Get financial data using akshare.

        Args:
            stock_code: Stock code

        Returns:
            Dictionary with financial data
        """
        try:
            # Get key financial indicators
            try:
                financial_indicators = ak.stock_financial_abstract_ths(
                    symbol=stock_code
                )
                # Convert to the expected format
                if not financial_indicators.empty:
                    # Transpose the data to get items as keys
                    financial_indicators_dict = {}
                    for col in financial_indicators.columns:
                        if col != "报告期":
                            financial_indicators_dict[col] = financial_indicators[col].to_dict()
                else:
                    financial_indicators_dict = {}
            except Exception as e:
                self.log_warning(f"Error getting financial indicators for {stock_code}: {e}")
                financial_indicators_dict = {}

            # Get balance sheet data
            try:
                balance_sheet = ak.stock_financial_debt_ths(symbol=stock_code)
                # Convert to the expected format
                if not balance_sheet.empty:
                    balance_sheet_dict = {}
                    for col in balance_sheet.columns:
                        if col != "报告期":
                            balance_sheet_dict[col] = balance_sheet[col].to_dict()
                else:
                    balance_sheet_dict = {}
            except Exception as e:
                self.log_warning(f"Error getting balance sheet for {stock_code}: {e}")
                balance_sheet_dict = {}

            # Get income statement data
            try:
                income_statement = ak.stock_financial_benefit_ths(symbol=stock_code)
                # Convert to the expected format
                if not income_statement.empty:
                    income_statement_dict = {}
                    for col in income_statement.columns:
                        if col != "报告期":
                            income_statement_dict[col] = income_statement[col].to_dict()
                else:
                    income_statement_dict = {}
            except Exception as e:
                self.log_warning(f"Error getting income statement for {stock_code}: {e}")
                income_statement_dict = {}

            # Get cash flow statement data
            try:
                cash_flow = ak.stock_financial_cash_ths(symbol=stock_code)
                # Convert to the expected format
                if not cash_flow.empty:
                    cash_flow_dict = {}
                    for col in cash_flow.columns:
                        if col != "报告期":
                            cash_flow_dict[col] = cash_flow[col].to_dict()
                else:
                    cash_flow_dict = {}
            except Exception as e:
                self.log_warning(f"Error getting cash flow for {stock_code}: {e}")
                cash_flow_dict = {}

            return {
                "financial_indicators": financial_indicators_dict,
                "balance_sheet": balance_sheet_dict,
                "income_statement": income_statement_dict,
                "cash_flow": cash_flow_dict,
            }
        except Exception as e:
            self.log_warning(f"Error getting financial data for {stock_code}: {e}")
            return {
                "financial_indicators": {},
                "balance_sheet": {},
                "income_statement": {},
                "cash_flow": {},
            }

    def calculate_financial_ratios(self, financial_data: Dict) -> Dict[str, Any]:
        """
        Calculate key financial ratios from financial data.

        Args:
            financial_data: Financial data dictionary

        Returns:
            Dictionary with calculated financial ratios
        """
        try:
            ratios = {}

            # Extract key data from financial statements
            balance_sheet = financial_data.get("balance_sheet", {})
            income_statement = financial_data.get("income_statement", {})
            financial_indicators = financial_data.get("financial_indicators", {})

            # Liquidity ratios
            ratios["current_ratio"] = self.calculate_current_ratio(balance_sheet)
            ratios["quick_ratio"] = self.calculate_quick_ratio(balance_sheet)

            # Profitability ratios
            ratios["roe"] = self.calculate_roe(balance_sheet, income_statement)
            ratios["roa"] = self.calculate_roa(balance_sheet, income_statement)
            ratios["gross_margin"] = self.calculate_gross_margin(income_statement)
            ratios["net_margin"] = self.calculate_net_margin(income_statement)

            # Leverage ratios
            ratios["debt_to_equity"] = self.calculate_debt_to_equity(balance_sheet)
            ratios["interest_coverage"] = self.calculate_interest_coverage(
                income_statement
            )

            # Efficiency ratios
            ratios["asset_turnover"] = self.calculate_asset_turnover(
                balance_sheet, income_statement
            )

            # Valuation ratios (using financial indicators)
            ratios["pe_ratio"] = self.calculate_pe_ratio(financial_indicators)
            ratios["pb_ratio"] = self.calculate_pb_ratio(financial_indicators)

            # Growth ratios
            ratios["revenue_growth"] = self.calculate_revenue_growth(income_statement)
            ratios["earnings_growth"] = self.calculate_earnings_growth(income_statement)

            return ratios
        except Exception as e:
            self.log_warning(f"Error calculating financial ratios: {e}")
            return {}

    def calculate_current_ratio(self, balance_sheet: Dict) -> float:
        """Calculate current ratio"""
        try:
            # Use actual field names from balance sheet
            current_assets = self.get_latest_value(balance_sheet, "流动资产合计")
            current_liabilities = self.get_latest_value(balance_sheet, "流动负债合计")
            if current_liabilities and current_liabilities != 0:
                return current_assets / current_liabilities
        except Exception:
            pass
        return 0.0

    def calculate_quick_ratio(self, balance_sheet: Dict) -> float:
        """Calculate quick ratio"""
        try:
            current_assets = self.get_latest_value(balance_sheet, "流动资产合计")
            inventory = self.get_latest_value(balance_sheet, "存货")
            current_liabilities = self.get_latest_value(balance_sheet, "流动负债合计")
            if current_liabilities and current_liabilities != 0:
                return (current_assets - inventory) / current_liabilities
        except Exception:
            pass
        return 0.0

    def calculate_roe(self, balance_sheet: Dict, income_statement: Dict) -> float:
        """Calculate Return on Equity"""
        try:
            net_income = self.get_latest_value(income_statement, "*净利润")
            total_equity = self.get_latest_value(balance_sheet, "*所有者权益（或股东权益）合计")
            if total_equity and total_equity != 0:
                return net_income / total_equity
        except Exception:
            pass
        return 0.0

    def calculate_roa(self, balance_sheet: Dict, income_statement: Dict) -> float:
        """Calculate Return on Assets"""
        try:
            net_income = self.get_latest_value(income_statement, "*净利润")
            total_assets = self.get_latest_value(balance_sheet, "*资产合计")
            if total_assets and total_assets != 0:
                return net_income / total_assets
        except Exception:
            pass
        return 0.0

    def calculate_gross_margin(self, income_statement: Dict) -> float:
        """Calculate gross margin"""
        try:
            revenue = self.get_latest_value(income_statement, "其中：营业收入")
            cogs = self.get_latest_value(income_statement, "其中：营业成本")
            if revenue and revenue != 0:
                return (revenue - cogs) / revenue
        except Exception:
            pass
        return 0.0

    def calculate_net_margin(self, income_statement: Dict) -> float:
        """Calculate net profit margin"""
        try:
            net_income = self.get_latest_value(income_statement, "*净利润")
            revenue = self.get_latest_value(income_statement, "其中：营业收入")
            if revenue and revenue != 0:
                return net_income / revenue
        except Exception:
            pass
        return 0.0

    def calculate_debt_to_equity(self, balance_sheet: Dict) -> float:
        """Calculate debt to equity ratio"""
        try:
            total_liabilities = self.get_latest_value(balance_sheet, "*负债合计")
            total_equity = self.get_latest_value(balance_sheet, "*所有者权益（或股东权益）合计")
            if total_equity and total_equity != 0:
                return total_liabilities / total_equity
        except Exception:
            pass
        return 0.0

    def calculate_interest_coverage(self, income_statement: Dict) -> float:
        """Calculate interest coverage ratio"""
        try:
            # For now, return a placeholder as interest expense data might not be available
            # In a real implementation, you would need to get interest expense from income statement
            return 0.0
        except Exception:
            pass
        return 0.0

    def calculate_asset_turnover(
        self, balance_sheet: Dict, income_statement: Dict
    ) -> float:
        """Calculate asset turnover ratio"""
        try:
            revenue = self.get_latest_value(income_statement, "其中：营业收入")
            total_assets_begin = self.get_earlier_value(balance_sheet, "*资产合计")
            total_assets_end = self.get_latest_value(balance_sheet, "*资产合计")
            if (
                total_assets_begin
                and total_assets_end
                and (total_assets_begin + total_assets_end) != 0
            ):
                avg_assets = (total_assets_begin + total_assets_end) / 2
                return revenue / avg_assets
        except Exception:
            pass
        return 0.0

    def calculate_pe_ratio(self, financial_indicators: Dict) -> float:
        """Calculate P/E ratio"""
        try:
            # This would typically require market price data
            # For now, we'll return a placeholder
            return 0.0
        except Exception:
            pass
        return 0.0

    def calculate_pb_ratio(self, financial_indicators: Dict) -> float:
        """Calculate P/B ratio"""
        try:
            # This would typically require market price data
            # For now, we'll return a placeholder
            return 0.0
        except Exception:
            pass
        return 0.0

    def calculate_revenue_growth(self, income_statement: Dict) -> float:
        """Calculate revenue growth rate"""
        try:
            revenue_latest = self.get_latest_value(income_statement, "其中：营业收入")
            revenue_previous = self.get_earlier_value(income_statement, "其中：营业收入")
            if revenue_previous and revenue_previous != 0:
                return (revenue_latest - revenue_previous) / revenue_previous
        except Exception:
            pass
        return 0.0

    def calculate_earnings_growth(self, income_statement: Dict) -> float:
        """Calculate earnings growth rate"""
        try:
            earnings_latest = self.get_latest_value(income_statement, "*净利润")
            earnings_previous = self.get_earlier_value(income_statement, "*净利润")
            if earnings_previous and earnings_previous != 0:
                return (earnings_latest - earnings_previous) / earnings_previous
        except Exception:
            pass
        return 0.0

    def get_latest_value(self, data_dict: Dict, key: str) -> float:
        """Get the latest available value for a key in the data dictionary"""
        if key in data_dict:
            values = list(data_dict[key].values())
            if values:
                # Get the most recent non-zero value
                for value in reversed(values):
                    try:
                        # Handle string values with units like "万" or "亿"
                        if isinstance(value, str):
                            # Remove units and convert to float
                            if "万" in value:
                                val = float(value.replace("万", "")) * 10000
                            elif "亿" in value:
                                val = float(value.replace("亿", "")) * 100000000
                            elif "%" in value:
                                val = float(value.replace("%", "")) / 100
                            else:
                                val = float(value)
                        else:
                            val = float(value)

                        if val != 0:
                            return val
                    except (ValueError, TypeError):
                        continue
                # If no non-zero value, return the last value
                try:
                    last_value = values[-1]
                    if isinstance(last_value, str):
                        if "万" in last_value:
                            return float(last_value.replace("万", "")) * 10000
                        elif "亿" in last_value:
                            return float(last_value.replace("亿", "")) * 100000000
                        elif "%" in last_value:
                            return float(last_value.replace("%", "")) / 100
                        else:
                            return float(last_value)
                    else:
                        return float(last_value)
                except (ValueError, TypeError):
                    return 0.0
        return 0.0

    def get_earlier_value(self, data_dict: Dict, key: str) -> float:
        """Get the earlier available value for a key in the data dictionary"""
        if key in data_dict:
            values = list(data_dict[key].values())
            if len(values) > 1:
                # Get the second to last value
                try:
                    earlier_value = values[-2]
                    if isinstance(earlier_value, str):
                        if "万" in earlier_value:
                            return float(earlier_value.replace("万", "")) * 10000
                        elif "亿" in earlier_value:
                            return float(earlier_value.replace("亿", "")) * 100000000
                        elif "%" in earlier_value:
                            return float(earlier_value.replace("%", "")) / 100
                        else:
                            return float(earlier_value)
                    else:
                        return float(earlier_value)
                except (ValueError, TypeError):
                    return 0.0
        return 0.0

    def get_industry_info(self, stock_code: str) -> Dict[str, Any]:
        """
        Get industry information for comparison.

        Args:
            stock_code: Stock code

        Returns:
            Dictionary with industry information
        """
        try:
            # Get industry information
            industry_info = ak.stock_individual_info_em(symbol=stock_code)
            info_dict = {}
            if not industry_info.empty:
                for _, row in industry_info.iterrows():
                    if row["item"] == "行业":
                        info_dict["industry"] = row["value"]
                        break

            # For now, we'll return a placeholder
            # In a real implementation, you would get industry averages and benchmarks
            info_dict["industry_averages"] = {
                "roe": 0.08,  # 8% average ROE
                "pe": 15.0,  # 15x average P/E
                "debt_to_equity": 0.5,  # 0.5 average debt-to-equity
            }

            return info_dict
        except Exception as e:
            self.log_warning(f"Error getting industry info for {stock_code}: {e}")
            return {}

    def create_analysis_prompt(
        self,
        stock_info: Dict,
        financial_data: Dict,
        financial_ratios: Dict,
        industry_info: Dict,
    ) -> Dict[str, Any]:
        """
        Create prompt for LLM analysis in JSON format.

        Args:
            stock_info: Stock information
            financial_data: Financial data
            financial_ratios: Calculated financial ratios
            industry_info: Industry information

        Returns:
            Analysis prompt in JSON format for LLM
        """
        # Extract only the most recent financial data to reduce token usage
        simplified_financial_data = self._simplify_financial_data(financial_data)

        # Simplify financial ratios to only show key metrics
        simplified_ratios = self._simplify_financial_ratios(financial_ratios)

        # Simplify industry info
        simplified_industry = self._simplify_industry_info(industry_info)

        # Create user prompt content
        user_prompt_content = f"""
股票代码: {stock_info.get("股票代码", "N/A")}
股票名称: {stock_info.get("股票简称", "N/A")}
行业: {stock_info.get("行业", "N/A")}

关键财务比率:
{json.dumps(simplified_ratios, ensure_ascii=False, indent=2)}

行业对比:
{json.dumps(simplified_industry, ensure_ascii=False, indent=2)}

最近财务数据:
{json.dumps(simplified_financial_data, ensure_ascii=False, indent=2)}
"""

        # Convert to JSON format for LLM
        user_prompt = {
            "role": "user",
            "content": user_prompt_content
        }

        self.log_info("Successfully created user prompt in JSON format")
        return user_prompt

    def _simplify_financial_data(self, financial_data: Dict) -> Dict:
        """
        Simplify financial data to reduce token usage.

        Args:
            financial_data: Original financial data

        Returns:
            Simplified financial data
        """
        simplified = {}

        # Extract only the most recent period from financial indicators
        financial_indicators = financial_data.get("financial_indicators", {})
        if financial_indicators:
            # Get only the latest values for key indicators
            key_indicators = [
                "每股收益",
                "每股净资产",
                "净资产收益率",
                "营业收入",
                "净利润",
            ]
            latest_values = {}
            for indicator in key_indicators:
                if indicator in financial_indicators:
                    values = list(financial_indicators[indicator].values())
                    if values:
                        latest_values[indicator] = values[-1]  # Most recent value
            simplified["关键财务指标"] = latest_values

        # Simplify balance sheet - only show key items
        balance_sheet = financial_data.get("balance_sheet", {})
        if balance_sheet:
            key_balance_items = [
                "资产总计",
                "负债合计",
                "股东权益合计",
                "流动资产",
                "流动负债",
            ]
            latest_balance = {}
            for item in key_balance_items:
                if item in balance_sheet:
                    values = list(balance_sheet[item].values())
                    if values:
                        latest_balance[item] = values[-1]
            simplified["资产负债表关键项目"] = latest_balance

        # Simplify income statement - only show key items
        income_statement = financial_data.get("income_statement", {})
        if income_statement:
            key_income_items = ["营业收入", "营业成本", "净利润", "营业利润"]
            latest_income = {}
            for item in key_income_items:
                if item in income_statement:
                    values = list(income_statement[item].values())
                    if values:
                        latest_income[item] = values[-1]
            simplified["利润表关键项目"] = latest_income

        return simplified

    def _simplify_financial_ratios(self, financial_ratios: Dict) -> Dict:
        """
        Simplify financial ratios to only show key metrics.

        Args:
            financial_ratios: Original financial ratios

        Returns:
            Simplified financial ratios
        """
        # Keep only the most important ratios
        key_ratios = [
            "roe",
            "roa",
            "gross_margin",
            "net_margin",
            "current_ratio",
            "quick_ratio",
            "debt_to_equity",
            "asset_turnover",
            "revenue_growth",
            "earnings_growth",
        ]

        simplified = {}
        for ratio in key_ratios:
            if ratio in financial_ratios:
                simplified[ratio] = financial_ratios[ratio]

        return simplified

    def _simplify_industry_info(self, industry_info: Dict) -> Dict:
        """
        Simplify industry information.

        Args:
            industry_info: Original industry information

        Returns:
            Simplified industry information
        """
        simplified = {}

        # Keep only essential industry info
        if "industry" in industry_info:
            simplified["行业"] = industry_info["industry"]

        if "industry_averages" in industry_info:
            # Only keep key industry averages
            key_averages = ["roe", "pe", "debt_to_equity"]
            industry_avgs = industry_info["industry_averages"]
            simplified_avgs = {}
            for avg in key_averages:
                if avg in industry_avgs:
                    simplified_avgs[avg] = industry_avgs[avg]
            simplified["行业平均水平"] = simplified_avgs

        return simplified

    def get_llm_analysis(self, user_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get analysis from LLM using JSON format prompts.

        Args:
            user_prompt: User prompt in JSON format

        Returns:
            Dictionary with analysis results
        """
        try:
            # Load system prompt in JSON format
            system_prompt = self._load_system_prompt()

            # Log the prompts being sent to LLM
            self.log_info(f"System prompt loaded: {system_prompt['content'][:100]}...")
            self.log_info(f"User prompt content: {user_prompt['content'][:200]}...")

            # LLM Configuration details
            api_url = self.llm_config["api_url"]
            api_key = self.llm_config["api_key"]
            # Model is part of the URL for Gemini API
            pass
            timeout = self.llm_config["timeout"]

            self.log_info(f"Calling LLM API at {api_url} for fundamental analysis")

            # Prepare the request for LLM API
            headers = {"Content-Type": "application/json"}

            # Prepare payload based on provider
            provider = self.llm_config.get("provider", "google")

            if provider == "google":  # Gemini API
                # For Gemini, we need to combine system and user prompts
                combined_content = f"{system_prompt['content']}\n\n{user_prompt['content']}"
                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "text": combined_content
                                }
                            ],
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 2000,
                    },
                }
                api_url_with_key = f"{api_url}?key={api_key}"
            elif provider in [
                "deepseek",
                "qwen",
                "openai",
                "ollama",
            ]:  # OpenAI-compatible APIs
                # For OpenAI-compatible APIs, we can use separate system and user messages
                payload = {
                    "model": self.llm_config.get("model", "deepseek-chat"),
                    "messages": [
                        system_prompt,
                        user_prompt
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000,
                }
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                api_url_with_key = api_url
            else:
                # Default to OpenAI-compatible format for most LLM APIs
                payload = {
                    "model": self.llm_config.get("model", "default"),
                    "messages": [
                        system_prompt,
                        user_prompt
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000,
                }
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                api_url_with_key = api_url

            # Log the payload being sent
            self.log_info(f"Sending payload to LLM API with {len(payload.get('messages', []))} messages")

            # 输出用户提示词到控制台，参考增强舆情分析策略v2的实现方式
            user_prompt_content = ""
            for msg in payload.get("messages", []):
                if msg.get('role') == 'user':
                    user_prompt_content = msg.get('content', '')
                    break

            if user_prompt_content:
                print(f"\n=== 用户提示词 (股票基本面分析) ===")
                print(user_prompt_content)
                print("=== 用户提示词结束 ===\n")

            # Send request to LLM API
            response = requests.post(
                api_url_with_key,
                headers=headers,
                json=payload,
                timeout=timeout,
            )

            if response.status_code == 200:
                response_data = response.json()

                # Extract content based on provider
                provider = self.llm_config.get("provider", "google")

                if provider == "google":
                    # Google Gemini format
                    content = response_data["candidates"][0]["content"]["parts"][0][
                        "text"
                    ]
                else:
                    # OpenAI-compatible format (deepseek, qwen, openai, ollama, etc.)
                    content = response_data["choices"][0]["message"]["content"]

                # Log the response content
                self.log_info(f"Received LLM response: {content[:200]}...")

                # Display LLM response content in console
                print(f"\n=== LLM Response Content ===")
                print(f"Content length: {len(content)} characters")
                print(f"Content:\n{content}")
                print("=== LLM Response End ===\n")

                # Filter out think content from the response
                # Remove <think> tags and their content
                import re

                # More comprehensive think content filtering
                # First try to remove the entire think block
                think_patterns = [
                    r'<think>.*?</think>',  # Standard think tags
                    r'首先，我需要.*?\n\n',  # Chinese think patterns
                    r'首先.*?\n\n',
                    r'<think>.*?(?=\n\n|$)',  # Think content until double newline or end
                    r'首先.*?(?=\n\n|$)'  # Chinese think until double newline or end
                ]

                for pattern in think_patterns:
                    content = re.sub(pattern, '', content, flags=re.DOTALL)

                # Also remove any remaining think-related text
                content = re.sub(r'^\s*<think>\s*', '', content)
                content = re.sub(r'\s*</think>\s*$', '', content)

                # Remove any leading/trailing whitespace
                content = content.strip()

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

                    # Try to parse the main JSON response
                    analysis_result = json.loads(content)
                    self.log_info("Successfully parsed LLM JSON response")

                    # Extract score and value from LLM response
                    llm_score = float(analysis_result.get("score", 0))
                    llm_value = analysis_result.get(
                        "value", analysis_result.get("analysis", content)
                    )

                    # For the new JSON format, we need to store the entire JSON as value
                    # and extract just the score for the score field
                    llm_value = json.dumps(analysis_result, ensure_ascii=False)

                    # Handle case where the value field itself contains a nested JSON object
                    # This can happen when the LLM returns a JSON string in the value field
                    if isinstance(llm_value, str):
                        try:
                            # Try to parse the value field as JSON
                            nested_result = json.loads(llm_value)
                            if isinstance(nested_result, dict):
                                # If it's a nested structure, extract the actual value and score
                                if "value" in nested_result:
                                    llm_value = nested_result["value"]
                                # Use the nested score if available, even if main score is not default
                                if "score" in nested_result:
                                    try:
                                        nested_score = float(nested_result["score"])
                                        # Ensure score is in valid range [0, 1]
                                        llm_score = max(0.0, min(1.0, nested_score))
                                    except (ValueError, TypeError):
                                        pass  # Keep original score if parsing fails
                        except json.JSONDecodeError:
                            # If parsing fails, keep the original value
                            # But try one more approach - check if the value looks like a JSON string
                            if llm_value.strip().startswith(
                                "{"
                            ) and llm_value.strip().endswith("}"):
                                try:
                                    # Try to fix common JSON issues and parse again
                                    fixed_value = self._fix_json_string(llm_value)
                                    nested_result = json.loads(fixed_value)
                                    if isinstance(nested_result, dict):
                                        if "value" in nested_result:
                                            llm_value = nested_result["value"]
                                        # Use the nested score if available, even if main score is not default
                                        if "score" in nested_result:
                                            try:
                                                nested_score = float(
                                                    nested_result["score"]
                                                )
                                                # Ensure score is in valid range [0, 1]
                                                llm_score = max(
                                                    0.0, min(1.0, nested_score)
                                                )
                                            except (ValueError, TypeError):
                                                pass  # Keep original score if parsing fails
                                except json.JSONDecodeError:
                                    pass

                    # Validate consistency between score field and score mentioned in value text
                    import re

                    score_matches = re.findall(
                        r"(?:评分|score)[:：]?\s*(\d+\.?\d*)",
                        str(llm_value),
                        re.IGNORECASE,
                    )
                    if score_matches:
                        try:
                            extracted_score = float(score_matches[0])
                            # Check if both scores are in the same range
                            if 0 <= llm_score <= 1 and 0 <= extracted_score <= 1:
                                # Both in 0-1 range, check for significant difference
                                if abs(llm_score - extracted_score) > 0.01:
                                    self.log_warning(
                                        f"Score inconsistency in 0-1 range: score field={llm_score}, value text mentions={extracted_score}"
                                    )
                            elif 0 <= llm_score <= 100 and 0 <= extracted_score <= 100:
                                # Both in 0-100 range, check for significant difference
                                if abs(llm_score - extracted_score) > 1:
                                    self.log_warning(
                                        f"Score inconsistency in 0-100 range: score field={llm_score}, value text mentions={extracted_score}"
                                    )
                                    # Normalize 0-100 range score to 0-1 range
                                    llm_score = max(0.0, min(1.0, llm_score / 100.0))
                            # If ranges are different, log warning but keep score field value
                            elif (
                                0 <= llm_score <= 1 and 0 <= extracted_score <= 100
                            ) or (0 <= llm_score <= 100 and 0 <= extracted_score <= 1):
                                self.log_warning(
                                    f"Score range mismatch: score field={llm_score}, value text mentions={extracted_score}"
                                )
                                # If score field is in 0-100 range, normalize it
                                if llm_score > 1:
                                    llm_score = max(0.0, min(1.0, llm_score / 100.0))
                        except ValueError:
                            pass  # If we can't parse the extracted score, ignore it

                    return {
                        "score": llm_score,
                        "value": llm_value,
                    }
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract information from raw content
                    self.log_warning(
                        "Failed to parse LLM JSON response, attempting to extract from raw content"
                    )

                    # Try to extract score and value from raw content even when JSON parsing fails
                    llm_score = 0.0  # Default score
                    llm_value = content

                    # Try to extract score from raw content using regex
                    import re

                    score_matches = re.findall(
                        r"(?:评分|score)[:：]?\s*(\d+\.?\d*)", content, re.IGNORECASE
                    )
                    if score_matches:
                        try:
                            extracted_score = float(score_matches[0])
                            # If score is in 0-100 range, normalize to 0-1 range
                            if 0 <= extracted_score <= 100:
                                llm_score = max(0.0, min(1.0, extracted_score / 100.0))
                            elif 0 <= extracted_score <= 1:
                                llm_score = extracted_score
                        except ValueError:
                            pass  # If we can't parse the extracted score, keep default

                    # Try to extract value/content from raw content
                    # Look for common patterns in LLM responses to extract just the analysis text
                    value_patterns = [
                        r"综合考虑以上因素，我给出的基本面评分是[\d.]+。(.*)",
                        r"综合考虑以上因素，我给出的基本面评分是[\d.]+。这个评分反映了.*?不足。(.*?)(?:\n\n|$)",
                        r"综合考虑以上因素，我给出的基本面评分是[\d.]+。这个评分反映了.*?不足。(.*)$",
                    ]

                    for pattern in value_patterns:
                        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                        if match:
                            extracted_value = match.group(1).strip()
                            if extracted_value:
                                llm_value = extracted_value
                                break

                    # Try nested JSON parsing on raw content as well
                    try:
                        # Check if the raw content looks like a JSON string
                        stripped_content = content.strip()
                        if stripped_content.startswith(
                            "{"
                        ) and stripped_content.endswith("}"):
                            # Try to fix common JSON issues and parse
                            fixed_content = self._fix_json_string(stripped_content)
                            nested_result = json.loads(fixed_content)
                            if isinstance(nested_result, dict):
                                # Extract score if available
                                if "score" in nested_result:
                                    try:
                                        extracted_score = float(nested_result["score"])
                                        if 0 <= extracted_score <= 100:
                                            llm_score = max(
                                                0.0, min(1.0, extracted_score / 100.0)
                                            )
                                        elif 0 <= extracted_score <= 1:
                                            llm_score = extracted_score
                                    except ValueError:
                                        pass

                                # Extract value if available
                                if "value" in nested_result:
                                    llm_value = nested_result["value"]
                                elif "analysis" in nested_result:
                                    llm_value = nested_result["analysis"]

                                # Handle nested JSON in value field
                                if isinstance(llm_value, str):
                                    try:
                                        nested_value_result = json.loads(llm_value)
                                        if (
                                            isinstance(nested_value_result, dict)
                                            and "value" in nested_value_result
                                        ):
                                            llm_value = nested_value_result["value"]
                                            # Also check for score in the nested value
                                            if "score" in nested_value_result:
                                                try:
                                                    nested_score = float(
                                                        nested_value_result["score"]
                                                    )
                                                    if 0 <= nested_score <= 100:
                                                        llm_score = max(
                                                            0.0,
                                                            min(
                                                                1.0,
                                                                nested_score / 100.0,
                                                            ),
                                                        )
                                                    elif 0 <= nested_score <= 1:
                                                        llm_score = nested_score
                                                except ValueError:
                                                    pass
                                    except json.JSONDecodeError:
                                        pass
                    except json.JSONDecodeError:
                        pass  # If nested parsing fails, keep the current values

                    return {
                        "score": llm_score,
                        "value": llm_value,
                    }
            else:
                self.log_error(
                    f"LLM API error: {response.status_code} - {response.text}"
                )
                return {
                    "score": 0.0,
                    "value": f"LLM分析失败: HTTP {response.status_code}",
                }

        except requests.exceptions.Timeout:
            self.log_error("LLM API request timed out")
            return {"score": 0.0, "value": "LLM分析失败: 请求超时"}
        except Exception as e:
            self.log_error(f"Error getting LLM analysis: {e}")
            return {"score": 0.0, "value": f"LLM分析失败: {str(e)}"}

    def _create_fallback_analysis(self, stock_code: str, financial_ratios: Dict, industry_info: Dict) -> Dict[str, Any]:
        """
        Create a fallback analysis when LLM fails to return proper JSON.

        Args:
            stock_code: Stock code
            financial_ratios: Calculated financial ratios
            industry_info: Industry information

        Returns:
            Dictionary with fallback analysis results
        """
        self.log_warning(f"Creating fallback analysis for stock {stock_code}")

        # Calculate a simple score based on financial ratios
        score = 0.0
        reasons = []

        # Check profitability
        roe = financial_ratios.get("roe", 0)
        if roe > 0.15:
            score += 0.3
            reasons.append("ROE较高")
        elif roe > 0.08:
            score += 0.2
            reasons.append("ROE中等")
        else:
            score += 0.1
            reasons.append("ROE较低")

        # Check growth
        revenue_growth = financial_ratios.get("revenue_growth", 0)
        if revenue_growth > 0:
            score += 0.2
            reasons.append("收入增长")
        else:
            score += 0.1
            reasons.append("收入下降")

        # Check debt
        debt_to_equity = financial_ratios.get("debt_to_equity", 0)
        if debt_to_equity < 0.5:
            score += 0.2
            reasons.append("负债率低")
        elif debt_to_equity < 1.0:
            score += 0.15
            reasons.append("负债率中等")
        else:
            score += 0.1
            reasons.append("负债率高")

        # Check liquidity
        current_ratio = financial_ratios.get("current_ratio", 0)
        if current_ratio > 1.5:
            score += 0.2
            reasons.append("流动性好")
        elif current_ratio > 1.0:
            score += 0.15
            reasons.append("流动性中等")
        else:
            score += 0.1
            reasons.append("流动性差")

        # Check efficiency
        asset_turnover = financial_ratios.get("asset_turnover", 0)
        if asset_turnover > 0.5:
            score += 0.1
            reasons.append("资产效率高")
        else:
            score += 0.05
            reasons.append("资产效率低")

        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))

        # Create fallback JSON structure
        fallback_json = {
            "score": score,
            "reason": "，".join(reasons),
            "details": {
                "profitability": {
                    "score": max(0.0, min(1.0, roe * 5)),
                    "reason": f"ROE: {roe:.2%}"
                },
                "solvency": {
                    "score": max(0.0, min(1.0, 1 - debt_to_equity / 2)),
                    "reason": f"负债权益比: {debt_to_equity:.2f}"
                },
                "efficiency": {
                    "score": max(0.0, min(1.0, asset_turnover * 2)),
                    "reason": f"资产周转率: {asset_turnover:.2f}"
                },
                "growth": {
                    "score": max(0.0, min(1.0, 0.5 + revenue_growth / 2)),
                    "reason": f"收入增长率: {revenue_growth:.2%}"
                },
                "industry_comparison": {
                    "score": 0.5,
                    "reason": "行业对比数据不足"
                },
                "risk": {
                    "score": 0.5,
                    "reason": "风险因素分析数据不足"
                }
            },
            "weights": {
                "profitability": 0.25,
                "solvency": 0.15,
                "efficiency": 0.15,
                "growth": 0.2,
                "industry_comparison": 0.15,
                "risk": 0.1
            },
            "confidence_level": 0.6,
            "analysis_summary": f"基于财务比率的自动分析，{reasons[-1] if reasons else '数据不足'}",
            "recommendation": "买入" if score > 0.7 else "卖出" if score < 0.3 else "观望",
            "risk_factors": ["LLM分析失败", "使用自动分析"],
            "key_strengths": ["财务数据可用", "自动评分"]
        }

        return {
            "score": score,
            "value": json.dumps(fallback_json, ensure_ascii=False)
        }

    def _fix_json_string(self, json_string: str) -> str:
        """
        Fix common JSON formatting issues in a JSON string.

        Args:
            json_string: The JSON string to fix

        Returns:
            Fixed JSON string
        """
        if not isinstance(json_string, str):
            return json_string

        # Fix common escape sequence issues
        fixed = (
            json_string.replace("\\n", "\\n")
            .replace("\\t", "\\t")
            .replace("\\r", "\\r")
        )

        # Fix unescaped quotes inside strings
        # This is a simple approach - in a real implementation, you'd want a more sophisticated parser
        lines = fixed.split("\n")
        in_string = False
        quote_char = None
        result = []

        for line in lines:
            new_line = ""
            i = 0
            while i < len(line):
                char = line[i]

                if not in_string:
                    if char in ['"', "'"]:
                        in_string = True
                        quote_char = char
                else:
                    if char == quote_char:
                        # Check if it's escaped
                        if i > 0 and line[i - 1] != "\\":
                            in_string = False
                            quote_char = None
                    elif (
                        char == '"'
                        and quote_char == '"'
                        and i > 0
                        and line[i - 1] != "\\"
                    ):
                        # Unescaped double quote inside double-quoted string
                        char = '\\"'

                new_line += char
                i += 1

            result.append(new_line)

        return "\n".join(result)

    def execute(
        self, stock_data: Dict[str, pd.DataFrame], agent_name: str, db_manager
    ) -> List[Dict]:
        """
        Execute the LLM fundamental strategy.

        Args:
            stock_data: Dictionary mapping stock codes to DataFrames with stock data
            agent_name: Name of the agent executing this strategy
            db_manager: Database manager instance

        Returns:
            List of selected stocks with analysis results
        """
        self.log_info("Executing LLM Fundamental Strategy")

        # Suppressing unused parameter warnings
        _ = agent_name
        _ = db_manager

        selected_stocks = []

        # Process each stock
        for stock_code in stock_data.keys():
            try:
                self.log_info(f"Analyzing stock {stock_code} with LLM")

                # Perform fundamental analysis using LLM
                analysis_result = self.analyze_stock_fundamentals(stock_code)

                # Create result entry
                result = {
                    "code": stock_code,
                    "score": analysis_result[
                        "score"
                    ],  # Already in 0-1 range as requested in prompt
                    "value": analysis_result["value"],
                    "selection_reason": f"LLM基本面分析评分: {analysis_result['score']}",
                }

                selected_stocks.append(result)
                self.log_info(f"Completed analysis for stock {stock_code}")

            except Exception as e:
                self.log_error(f"Error processing stock {stock_code}: {e}")
                continue

        # Sort stocks by score in descending order
        selected_stocks.sort(key=lambda x: x["score"], reverse=True)

        self.log_info(
            f"LLM Fundamental Strategy completed. Analyzed {len(selected_stocks)} stocks"
        )
        return selected_stocks

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on input data.

        Args:
            data: Input data DataFrame with required columns

        Returns:
            DataFrame with signals
        """
        # For this strategy, we're focusing on fundamental analysis rather than technical signals
        signals = data.copy()
        signals["signal"] = "HOLD"  # Default signal
        signals["score"] = 0.0  # Default score

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
        # For fundamental strategy, we might use a different position sizing approach
        if signal == "BUY":
            # Example: Use a fixed percentage of portfolio for each stock
            position_percentage = 0.02  # 2% of portfolio
            position_value = portfolio_value * position_percentage
            return position_value / price if price > 0 else 0
        else:
            return 0.0


# Example usage
if __name__ == "__main__":
    # This is just a placeholder to make the file importable
    pass
