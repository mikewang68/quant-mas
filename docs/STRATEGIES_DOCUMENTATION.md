# 策略说明文档

本文档详细说明了项目中所有策略的参数设置、策略思想及输出含义。

## 1. BaseStrategy (基础策略类)

**策略思想**: 所有策略的基类，定义了策略的基本接口和通用方法。

**参数设置**:
- `name`: 策略名称
- `params`: 策略参数字典

**输出含义**:
- 作为所有策略的基类，不直接生成交易信号

## 2. MACrossoverStrategy (移动平均线交叉策略)

**策略思想**: 当短期移动平均线向上穿越长期移动平均线时产生买入信号，向下穿越时产生卖出信号。

**参数设置**:
- `short_period`: 短期移动平均周期 (默认: 5)
- `long_period`: 长期移动平均周期 (默认: 20)
- `max_position_ratio`: 最大仓位比例 (默认: 0.1)

**输出含义**:
- `signal`: 交易信号 ('BUY', 'SELL', 'HOLD')
- `position`: 仓位大小

## 3. RSIStrategy (RSI相对强弱指数策略)

**策略思想**: 当RSI指标向下穿越超卖区(30)时产生买入信号，向上穿越超买区(70)时产生卖出信号。

**参数设置**:
- `period`: RSI计算周期 (默认: 14)
- `overbought`: 超买阈值 (默认: 70)
- `oversold`: 超卖阈值 (默认: 30)
- `max_position_ratio`: 最大仓位比例 (默认: 0.1)

**输出含义**:
- `rsi`: RSI指标值
- `signal`: 交易信号 ('BUY', 'SELL', 'HOLD')
- `position`: 仓位大小

## 4. BollingerBandsStrategy (布林带策略)

**策略思想**: 当价格向下穿越布林带下轨时产生买入信号，向上穿越布林带上轨时产生卖出信号。

**参数设置**:
- `period`: 布林带计算周期 (默认: 20)
- `std_dev`: 标准差倍数 (默认: 2)
- `max_position_ratio`: 最大仓位比例 (默认: 0.1)

**输出含义**:
- `upper_band`: 布林带上轨
- `middle_band`: 布林带中轨
- `lower_band`: 布林带下轨
- `signal`: 交易信号 ('BUY', 'SELL', 'HOLD')
- `position`: 仓位大小

## 5. MACDStrategy (MACD策略)

**策略思想**: 当MACD线向上穿越信号线时产生买入信号，向下穿越时产生卖出信号。

**参数设置**:
- `fast_period`: 快速EMA周期 (默认: 12)
- `slow_period`: 慢速EMA周期 (默认: 26)
- `signal_period`: 信号线周期 (默认: 9)
- `max_position_ratio`: 最大仓位比例 (默认: 0.1)

**输出含义**:
- `macd`: MACD线
- `macd_signal`: 信号线
- `macd_hist`: 柱状图
- `signal`: 交易信号 ('BUY', 'SELL', 'HOLD')
- `position`: 仓位大小

## 6. VolumeStrategy (成交量策略)

**策略思想**: 当成交量显著高于平均值时产生买入信号，显著低于平均值时产生卖出信号。

**参数设置**:
- `period`: 成交量移动平均周期 (默认: 20)
- `threshold`: 成交量倍数阈值 (默认: 1.5)
- `max_position_ratio`: 最大仓位比例 (默认: 0.1)

**输出含义**:
- `volume`: 成交量
- `volume_ma`: 成交量移动平均
- `volume_ratio`: 成交量比率
- `signal`: 交易信号 ('BUY', 'SELL', 'HOLD')
- `position`: 仓位大小

## 7. MeanReversionStrategy (均值回归策略)

**策略思想**: 当价格显著偏离移动平均线下方时产生买入信号，显著偏离上方时产生卖出信号。

**参数设置**:
- `period`: 移动平均周期 (默认: 20)
- `std_dev_multiplier`: 标准差倍数 (默认: 2)
- `max_position_ratio`: 最大仓位比例 (默认: 0.1)

**输出含义**:
- `ma`: 移动平均线
- `upper_band`: 上轨线
- `lower_band`: 下轨线
- `signal`: 交易信号 ('BUY', 'SELL', 'HOLD')
- `position`: 仓位大小

## 8. MomentumStrategy (动量策略)

**策略思想**: 当动量指标转正时产生买入信号，转负时产生卖出信号。

**参数设置**:
- `period`: 动量计算周期 (默认: 14)
- `threshold`: 动量阈值 (默认: 0)
- `max_position_ratio`: 最大仓位比例 (默认: 0.1)

**输出含义**:
- `momentum`: 动量指标
- `signal`: 交易信号 ('BUY', 'SELL', 'HOLD')
- `position`: 仓位大小

## 9. VolatilityStrategy (波动率策略)

**策略思想**: 当波动率低时(预期突破)产生买入信号，波动率高时(预期反转)产生卖出信号。

**参数设置**:
- `period`: 波动率计算周期 (默认: 14)
- `low_percentile`: 低波动率百分位阈值 (默认: 20)
- `high_percentile`: 高波动率百分位阈值 (默认: 80)
- `max_position_ratio`: 最大仓位比例 (默认: 0.1)

**输出含义**:
- `atr`: 平均真实波幅
- `signal`: 交易信号 ('BUY', 'SELL', 'HOLD')
- `position`: 仓位大小

## 10. SupportResistanceStrategy (支撑阻力策略)

**策略思想**: 当价格从支撑位反弹时产生买入信号，从阻力位回落时产生卖出信号。

**参数设置**:
- `period`: 支撑阻力检测回看周期 (默认: 20)
- `threshold`: 价格接近度阈值 (默认: 0.02, 即2%)
- `max_position_ratio`: 最大仓位比例 (默认: 0.1)

**输出含义**:
- `support`: 支撑位
- `resistance`: 阻力位
- `signal`: 交易信号 ('BUY', 'SELL', 'HOLD')
- `position`: 仓位大小

## 11. TrendFollowingStrategy (趋势跟踪策略)

**策略思想**: 当价格突破移动平均线时产生买入信号，跌破时产生卖出信号。

**参数设置**:
- `period`: 移动平均周期 (默认: 50)
- `max_position_ratio`: 最大仓位比例 (默认: 0.1)

**输出含义**:
- `ma`: 移动平均线
- `signal`: 交易信号 ('BUY', 'SELL', 'HOLD')
- `position`: 仓位大小

## 12. BreakoutStrategy (突破策略)

**策略思想**: 当价格突破阻力位时产生买入信号，跌破支撑位时产生卖出信号。

**参数设置**:
- `period`: 支撑阻力计算回看周期 (默认: 20)
- `buffer`: 突破确认缓冲百分比 (默认: 0.01, 即1%)
- `max_position_ratio`: 最大仓位比例 (默认: 0.1)

**输出含义**:
- `support`: 支撑位
- `resistance`: 阻力位
- `signal`: 交易信号 ('BUY', 'SELL', 'HOLD')
- `position`: 仓位大小

## 13. ScalpingStrategy (高频交易策略)

**策略思想**: 基于短期价格变动产生交易信号，适用于高频交易。

**参数设置**:
- `period`: 动量计算回看周期 (默认: 5)
- `threshold`: 价格变动阈值 (默认: 0.005, 即0.5%)
- `max_position_ratio`: 最大仓位比例 (默认: 0.1)

**输出含义**:
- `momentum`: 动量指标
- `price_change_ratio`: 价格变动比率
- `signal`: 交易信号 ('BUY', 'SELL', 'HOLD')
- `position`: 仓位大小

## 14. MultiAgentStrategy (多智能体策略)

**策略思想**: 结合多个智能体的决策结果产生最终交易信号。

**参数设置**:
- 根据具体实现而定

**输出含义**:
- 根据具体实现而定

## 15. AcceleratingUptrendStrategy (加速上涨策略)

**策略思想**: 通过计算股价上涨角度并检测角度加速来识别具有强劲上涨动力的股票。当股价上涨角度超过阈值且在加速时产生买入信号。

**参数设置**:
- `angle_threshold`: 最小上涨角度阈值 (默认: 30度)
- `lookback_period`: 计算角度的回看周期 (默认: 20天)
- `volume_ratio_threshold`: 成交量比率阈值 (默认: 1.2)
- `acceleration_window`: 计算加速度的窗口 (默认: 2)

**输出含义**:
- `current_angle`: 当前价格角度
- `previous_angle`: 前一时间段价格角度
- `acceleration`: 角度加速度
- `volume_confirmed`: 成交量确认
- `signal`: 交易信号 ('BUY', 'SELL', 'HOLD')
- `position`: 仓位大小

---
*注: 所有策略的position_size计算方法都遵循相同的逻辑，根据信号类型、投资组合价值和当前价格计算仓位大小，并根据中国市场习惯四舍五入到100股的整数倍。*

