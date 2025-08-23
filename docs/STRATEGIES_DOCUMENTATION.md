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

策略思想:
利用均线多头排列、MACD动量以及价格突破三大条件来识别稳健的趋势性上涨行情。只有当价格站稳在关键均线之上，且动量指标与价格行为相互确认时，才产生买入信号，有效避免震荡市中的频繁交易。
参数设置:
ma_fast: 快速均线周期 (默认: 5)
ma_slow: 慢速均线周期 (默认: 13)
macd_fast: MACD快线周期 (默认: 12)
macd_slow: MACD慢线周期 (默认: 26)
macd_signal: MACD信号线周期 (默认: 9)
new_high_period: 新高周期 (默认: 20)
输出含义:
ma_fast: 当前快速均线值 (MA5)
ma_slow: 当前中期均线值 (MA13)
macd_dif: 当前DIF值
macd_dea: 当前DEA值
macd_histogram: 当前MACD柱状线值
score: 趋势强度评分 (0 ~ 100)
golden_cross: 金叉信号 (布尔值，True表示检测到金叉)
position: 仓位大小 (0 ~ 1, 满仓=1)
Score 计算公式:
python
score = max(
    0,
    min(
        100,
        40 * (ma_fast - ma_slow) / ma_mid  # 均线排列强度
      + 30 * (macd_dif - macd_dea) / abs(macd_dea) if macd_dea != 0 else 0  # MACD动量
      + 20 * max(0, (macd_dif - 0)) / max(0.01, macd_dif)  # 零轴之上加分
      + 10 * (price - max(historical_high)) / max(historical_high)  # 突破强度
    )
)
解释：
第一项 (40%)：快速与慢速均线的距离，反映近期趋势强度
第二项 (30%)：MACD金叉后的扩散程度，体现动量加速
第三项 (20%)：DIF线在零轴之上的偏离程度，确认多头市场
第四项 (10%)：价格突破历史高点的幅度，过滤假信号
金叉检测：
当快速均线(MA5)向上穿越中期均线(MA13)且MACD的DIF线上穿DEA线时，产生金叉确认信号。
止损条件：
当收盘价跌破慢速均线(MA13)时，触发止损信号，position设置为0。
止盈条件：
当收益率达到20%~30%时，开始分批止盈
当收盘价跌破快速均线(MA5)时，清仓离场

信号生成规则：
基础信号：MA5 > MA13 && DIF > DEA && 价格创20周期新高
强度确认：score > 60 (可调节)
仓位管理：score越高，position越接近1
风险控制：严格执行止损止盈规则
策略优势：
多维度确认趋势，减少假信号
量化趋势强度，实现动态仓位管理
明确的止损止盈机制，控制风险
适合中长线趋势跟踪，避免频繁交易
此策略通过均线、MACD、价格突破三大维度的综合评分，实现了对趋势强度的量化评估，同时保留了原策略的核心风控规则，是一个完整的趋势跟随系统。

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

16. ThreeMABullishArrangementStrategy(三均线多头排列策略)

策略思想:
利用短期、中期和长期移动平均线的多头排列 (short > mid > long) 来识别趋势性上涨行情。当价格高于三条均线，且三条均线均呈上升趋势时，产生买入信号；否则持有或卖出。通过引入 score 衡量趋势强度。同时检测短期均线与中期均线的金叉信号，作为辅助确认信号。

参数设置:
- ma_short_period: 短期均线周期 (默认: 5天)
- ma_mid_period: 中期均线周期 (默认: 13天)
- ma_long_period: 长期均线周期 (默认: 34天)

输出含义:
- ma_short: 当前短期均线值
- ma_mid: 当前中期均线值
- ma_long: 当前长期均线值
- score: 趋势强度评分 (0 ~ 100)
- golden_cross: 金叉信号 (布尔值，True表示检测到金叉)
- position: 仓位大小 (0 ~ 1, 满仓=1)

Score 计算公式:
score = max(
    0,
    min(
        100,
        50 * (ma_short - ma_mid) / ma_mid
      + 30 * (ma_mid - ma_long) / ma_long
      + 20 * (price - ma_short) / ma_short
    )
)

解释：
第一项 (50%)：短期与中期均线的距离，占比最大，反映近期趋势强度。
第二项 (30%)：中期与长期均线的距离，占次要地位，保证大趋势。
第三项 (20%)：当前价格相对短期均线的偏离，体现市场动能。

结果归一化到 [0, 100]，越高表示趋势越强。

金叉检测：
当短期均线向上穿越中期均线时，产生金叉信号，作为趋势确认的辅助指标。
---
*注: 所有策略的position_size计算方法都遵循相同的逻辑，根据信号类型、投资组合价值和当前价格计算仓位大小，并根据中国市场习惯四舍五入到100股的整数倍。*

