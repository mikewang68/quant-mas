"""
信号生成V1 Strategy
A strategy that analyzes existing strategy results in the pool to generate new signals.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from strategies.base_strategy import BaseStrategy
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


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
                    
                    # Add signals field to the existing stock
                    if "signals" not in existing_stock:
                        existing_stock["signals"] = {}
                    
                    # Add our strategy signals
                    existing_stock["signals"][self.name] = analyzed_stock.get("signals", {})

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

        self.logger.info(f"Initialized {self.name} strategy")

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

            self.log_info(f"Analyzing {len(pool_stocks)} stocks from latest pool record")

            # Process each stock to calculate signals
            analyzed_stocks = []

            for stock in pool_stocks:
                try:
                    code = stock.get('code')
                    if not code:
                        continue

                    # Analyze the stock
                    analysis_result = self._analyze_stock(stock)

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

    def _analyze_stock(self, stock: Dict) -> Optional[Dict]:
        """
        Analyze a single stock to calculate signals.

        Args:
            stock: Stock data from pool

        Returns:
            Analysis results or None if error
        """
        try:
            code = stock.get('code', '')

            # Initialize counters and accumulators
            strategy_count = 0  # Number of strategies satisfied
            total_score = 0.0   # Sum of scores
            valid_scores = 0    # Number of valid scores

            # Collect strategy data for AI analysis
            strategy_data = []

            # Check tech field
            if 'tech' in stock and isinstance(stock['tech'], dict):
                for strategy_name, strategy_info in stock['tech'].items():
                    if isinstance(strategy_info, dict):
                        score = strategy_info.get('score', 0.0)
                        value = strategy_info.get('value', '')

                        # Count valid strategies (where score > 0)
                        if score and float(score) > 0:
                            strategy_count += 1

                        # Accumulate scores (use 0 for None/empty scores)
                        try:
                            score_float = float(score) if score is not None else 0.0
                            total_score += score_float
                            valid_scores += 1
                        except (ValueError, TypeError):
                            total_score += 0.0
                            valid_scores += 1  # Still count as valid for averaging

                        # Collect data for AI analysis
                        strategy_data.append({
                            'strategy': f"tech_{strategy_name}",
                            'score': score,
                            'value': value
                        })

            # Check fund field
            if 'fund' in stock and isinstance(stock['fund'], dict):
                for strategy_name, strategy_info in stock['fund'].items():
                    if isinstance(strategy_info, dict):
                        score = strategy_info.get('score', 0.0)
                        value = strategy_info.get('value', '')

                        # Count valid strategies (where score > 0)
                        if score and float(score) > 0:
                            strategy_count += 1

                        # Accumulate scores (use 0 for None/empty scores)
                        try:
                            score_float = float(score) if score is not None else 0.0
                            total_score += score_float
                            valid_scores += 1
                        except (ValueError, TypeError):
                            total_score += 0.0
                            valid_scores += 1  # Still count as valid for averaging

                        # Collect data for AI analysis
                        strategy_data.append({
                            'strategy': f"fund_{strategy_name}",
                            'score': score,
                            'value': value
                        })

            # Check pub field
            if 'pub' in stock and isinstance(stock['pub'], dict):
                for strategy_name, strategy_info in stock['pub'].items():
                    if isinstance(strategy_info, dict):
                        score = strategy_info.get('score', 0.0)
                        value = strategy_info.get('value', '')

                        # Count valid strategies (where score > 0)
                        if score and float(score) > 0:
                            strategy_count += 1

                        # Accumulate scores (use 0 for None/empty scores)
                        try:
                            score_float = float(score) if score is not None else 0.0
                            total_score += score_float
                            valid_scores += 1
                        except (ValueError, TypeError):
                            total_score += 0.0
                            valid_scores += 1  # Still count as valid for averaging

                        # Collect data for AI analysis
                        strategy_data.append({
                            'strategy': f"pub_{strategy_name}",
                            'score': score,
                            'value': value
                        })

            # Calculate average score
            if valid_scores > 0:
                score_calc = total_score / valid_scores
            else:
                score_calc = 0.0

            # Determine signal based on average score
            if score_calc < 0.4:
                signal_calc = "卖出"
            elif score_calc <= 0.7:
                signal_calc = "持有"
            else:
                signal_calc = "买入"

            # Use AI to analyze strategy data (placeholder implementation)
            ai_result = self._analyze_with_ai(strategy_data)
            score_ai = ai_result.get('score_ai', 0.0)
            signal_ai = ai_result.get('signal_ai', '持有')

            # Create analysis result
            result = {
                'selection_reason': f"满足{strategy_count}个策略，计算得分:{score_calc:.2f}，AI得分:{score_ai:.2f}",
                'score': score_calc,  # Use calculated score as main score
                'value': {
                    'count': strategy_count,
                    'score_calc': round(score_calc, 4),
                    'signal_calc': signal_calc,
                    'score_ai': round(score_ai, 4),
                    'signal_ai': signal_ai,
                    'strategy_details': strategy_data
                },
                'technical_analysis': {
                    'strategy_count': strategy_count,
                    'average_score': round(score_calc, 4),
                    'calculated_signal': signal_calc,
                    'ai_score': round(score_ai, 4),
                    'ai_signal': signal_ai
                },
                'signals': {
                    'score': round(score_calc, 4),
                    'value': {
                        'count': strategy_count,
                        'score_calc': round(score_calc, 4),
                        'signal_calc': signal_calc,
                        'score_ai': round(score_ai, 4),
                        'signal_ai': signal_ai
                    }
                }
            }

            return result

        except Exception as e:
            self.log_error(f"Error analyzing stock {stock.get('code', 'unknown')}: {e}")
            return None

    def _analyze_with_ai(self, strategy_data: List[Dict]) -> Dict:
        """
        Use AI to analyze strategy scores and values.

        Args:
            strategy_data: List of strategy data with scores and values

        Returns:
            AI analysis results with score_ai and signal_ai
        """
        try:
            # This is a placeholder implementation
            # In a real implementation, this would:
            # 1. Get AI configuration from database
            # 2. Call AI service with strategy_data
            # 3. Parse AI response to extract score_ai and signal_ai

            # For now, we'll use a simple heuristic-based approach
            if not strategy_data:
                return {'score_ai': 0.0, 'signal_ai': '持有'}

            # Calculate a weighted average based on scores
            total_weighted_score = 0.0
            total_weight = 0.0

            for data in strategy_data:
                try:
                    score = float(data.get('score', 0.0)) if data.get('score') is not None else 0.0
                    # Use score as weight
                    weight = max(0.1, score)  # Minimum weight of 0.1
                    total_weighted_score += score * weight
                    total_weight += weight
                except (ValueError, TypeError):
                    continue

            if total_weight > 0:
                ai_score = total_weighted_score / total_weight
            else:
                ai_score = 0.0

            # Determine AI signal based on AI score
            if ai_score < 0.4:
                ai_signal = "卖出"
            elif ai_score <= 0.7:
                ai_signal = "持有"
            else:
                ai_signal = "买入"

            return {
                'score_ai': max(0.0, min(1.0, ai_score)),  # Normalize to 0-1 range
                'signal_ai': ai_signal
            }

        except Exception as e:
            self.log_error(f"Error in AI analysis: {e}")
            # Return default values on error
            return {'score_ai': 0.0, 'signal_ai': '持有'}

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

                    # Add our strategy signals
                    existing_stock["signals"][self.name] = analyzed_stock.get("signals", {})

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


# Example usage
if __name__ == "__main__":
    import logging

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # This strategy doesn't need sample data as it works with pool data
    print("信号生成V1 Strategy - Analyzes existing pool data to generate signals")

