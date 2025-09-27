"""
Fundamental Strategy based on financial analysis
Performs fundamental analysis of stocks based on financial statements and ratios.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from strategies.base_strategy import BaseStrategy
import akshare as ak

# Configure logger
logger = logging.getLogger(__name__)


class FundamentalStrategy(BaseStrategy):
    """
    Fundamental Strategy - Performs fundamental analysis based on financial statements
    """

    def __init__(self, name: str = "基本面分析策略", params: Optional[Dict] = None):
        """
        Initialize the fundamental strategy.

        Args:
            name: Name of the strategy
            params: Strategy parameters
        """
        super().__init__(name, params)

        # Strategy parameters with defaults
        self.params = params or {}
        self.min_roe = self.params.get('min_roe', 0.1)  # Minimum ROE 10%
        self.max_pe = self.params.get('max_pe', 20)     # Maximum P/E ratio
        self.min_current_ratio = self.params.get('min_current_ratio', 1.5)  # Minimum current ratio
        self.max_debt_equity = self.params.get('max_debt_equity', 0.5)  # Maximum debt to equity ratio
        self.min_revenue_growth = self.params.get('min_revenue_growth', 0.1)  # Minimum revenue growth 10%

        self.log_info(f"Initialized Fundamental Strategy with params: {self.params}")

    def analyze_stock_fundamentals(self, stock_code: str) -> Dict[str, Any]:
        """
        Analyze stock fundamentals using financial data.

        Args:
            stock_code: Stock code to analyze

        Returns:
            Dictionary with analysis results
        """
        try:
            # Get financial data
            financial_data = self.get_financial_data(stock_code)

            # Calculate financial ratios
            financial_ratios = self.calculate_financial_ratios(financial_data)

            # Score the stock based on financial criteria
            score_result = self.score_stock(financial_ratios)

            return {
                'ratios': financial_ratios,
                'score': score_result['score'],
                'analysis': score_result['analysis']
            }

        except Exception as e:
            self.log_error(f"Error analyzing stock {stock_code}: {e}")
            return {
                'ratios': {},
                'score': 0.0,
                'analysis': f"分析失败: {str(e)}"
            }

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
                financial_indicators = ak.stock_financial_abstract_ths(symbol=stock_code)
            except:
                financial_indicators = pd.DataFrame()

            # Get balance sheet data
            try:
                balance_sheet = ak.stock_balance_sheet_by_report_em(symbol=stock_code)
            except:
                balance_sheet = pd.DataFrame()

            # Get income statement data
            try:
                income_statement = ak.stock_profit_sheet_by_report_em(symbol=stock_code)
            except:
                income_statement = pd.DataFrame()

            # Get cash flow statement data
            try:
                cash_flow = ak.stock_cash_flow_sheet_by_report_em(symbol=stock_code)
            except:
                cash_flow = pd.DataFrame()

            return {
                'financial_indicators': financial_indicators.to_dict() if not financial_indicators.empty else {},
                'balance_sheet': balance_sheet.to_dict() if not balance_sheet.empty else {},
                'income_statement': income_statement.to_dict() if not income_statement.empty else {},
                'cash_flow': cash_flow.to_dict() if not cash_flow.empty else {}
            }
        except Exception as e:
            self.log_warning(f"Error getting financial data for {stock_code}: {e}")
            return {
                'financial_indicators': {},
                'balance_sheet': {},
                'income_statement': {},
                'cash_flow': {}
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
            balance_sheet = financial_data.get('balance_sheet', {})
            income_statement = financial_data.get('income_statement', {})

            # Profitability ratios
            ratios['roe'] = self.calculate_roe(balance_sheet, income_statement)
            ratios['roa'] = self.calculate_roa(balance_sheet, income_statement)
            ratios['gross_margin'] = self.calculate_gross_margin(income_statement)
            ratios['net_margin'] = self.calculate_net_margin(income_statement)

            # Liquidity ratios
            ratios['current_ratio'] = self.calculate_current_ratio(balance_sheet)
            ratios['quick_ratio'] = self.calculate_quick_ratio(balance_sheet)

            # Leverage ratios
            ratios['debt_to_equity'] = self.calculate_debt_to_equity(balance_sheet)
            ratios['interest_coverage'] = self.calculate_interest_coverage(income_statement)

            # Efficiency ratios
            ratios['asset_turnover'] = self.calculate_asset_turnover(balance_sheet, income_statement)

            # Growth ratios
            ratios['revenue_growth'] = self.calculate_revenue_growth(income_statement)
            ratios['earnings_growth'] = self.calculate_earnings_growth(income_statement)

            return ratios
        except Exception as e:
            self.log_warning(f"Error calculating financial ratios: {e}")
            return {}

    def calculate_roe(self, balance_sheet: Dict, income_statement: Dict) -> float:
        """Calculate Return on Equity"""
        try:
            net_income = self.get_latest_value(income_statement, '净利润')
            total_equity = self.get_latest_value(balance_sheet, '股东权益合计')
            if total_equity and total_equity != 0:
                return net_income / total_equity
        except:
            pass
        return 0.0

    def calculate_roa(self, balance_sheet: Dict, income_statement: Dict) -> float:
        """Calculate Return on Assets"""
        try:
            net_income = self.get_latest_value(income_statement, '净利润')
            total_assets = self.get_latest_value(balance_sheet, '资产总计')
            if total_assets and total_assets != 0:
                return net_income / total_assets
        except:
            pass
        return 0.0

    def calculate_gross_margin(self, income_statement: Dict) -> float:
        """Calculate gross margin"""
        try:
            revenue = self.get_latest_value(income_statement, '营业收入')
            cogs = self.get_latest_value(income_statement, '营业成本')
            if revenue and revenue != 0:
                return (revenue - cogs) / revenue
        except:
            pass
        return 0.0

    def calculate_net_margin(self, income_statement: Dict) -> float:
        """Calculate net profit margin"""
        try:
            net_income = self.get_latest_value(income_statement, '净利润')
            revenue = self.get_latest_value(income_statement, '营业收入')
            if revenue and revenue != 0:
                return net_income / revenue
        except:
            pass
        return 0.0

    def calculate_current_ratio(self, balance_sheet: Dict) -> float:
        """Calculate current ratio"""
        try:
            current_assets = self.get_latest_value(balance_sheet, '流动资产')
            current_liabilities = self.get_latest_value(balance_sheet, '流动负债')
            if current_liabilities and current_liabilities != 0:
                return current_assets / current_liabilities
        except:
            pass
        return 0.0

    def calculate_quick_ratio(self, balance_sheet: Dict) -> float:
        """Calculate quick ratio"""
        try:
            current_assets = self.get_latest_value(balance_sheet, '流动资产')
            inventory = self.get_latest_value(balance_sheet, '存货')
            current_liabilities = self.get_latest_value(balance_sheet, '流动负债')
            if current_liabilities and current_liabilities != 0:
                return (current_assets - inventory) / current_liabilities
        except:
            pass
        return 0.0

    def calculate_debt_to_equity(self, balance_sheet: Dict) -> float:
        """Calculate debt to equity ratio"""
        try:
            total_liabilities = self.get_latest_value(balance_sheet, '负债合计')
            total_equity = self.get_latest_value(balance_sheet, '股东权益合计')
            if total_equity and total_equity != 0:
                return total_liabilities / total_equity
        except:
            pass
        return 0.0

    def calculate_interest_coverage(self, income_statement: Dict) -> float:
        """Calculate interest coverage ratio"""
        try:
            ebit = self.get_latest_value(income_statement, '息税前利润')
            interest_expense = self.get_latest_value(income_statement, '利息支出')
            if interest_expense and interest_expense != 0:
                return ebit / abs(interest_expense)
        except:
            pass
        return 0.0

    def calculate_asset_turnover(self, balance_sheet: Dict, income_statement: Dict) -> float:
        """Calculate asset turnover ratio"""
        try:
            revenue = self.get_latest_value(income_statement, '营业收入')
            total_assets_begin = self.get_earlier_value(balance_sheet, '资产总计')
            total_assets_end = self.get_latest_value(balance_sheet, '资产总计')
            if total_assets_begin and total_assets_end and (total_assets_begin + total_assets_end) != 0:
                avg_assets = (total_assets_begin + total_assets_end) / 2
                return revenue / avg_assets
        except:
            pass
        return 0.0

    def calculate_revenue_growth(self, income_statement: Dict) -> float:
        """Calculate revenue growth rate"""
        try:
            revenue_latest = self.get_latest_value(income_statement, '营业收入')
            revenue_previous = self.get_earlier_value(income_statement, '营业收入')
            if revenue_previous and revenue_previous != 0:
                return (revenue_latest - revenue_previous) / revenue_previous
        except:
            pass
        return 0.0

    def calculate_earnings_growth(self, income_statement: Dict) -> float:
        """Calculate earnings growth rate"""
        try:
            earnings_latest = self.get_latest_value(income_statement, '净利润')
            earnings_previous = self.get_earlier_value(income_statement, '净利润')
            if earnings_previous and earnings_previous != 0:
                return (earnings_latest - earnings_previous) / earnings_previous
        except:
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
                        val = float(value)
                        if val != 0:
                            return val
                    except (ValueError, TypeError):
                        continue
                # If no non-zero value, return the last value
                try:
                    return float(values[-1]) if values else 0.0
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
                    return float(values[-2]) if len(values) > 1 else 0.0
                except (ValueError, TypeError):
                    return 0.0
        return 0.0

    def score_stock(self, financial_ratios: Dict) -> Dict[str, Any]:
        """
        Score stock based on financial ratios and criteria.

        Args:
            financial_ratios: Dictionary with calculated financial ratios

        Returns:
            Dictionary with score and analysis
        """
        try:
            score = 0.0
            analysis_details = []

            # Score based on ROE
            roe = financial_ratios.get('roe', 0)
            if roe >= self.min_roe:
                score += 0.2
                analysis_details.append(f"ROE达标 ({roe:.2%} >= {self.min_roe:.2%})")
            else:
                analysis_details.append(f"ROE不足 ({roe:.2%} < {self.min_roe:.2%})")

            # Score based on current ratio
            current_ratio = financial_ratios.get('current_ratio', 0)
            if current_ratio >= self.min_current_ratio:
                score += 0.15
                analysis_details.append(f"流动性良好 (流动比率 {current_ratio:.2f} >= {self.min_current_ratio})")
            else:
                analysis_details.append(f"流动性不足 (流动比率 {current_ratio:.2f} < {self.min_current_ratio})")

            # Score based on debt to equity
            debt_equity = financial_ratios.get('debt_to_equity', 0)
            if debt_equity <= self.max_debt_equity:
                score += 0.15
                analysis_details.append(f"负债率合理 (负债权益比 {debt_equity:.2f} <= {self.max_debt_equity})")
            else:
                analysis_details.append(f"负债率过高 (负债权益比 {debt_equity:.2f} > {self.max_debt_equity})")

            # Score based on revenue growth
            revenue_growth = financial_ratios.get('revenue_growth', 0)
            if revenue_growth >= self.min_revenue_growth:
                score += 0.2
                analysis_details.append(f"营收增长良好 ({revenue_growth:.2%} >= {self.min_revenue_growth:.2%})")
            else:
                analysis_details.append(f"营收增长不足 ({revenue_growth:.2%} < {self.min_revenue_growth:.2%})")

            # Score based on profitability ratios
            net_margin = financial_ratios.get('net_margin', 0)
            if net_margin > 0:
                score += 0.1
                analysis_details.append(f"盈利能力良好 (净利率 {net_margin:.2%} > 0)")
            else:
                analysis_details.append(f"盈利能力不足 (净利率 {net_margin:.2%} <= 0)")

            # Score based on asset efficiency
            asset_turnover = financial_ratios.get('asset_turnover', 0)
            if asset_turnover > 0:
                score += 0.1
                analysis_details.append(f"资产效率良好 (资产周转率 {asset_turnover:.2f} > 0)")
            else:
                analysis_details.append(f"资产效率不足 (资产周转率 {asset_turnover:.2f} <= 0)")

            # Score based on interest coverage
            interest_coverage = financial_ratios.get('interest_coverage', 0)
            if interest_coverage > 3:  # Generally considered safe
                score += 0.1
                analysis_details.append(f"利息保障充足 (利息覆盖率 {interest_coverage:.2f} > 3)")
            else:
                analysis_details.append(f"利息保障不足 (利息覆盖率 {interest_coverage:.2f} <= 3)")

            # Create analysis text
            analysis = "财务分析详情: " + "; ".join(analysis_details)

            return {
                'score': score,
                'analysis': analysis
            }

        except Exception as e:
            self.log_error(f"Error scoring stock: {e}")
            return {
                'score': 0.0,
                'analysis': f"评分失败: {str(e)}"
            }

    def execute(self, stock_data: Dict[str, pd.DataFrame], agent_name: str,
                db_manager) -> List[Dict]:
        """
        Execute the fundamental strategy.

        Args:
            stock_data: Dictionary mapping stock codes to DataFrames with stock data
            agent_name: Name of the agent executing this strategy
            db_manager: Database manager instance

        Returns:
            List of selected stocks with analysis results
        """
        self.log_info("Executing Fundamental Strategy")

        selected_stocks = []

        # Process each stock
        for stock_code in stock_data.keys():
            try:
                self.log_info(f"Analyzing stock {stock_code}")

                # Perform fundamental analysis
                analysis_result = self.analyze_stock_fundamentals(stock_code)

                # Create result entry
                result = {
                    'code': stock_code,
                    'score': analysis_result['score'],  # Already in 0-1 range
                    'value': analysis_result['analysis'],
                    'selection_reason': f"基本面分析评分: {analysis_result['score']:.2f}"
                }

                # Only include stocks with reasonable scores
                if analysis_result['score'] >= 0.5:  # At least 50% of criteria met
                    selected_stocks.append(result)
                    self.log_info(f"Selected stock {stock_code} with score {analysis_result['score']:.2f}")
                else:
                    self.log_info(f"Stock {stock_code} not selected (score: {analysis_result['score']:.2f})")

            except Exception as e:
                self.log_error(f"Error processing stock {stock_code}: {e}")
                continue

        # Sort stocks by score in descending order
        selected_stocks.sort(key=lambda x: x['score'], reverse=True)

        self.log_info(f"Fundamental Strategy completed. Selected {len(selected_stocks)} stocks out of {len(stock_data)}")
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
        signals['signal'] = 'HOLD'  # Default signal
        signals['score'] = 0.0  # Default score

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
        # For fundamental strategy, we might use a different position sizing approach
        if signal == 'BUY':
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

