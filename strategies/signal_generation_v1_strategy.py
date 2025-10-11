"""
信号生成V1 Strategy
A strategy that analyzes existing strategy results in the pool to generate new signals.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import sys
import os
import requests
import json
from strategies.base_strategy import BaseStrategy
import logging
from datetime import datetime
from bson import ObjectId
from config.mongodb_config import MongoDBConfig
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class SignalGenerationV1Strategy(BaseStrategy):
    """
    信号生成V1 Strategy
    Analyzes existing strategy results in the pool to generate new signals:
    1. Count how many strategies each stock satisfies
    2. Calculate average score (score_calc)
    3. Determine signal based on average score (signal_calc)
    4. Use AI to analyze scores and values to generate AI-based score and signal (score_ai, signal_ai)
    """

    def __init__(self, name: str = "信号生成V1", params: Optional[Dict] = None):
        """
        Initialize the 信号生成V1 strategy.

        Args:
            name: Strategy name
            params: Strategy parameters
        """
        super().__init__(name, params or {})

        # Get LLM configuration name from strategy parameters
        self.llm_name = self.params.get("llm_name", "")

        # Load LLM configuration from database
        self.llm_config = self._load_llm_config_from_db(self.llm_name)

        self.logger.info(f"Initialized {self.name} strategy with LLM: {self.llm_config.get('name', 'default')}")

    def execute(self, stock_data: Dict[str, pd.DataFrame], agent_name: str, db_manager) -> List[Dict]:
        """
        Execute the strategy by analyzing existing pool data and generating new signals.

        Args:
            stock_data: Dictionary mapping stock codes to their data DataFrames (not used in this strategy)
            agent_name: Name of the agent executing this strategy
            db_manager: Database manager instance

        Returns:
            List of stocks with analysis results
        """
        self.log_info(f"Executing {self.name} strategy")

        try:
            # Get the latest pool record
            pool_collection = db_manager.db['pool']
            latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

            if not latest_pool_record:
                self.log_error("No records found in pool collection")
                return []

            # Get stocks from the latest pool record
            pool_stocks = latest_pool_record.get("stocks", [])

            if not pool_stocks:
                self.log_error("No stocks found in latest pool record")
                return []

            # Get the global strategy count from the database
            global_strategy_count = self._get_global_strategy_count(db_manager)
            self.log_info(f"Global strategy count: {global_strategy_count}")

            self.log_info(f"Analyzing {len(pool_stocks)} stocks from latest pool record")

            # Process each stock to calculate signals
            analyzed_stocks = []

            for stock in pool_stocks:
                try:
                    code = stock.get('code')
                    if not code:
                        continue

                    # Log the stock code being processed
                    self.log_info(f"Processing stock: {code}")

                    # Analyze the stock using global strategy count
                    analysis_result = self._analyze_stock(stock, global_strategy_count)

                    if analysis_result:
                        # Add code to the result
                        analysis_result['code'] = code
                        analyzed_stocks.append(analysis_result)

                except Exception as e:
                    self.log_warning(f"Error processing stock {code}: {e}")
                    continue

            self.log_info(f"Analyzed {len(analyzed_stocks)} stocks")

            # Update the latest pool record with signal generation results
            success = self._update_pool_with_signals(db_manager, analyzed_stocks)

            if success:
                self.log_info("Successfully updated pool with signal generation results")
            else:
                self.log_error("Failed to update pool with signal generation results")

            return analyzed_stocks

        except Exception as e:
            self.log_error(f"Error executing strategy: {e}")
            return []

    def _analyze_stock(self, stock: Dict, global_strategy_count: int) -> Optional[Dict]:
        """
        Analyze a single stock to calculate signals.

        Args:
            stock: Stock data from pool
            global_strategy_count: Global strategy count to use as denominator

        Returns:
            Analysis results or None if error
        """
        try:
            code = stock.get('code', '')
            self.log_info(f"[{code}] Analyzing stock with global strategy count: {global_strategy_count}")

            # Initialize counters and accumulators
            non_zero_strategy_count = 0   # Strategies with non-zero scores (for count value)
            total_score = 0.0             # Sum of all scores (including zeros)

            # Collect strategy data for AI analysis
            strategy_data = []

            # Process all fields except 'signal', 'code', and 'signals'
            for field_name, field_value in stock.items():
                # Skip non-dict fields and excluded fields
                if field_name in ['signal', 'code', 'signals'] or not isinstance(field_value, dict):
                    continue

                # Process each strategy in the field
                for strategy_name, strategy_info in field_value.items():
                    if isinstance(strategy_info, dict):
                        score = strategy_info.get('score', 0.0)
                        value = strategy_info.get('value', '')

                        # Count strategies with non-zero scores - for count value
                        try:
                            score_float = float(score) if score is not None else 0.0
                            if score_float != 0.0:
                                non_zero_strategy_count += 1
                        except (ValueError, TypeError):
                            pass  # Score is 0 if it can't be converted

                        # Accumulate all scores (including zeros)
                        try:
                            score_float = float(score) if score is not None else 0.0
                            total_score += score_float
                        except (ValueError, TypeError):
                            total_score += 0.0  # Add 0 for invalid scores

                        # Collect data for AI analysis
                        strategy_data.append({
                            'strategy': f"{field_name}_{strategy_name}",
                            'score': score,
                            'value': value
                        })

            self.log_info(f"[{code}] Processed {len(strategy_data)} strategies, {non_zero_strategy_count} with non-zero scores")

            # Calculate average score using global_strategy_count as denominator
            # (including strategies with zero scores)
            if global_strategy_count > 0:
                score_calc = total_score / global_strategy_count
            else:
                score_calc = 0.0

            # Determine signal based on average score
            if score_calc < 0.4:
                signal_calc = "卖出"
            elif score_calc <= 0.7:
                signal_calc = "持有"
            else:
                signal_calc = "买入"

            self.log_info(f"[{code}] Calculated score: {score_calc:.2f}, signal: {signal_calc}")

            # Use AI to analyze strategy data
            self.log_info(f"[{code}] Strategy data collected: {len(strategy_data)} strategies")
            if strategy_data:
                self.log_info(f"[{code}] First strategy data sample: {strategy_data[0]}")

            ai_result = self._analyze_with_ai(strategy_data)
            score_ai = ai_result.get('score_ai', 0.0)
            signal_ai = ai_result.get('signal_ai', '持有')

            self.log_info(f"[{code}] AI analysis - score: {score_ai:.2f}, signal: {signal_ai}")

            # Determine action based on new rules:
            # - If both signal_calc and signal_ai are "买入", output "买入"
            # - If either signal_calc or signal_ai is "卖出", output "卖出"
            # - Otherwise, output empty string
            if signal_calc == "买入" and signal_ai == "买入":
                action = "买入"
            elif signal_calc == "卖出" or signal_ai == "卖出":
                action = "卖出"
            else:
                action = ""

            # Create analysis result with exactly the required structure
            signal_data = {
                'counts': non_zero_strategy_count,
                'action': action,
                'score_calc': round(score_calc, 2),
                'signal_calc': signal_calc,
                'score_ai': round(score_ai, 2),
                'signal_ai': signal_ai,
                'reason_ai': ai_result.get('reasoning', '')
            }

            result = {
                'counts': non_zero_strategy_count,
                'action': action,
                'score_ai': round(score_ai, 2),
                'score_calc': round(score_calc, 2),
                'signal_calc': signal_calc,
                'signal_ai': signal_ai,
                'reason_ai': ai_result.get('reasoning', ''),
                # Keep signals structure for compatibility with pool update
                'signals': signal_data
            }

            self.log_info(f"[{code}] Analysis completed - counts: {non_zero_strategy_count}, action: '{action}'")
            return result

        except Exception as e:
            self.log_error(f"Error analyzing stock {stock.get('code', 'unknown')}: {e}")
            return None

    def _analyze_with_ai(self, strategy_data: List[Dict]) -> Dict:
        """
        Use AI to analyze strategy scores and values with LLM.

        Args:
            strategy_data: List of strategy data with scores and values

        Returns:
            AI analysis results with score_ai and signal_ai
        """
        try:
            # Handle empty data case
            if not strategy_data:
                return {'score_ai': 0.0, 'signal_ai': '持有'}

            # Use LLM for AI analysis instead of simple weighted average
            ai_result = self._analyze_with_llm(strategy_data)
            return ai_result

        except Exception as e:
            self.log_error(f"Error in AI analysis: {e}")
            # Return default values on error
            return {
                'score_ai': 0.0,
                'signal_ai': '持有',
                'reasoning': 'AI分析过程中发生错误'
            }

    def _analyze_with_llm(self, strategy_data: List[Dict]) -> Dict:
        """
        Analyze strategy data using LLM.

        Args:
            strategy_data: List of strategy data with scores and values

        Returns:
            AI analysis results with score_ai and signal_ai
        """
        try:
            # LLM Configuration details
            api_url = self.llm_config["api_url"]
            api_key = self.llm_config["api_key"]
            model = self.llm_config["model"]
            timeout = self.llm_config["timeout"]

            self.log_info(f"Calling LLM API at {api_url} for AI analysis")

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

            # Load system prompt from config file
            system_prompt = self._load_system_prompt()

            # Format strategy data as JSON string for user prompt
            user_prompt = self._format_stock_data_for_llm(strategy_data)

            # Log user prompt to console
            self.log_info(f"User prompt for LLM analysis:\n{user_prompt}")

            # Prepare payload based on provider
            if provider == "google":  # Gemini API
                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "text": system_prompt + "\n\n" + user_prompt
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
                            "content": system_prompt,
                        },
                        {"role": "user", "content": user_prompt},
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
                            "content": system_prompt,
                        },
                        {"role": "user", "content": user_prompt},
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
                    score_ai = float(
                        analysis_result.get("score_ai", 0.5)
                    )
                    signal_ai = analysis_result.get(
                        "signal_ai", "持有"
                    )
                    reasoning = analysis_result.get(
                        "reasoning", content
                    )

                    self.log_info(
                        "Successfully received LLM AI analysis response"
                    )
                    return {
                        'score_ai': round(max(0.0, min(1.0, score_ai)), 2),  # Normalize to 0-1 range and round to 2 decimal places
                        'signal_ai': signal_ai,
                        'reasoning': reasoning
                    }
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract score and signal from content
                    self.log_warning(
                        "Failed to parse LLM JSON response, extracting score and signal from content"
                    )
                    # Simple extraction of score and signal from content
                    import re

                    score_match = re.search(
                        r'"score_ai"\s*:\s*(\d+\.?\d*)', content
                    )
                    signal_match = re.search(
                        r'"signal_ai"\s*:\s*"([^"]+)"', content
                    )

                    score_ai = 0.5  # Default neutral score
                    signal_ai = "持有"  # Default signal

                    if score_match:
                        score_ai = float(score_match.group(1))
                        score_ai = max(
                            0.0, min(1.0, score_ai)
                        )  # Clamp to 0-1 range

                    if signal_match:
                        signal_ai = signal_match.group(1)
                        # Validate signal
                        if signal_ai not in ["买入", "持有", "卖出"]:
                            signal_ai = "持有"  # Default to hold if invalid

                    return {
                        'score_ai': round(score_ai, 2),
                        'signal_ai': signal_ai,
                        'reasoning': content,
                    }
            else:
                self.log_error(
                    f"LLM API error: {response.status_code} - {response.text}"
                )
                raise Exception(f"LLM API error: {response.status_code}")

        except requests.exceptions.Timeout:
            self.log_error("LLM API request timed out")
            return {"score_ai": 0.0, "signal_ai": "持有", "reasoning": "LLM分析失败: 请求超时"}
        except Exception as e:
            self.log_error(
                f"Error getting LLM AI analysis: {e}"
            )
            return {"score_ai": 0.0, "signal_ai": "持有", "reasoning": f"LLM分析失败: {str(e)}"}

    def _format_stock_data_for_llm(self, strategy_data: List[Dict]) -> str:
        """
        Format strategy data for LLM analysis

        Args:
            strategy_data: List of strategy data dictionaries with scores and values

        Returns:
            JSON string for LLM analysis
        """
        try:
            # Format the strategy data for LLM analysis
            formatted_data = {
                "strategies": strategy_data
            }

            # Convert to JSON string
            json_string = json.dumps(formatted_data, ensure_ascii=False, indent=2)

            return json_string

        except Exception as e:
            self.log_error(f"Error formatting strategy data for LLM: {e}")
            return "{}"

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on input data.
        Not used in this strategy as it analyzes pool data instead.

        Args:
            data: Input data DataFrame with required columns

        Returns:
            DataFrame with signals
        """
        # For this strategy, we don't generate signals from price data
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 'HOLD'
        signals['position'] = 0.0
        return signals

    def calculate_position_size(self, signal: str, portfolio_value: float,
                              price: float) -> float:
        """
        Calculate position size based on signal.

        Args:
            signal: Trading signal ('买入', '卖出', '持有')
            portfolio_value: Current portfolio value
            price: Current asset price

        Returns:
            Position size (number of shares)
        """
        if signal == '买入':
            # Allocate 10% of portfolio value for buy signals
            return (portfolio_value * 0.1) / price
        elif signal == '卖出':
            # Sell all holdings (in practice, this would depend on current holdings)
            return -100.0  # Placeholder
        else:
            return 0.0

    def _get_global_strategy_count(self, db_manager) -> int:
        """
        Get the global strategy count from the latest pool record.
        This counts the actual strategies that have contributed data to the pool.

        Args:
            db_manager: Database manager instance

        Returns:
            int: Count of strategies that have contributed data to the pool
        """
        try:
            # Get the latest pool record
            pool_collection = db_manager.db['pool']
            latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

            if not latest_pool_record:
                self.log_error("No records found in pool collection")
                return 0

            # Get stocks from the latest pool record
            pool_stocks = latest_pool_record.get("stocks", [])

            if not pool_stocks:
                self.log_error("No stocks found in latest pool record")
                return 0

            # Count strategies from the first stock (all stocks should have the same strategy structure)
            first_stock = pool_stocks[0]
            strategy_count = 0

            # Process all fields except 'signal', 'code', and 'signals'
            for field_name, field_value in first_stock.items():
                # Skip non-dict fields and excluded fields
                if field_name in ['signal', 'code', 'signals'] or not isinstance(field_value, dict):
                    continue

                # Count strategies in this field
                strategy_count += len(field_value)

            self.log_info(f"Found {strategy_count} strategies in latest pool record")
            return strategy_count

        except Exception as e:
            self.log_error(f"Error getting global strategy count: {e}")
            return 0

    def _update_pool_with_signals(self, db_manager, analyzed_stocks: List[Dict]) -> bool:
        """
        Update the latest pool record with signal generation results.

        Args:
            db_manager: Database manager instance
            analyzed_stocks: List of analyzed stocks with signal data

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Get pool collection
            collection = db_manager.db["pool"]

            # Find the latest pool record
            latest_pool_record = collection.find_one(sort=[("_id", -1)])

            if not latest_pool_record:
                self.log_error("No records found in pool collection")
                return False

            # Get existing stocks from the latest record
            existing_stocks = latest_pool_record.get("stocks", [])

            # Create a mapping of analyzed stocks by code for easy lookup
            analyzed_stock_map = {stock.get("code"): stock for stock in analyzed_stocks}

            # Update signal data for existing stocks
            for existing_stock in existing_stocks:
                code = existing_stock.get("code")
                if code in analyzed_stock_map:
                    analyzed_stock = analyzed_stock_map[code]

                    # Add signals field to the existing stock if it doesn't exist
                    if "signals" not in existing_stock:
                        existing_stock["signals"] = {}

                    # Create the proper structure for our strategy signals
                    # Format: {"信号生成V1": {counts, action, score_calc, signal_calc, score_ai, signal_ai, reason_ai}}
                    signal_data = {
                        "counts": analyzed_stock.get("counts", 0),
                        "action": analyzed_stock.get("action", ""),
                        "score_calc": round(analyzed_stock.get("score_calc", 0.0), 2),
                        "signal_calc": analyzed_stock.get("signal_calc", "持有"),
                        "score_ai": round(analyzed_stock.get("score_ai", 0.0), 2),
                        "signal_ai": analyzed_stock.get("signal_ai", "持有"),
                        "reason_ai": analyzed_stock.get("reason_ai", "")
                    }

                    # Add our strategy signals with the correct structure
                    existing_stock["signals"][self.name] = signal_data

            # Update the latest pool record with modified stocks
            result = collection.update_one(
                {"_id": latest_pool_record["_id"]},
                {
                    "$set": {
                        "stocks": existing_stocks,
                        "signals_at": datetime.now(),
                    }
                },
            )

            if result.modified_count > 0:
                self.log_info(
                    f"Updated latest pool record with {len(analyzed_stocks)} signal generation stocks"
                )
            else:
                self.log_info("No changes made to the latest pool record")

            return True

        except Exception as e:
            self.log_error(
                f"Error updating latest pool record with signal generation: {e}"
            )
            return False

    def get_strategy_count(self, stock_data: Dict) -> int:
        """
        Get the total count of strategies across all stocks in the provided data.

        Args:
            stock_data: Dictionary containing stock data from pool

        Returns:
            int: Total count of strategies
        """
        total_strategies = 0

        # Process each stock to count strategies
        for stock in stock_data.get("stocks", []):
            # Process all fields except 'signal', 'code', and 'signals'
            for field_name, field_value in stock.items():
                # Skip non-dict fields and excluded fields
                if field_name in ['signal', 'code', 'signals'] or not isinstance(field_value, dict):
                    continue

                # Process each strategy in the field
                for strategy_name, strategy_info in field_value.items():
                    if isinstance(strategy_info, dict):
                        total_strategies += 1

        return total_strategies


    def _load_llm_config_from_db(self, config_name: Optional[str] = None) -> Dict[str, any]:
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

                # If a specific config name is provided, find it
                if config_name:
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

                # If not found or no specific config name, use the first one
                if llm_configs:
                    if config_name:
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

    def _load_system_prompt(self) -> str:
        """
        Load system prompt from config/signal_sys_prompt.md file.

        Returns:
            System prompt string
        """
        try:
            prompt_file_path = "config/signal_sys_prompt.md"
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read().strip()
            self.log_info("Successfully loaded system prompt from config/signal_sys_prompt.md")
            return system_prompt
        except Exception as e:
            self.log_error(f"Error loading system prompt from config/signal_sys_prompt.md: {e}")
            # Fallback to default system prompt
            return "你是一个专业的股票信号生成分析师，请根据提供的多策略数据进行综合分析。请严格按照以下JSON格式输出你的分析结果：{\"score_ai\": 0.75, \"signal_ai\": \"买入\", \"reasoning\": \"详细的分析理由...\"}"

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
    import logging

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # This strategy doesn't need sample data as it works with pool data
    print("信号生成V1 Strategy - Analyzes existing pool data to generate signals")

