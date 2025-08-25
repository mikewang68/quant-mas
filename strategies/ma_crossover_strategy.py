"""
移动平均线交叉策略
从pool中获取股票代码，针对每个股票代码使用akshare获取日线数据，并考虑复权情况。
"""

import pandas as pd
import numpy as np
import talib
from typing import Dict, Optional
from strategies.base_strategy import BaseStrategy
from utils.akshare_client import akshare_client
from datetime import datetime, timedelta


class MACrossoverStrategy(BaseStrategy):
    """
    移动平均线交叉策略
    当短期均线向上穿过长期均线时生成买入信号，
    当短期均线向下穿过长期均线时生成卖出信号。
    """

    def __init__(self, name: str = "移动平均线交叉策略", params: Optional[Dict] = None):
        """
        初始化移动平均线交叉策略。

        Args:
            name: 策略名称
            params: 策略参数
                - short_period: 短期移动平均周期 (默认: 5)
                - long_period: 长期移动平均周期 (默认: 20)
                - max_position_ratio: 最大仓位比例 (默认: 0.1)
                - adjust_type: 复权类型 ('qfq' 前复权, 'hfq' 后复权, '' 不复权) (默认: 'qfq')
        """
        super().__init__(name, params)

        # 策略参数
        self.short_period = self.params.get("short_period", 5)
        self.long_period = self.params.get("long_period", 20)
        self.max_position_ratio = self.params.get("max_position_ratio", 0.1)
        # 复权类型应使用 akshare 支持的值: "" (不复权), "qfq" (前复权), "hfq" (后复权)
        adjust_type = self.params.get("adjust_type", "qfq")
        # 确保使用正确的复权参数值
        if adjust_type == "q":
            self.adjust_type = "qfq"
        elif adjust_type == "h":
            self.adjust_type = "hfq"
        elif adjust_type == "none":
            self.adjust_type = ""
        else:
            self.adjust_type = adjust_type  # 直接使用传入的值

        self.logger.info(
            f"初始化 {self.name} 策略，参数: "
            f"short_period={self.short_period}, long_period={self.long_period}, "
            f"adjust_type={self.adjust_type}"
        )

    def fetch_stock_data(self, code: str) -> pd.DataFrame:
        """
        使用akshare获取股票日线数据，考虑复权情况。
        根据策略参数动态计算需要的数据天数。

        Args:
            code: 股票代码

        Returns:
            包含日线数据的DataFrame
        """
        try:
            # 根据长期均线周期计算需要的数据天数
            # 获取比长期均线周期多30%的数据，确保有足够的数据进行计算
            required_days = int(self.long_period * 1.3)
            # 至少获取60天的数据
            required_days = max(required_days, 60)
            # 最多获取365天的数据（一年）
            required_days = min(required_days, 365)

            # 计算日期范围
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=required_days)).strftime(
                "%Y-%m-%d"
            )

            # 验证日期，确保不请求未来日期的数据
            today = datetime.now().strftime("%Y-%m-%d")
            if end_date > today:
                self.logger.warning(
                    f"结束日期 {end_date} 超过今天 {today}，将使用今天作为结束日期"
                )
                end_date = today
                # 重新计算开始日期
                start_date = (
                    datetime.strptime(end_date, "%Y-%m-%d")
                    - timedelta(days=required_days)
                ).strftime("%Y-%m-%d")

            # 使用akshare获取数据，考虑复权设置
            k_data = akshare_client.get_daily_k_data(
                code=code,
                start_date=start_date,
                end_date=end_date,
                adjust_type=self.adjust_type,
            )

            if k_data.empty:
                self.logger.warning(f"未获取到股票 {code} 的数据")
                return pd.DataFrame()

            self.logger.info(
                f"成功获取股票 {code} 的 {len(k_data)} 条记录 (需要 {required_days} 天数据)"
            )
            return k_data

        except Exception as e:
            self.logger.error(f"获取股票 {code} 数据时出错: {e}")
            return pd.DataFrame()

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成移动平均线交叉信号。

        Args:
            data: 包含列 ['date', 'open', 'high', 'low', 'close', 'volume'] 的DataFrame

        Returns:
            包含信号的DataFrame
        """
        if not self.validate_data(data):
            return pd.DataFrame()

        # 计算移动平均线
        close_prices = data["close"].values.astype(np.double)  # 确保数据类型正确
        ma_short = talib.SMA(close_prices, timeperiod=self.short_period)
        ma_long = talib.SMA(close_prices, timeperiod=self.long_period)

        # 初始化信号
        signals = pd.DataFrame(index=data.index)
        signals["date"] = data["date"]
        signals["close"] = data["close"]
        signals["ma_short"] = ma_short
        signals["ma_long"] = ma_long
        signals["signal"] = "HOLD"
        signals["position"] = 0.0

        # 生成信号
        for i in range(1, len(signals)):
            # 买入信号: 短期均线向上穿过长期均线
            if ma_short[i - 1] <= ma_long[i - 1] and ma_short[i] > ma_long[i]:
                signals.loc[i, "signal"] = "BUY"
                signals.loc[i, "position"] = 1.0

            # 卖出信号: 短期均线向下穿过长期均线
            elif ma_short[i - 1] >= ma_long[i - 1] and ma_short[i] < ma_long[i]:
                signals.loc[i, "signal"] = "SELL"
                signals.loc[i, "position"] = -1.0

            # 持有信号: 维持之前仓位
            else:
                signals.loc[i, "signal"] = "HOLD"
                signals.loc[i, "position"] = signals.loc[i - 1, "position"]

        return signals

    def calculate_position_size(
        self, signal: str, portfolio_value: float, price: float
    ) -> float:
        """
        根据信号计算仓位大小。

        Args:
            signal: 交易信号 ('BUY', 'SELL', 'HOLD')
            portfolio_value: 当前组合价值
            price: 当前资产价格

        Returns:
            仓位大小 (股数)
        """
        if signal == "BUY":
            # 计算最大仓位价值
            max_position_value = portfolio_value * self.max_position_ratio

            # 计算股数
            shares = max_position_value / price

            # 四舍五入到100股的整数倍 (中国股市常见规则)
            shares = round(shares / 100) * 100

            return float(shares)

        elif signal == "SELL":
            # 对于卖出信号，返回负的仓位大小
            # 实际应用中，这取决于当前持仓
            return -100.0  # 占位符

        else:
            return 0.0

    def execute(self, stock_data: Dict[str, pd.DataFrame],
                agent_name: str, db_manager) -> list:
        """
        执行移动平均线交叉策略并保存结果到pool

        Args:
            stock_data: 股票数据字典
            agent_name: 执行策略的agent名称
            db_manager: 数据库管理器

        Returns:
            选中的股票列表
        """
        self.log_info(f"执行 {self.name} 策略，股票数量: {len(stock_data)}")

        selected_stocks = []

        # 分析每只股票
        for code, data in stock_data.items():
            try:
                if data.empty:
                    continue

                # 生成信号
                signals = self.generate_signals(data)

                if not signals.empty:
                    # 获取最新信号
                    latest_signal = signals.iloc[-1]
                    signal_type = latest_signal['signal']
                    position = latest_signal['position']

                    # 如果有买入信号，则选择该股票
                    if signal_type == 'BUY':
                        selected_stocks.append({
                            'code': code,
                            'selection_reason': f"MA交叉策略买入信号 - 短期均线: {latest_signal['ma_short']:.2f}, 长期均线: {latest_signal['ma_long']:.2f}",
                            'signal': signal_type,
                            'position': position,
                            'technical_analysis': {
                                'price': float(latest_signal['close']),
                                'ma_short': float(latest_signal['ma_short']),
                                'ma_long': float(latest_signal['ma_long'])
                            }
                        })

            except Exception as e:
                self.log_warning(f"处理股票 {code} 时出错: {e}")
                continue

        self.log_info(f"策略选中 {len(selected_stocks)} 只股票")

        # 保存结果到pool
        if selected_stocks:
            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')

            # Use the new common formatting methods
            formatted_output = self.format_strategy_output(
                stocks=selected_stocks,
                agent_name=agent_name,
                date=current_date,
                strategy_params=self.params,
                additional_metadata={
                    'strategy_version': '1.0',
                    'total_stocks_analyzed': len(stock_data)
                }
            )

            save_success = self.save_to_pool(
                db_manager=db_manager,
                agent_name=agent_name,
                stocks=selected_stocks,
                date=current_date,
                strategy_params=self.params,
                additional_metadata={
                    'strategy_version': '1.0',
                    'total_stocks_analyzed': len(stock_data)
                }
            )

            if save_success:
                self.log_info("策略结果已保存到pool")
            else:
                self.log_error("保存策略结果到pool失败")

        return selected_stocks


# Example usage
if __name__ == "__main__":
    import logging

    # 配置日志
    logging.basicConfig(level=logging.INFO)

    # 创建示例数据
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    sample_data = pd.DataFrame(
        {
            "date": dates,
            "open": np.random.uniform(100, 110, 100),
            "high": np.random.uniform(110, 120, 100),
            "low": np.random.uniform(90, 100, 100),
            "close": np.random.uniform(100, 110, 100),
            "volume": np.random.uniform(1000000, 2000000, 100),
        }
    )

    # 初始化策略
    strategy = MACrossoverStrategy()

    # 生成信号
    signals = strategy.generate_signals(sample_data)
    print(f"生成了 {len(signals[signals['signal'] != 'HOLD'])} 个交易信号")
    print(signals.tail(10))
