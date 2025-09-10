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

**策略思想**: 基于动量指标选择股票的策略，当动量值超过阈值时产生买入信号，当动量值低于阈值时产生卖出信号。该策略使用分数机制来评估股票的强度，并根据分数计算仓位大小。策略执行后会自动将结果保存到数据库中。

**参数设置**:
- `period`: 动量计算周期 (默认: 14)
- `threshold`: 动量阈值 (默认: 0)
- `lookback_period`: 数据完整性检查周期 (默认: 20)

**输出含义**:
- `code`: 股票代码
- `selection_reason`: 选股理由
- `score`: 选股分数 (0-1之间)
- `position`: 基于分数计算的仓位大小
- `strategy_name`: 策略名称
- `technical_analysis`: 技术分析数据
  - `price`: 当前价格
  - `momentum`: 动量指标值
  - `volume`: 成交量
- `momentum_positive`: 动量是否为正

**功能特性**:
- 支持基于动量指标的选股分析
- 采用分数机制评估股票强度
- 自动生成交易信号 (BUY/SELL/HOLD)
- 根据分数动态计算仓位大小
- 自动保存策略执行结果到数据库

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
- `strategy_name`: 策略名称 (用于标识策略来源)

**最近更新**:
- 添加了 `strategy_name` 字段到选中的股票中，以标识策略来源
- 该更新是整体池数据结构修复的一部分，确保只写入标准字段到池中

## 16. ThreeMABullishArrangementStrategy(三均线多头排列策略)

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

## 17. VolumeBreakoutStrategy (放量突破策略)

策略思想:
利用价格突破前期高点、成交量显著放大和动量指标确认三者共振，识别强势龙头股的启动信号。当价格创周期新高、量能放大达到阈值且MACD维持多头格局时，产生买入信号；否则观望或卖出。通过引入score衡量突破强度，辅助决策。

参数设置:
- breakout_period: 突破周期 (默认: 13天)
- volume_ma_period: 量能均线周期 (默认: 5天)
- volume_multiplier: 量能放大倍数 (默认: 1.8倍)
- macd_fast: MACD快线周期 (默认: 12)
- macd_slow: MACD慢线周期 (默认: 26)
- macd_signal: MACD信号线周期 (默认: 9)

输出含义:
- price: 当前收盘价
- breakout_high: 突破的前期高点值
- current_volume: 当前成交量
- avg_volume: 平均成交量值
- volume_ratio: 量比 (当前量/平均量)
- macd: MACD指标值 (包含dif和dea)
- score: 突破强度评分 (0 ~ 100)
- breakout_signal: 突破信号 (布尔值，True表示有效突破)
- position: 仓位大小 (0 ~ 1, 满仓=1)

Score 计算公式:
```
score = max(
    0,
    min(
        100,
        40 * min(2.0, (volume_ratio - 1)) / 1.0  # 量能放大强度
      + 35 * (price - breakout_high) / breakout_high  # 突破幅度强度
      + 25 * max(0, macd_dif) / max(0.01, abs(macd_dif))  # 动量确认强度
    )
)
```

解释：
第一项 (40%)：量能放大程度，反映资金进场力度。1倍得0分，2倍得40分。
第二项 (35%)：突破前期高点的幅度，体现价格强度。突破幅度越大得分越高。
第三项 (25%)：MACD多头动量强度，DIF为正值且越大得分越高。

结果归一化到 [0, 100]，越高表示突破信号越可靠。

突破信号检测：
当同时满足以下三个条件时，产生有效突破信号：

1. 收盘价 > 前期最高价 × (1 + 1.5%) （有效突破过滤）
2. 成交量 > 平均成交量 × volume_multiplier
3. MACD的DIF线 > 0 且方向向上

仓位管理规则：
- score ≥ 80: position = 1.0 （满仓）
- 70 ≤ score < 80: position = 0.7 （7成仓）
- 60 ≤ score < 70: position = 0.4 （4成仓）
- score < 60: position = 0.0 （不参与）

风险控制：
- 止损：跌破突破K线最低价立即止损
- 止盈：采用移动止盈，最高点回撤5%止盈一半，回撤8%全部清仓
- 单只个股最大仓位不超过25%

18. PullbackBuyingStrategy (回踩低吸型策略)

策略思想:
在长期趋势向上的背景下，寻找价格有效回踩重要支撑位的机会进行低吸买入。通过趋势、超卖和支撑三重确认，在相对低位布局。

参数设置:

ma_period: 趋势均线周期 (默认: 13天)

kdj_n: KDJ周期参数N (默认: 9)

rsi_period: RSI周期 (默认: 14)

oversold_threshold: 超卖阈值 (默认: 30)

support_band_pct: 支撑带宽 (默认: 0.03) # ±3%

输出含义:

ma_value: 当前均线值

ma_trend: 均线趋势方向 (1:向上, 0:走平, -1:向下)

kdj_j: 当前KDJ的J值

rsi_value: 当前RSI值

is_valid_pullback: 有效回踩信号 (布尔值)

score: 低吸机会评分 (0 ~ 100)

position: 仓位大小 (0 ~ 1, 满仓=1)

Score 计算公式:

python
score = max(
    0,
    min(
        100,
        40 * max(0, (oversold_threshold - kdj_j)) / oversold_threshold  # KDJ超卖程度
      + 30 * max(0, (oversold_threshold - rsi_value)) / oversold_threshold  # RSI超卖程度
      + 30 * max(0, (ma_value - close)) / ma_value  # 回踩深度
    )
)
解释：
第一项 (40%)：KDJ的J值超卖程度，J值越低得分越高
第二项 (30%)：RSI超卖程度，RSI越低得分越高
第三项 (30%)：价格回踩均线的深度，回踩越深得分越高

结果归一化到 [0, 100]，越高表示低吸机会越好。

有效回踩判断条件:

python
def is_valid_pullback(close, ma_value, kdj_j, rsi_value, ma_trend):
    """判断是否为有效回踩"""
    # 基础条件
    price_condition = abs(close - ma_value) / ma_value <= 0.03  # 价格在均线±3%内
    oversold_condition = (kdj_j < 20) or (rsi_value < 30)      # 超卖状态
    trend_condition = ma_trend > 0                             # 趋势向上
    
    return price_condition and oversold_condition and trend_condition
买入信号检测：
当 is_valid_pullback 为 True 且 score ≥ 60 时，产生买入信号

仓位管理规则：

score ≥ 80: position = 0.8 （8成仓）

70 ≤ score < 80: position = 0.6 （6成仓）

60 ≤ score < 70: position = 0.4 （4成仓）

score < 60: position = 0.0 （不参与）

风险控制：

止损：收盘价跌破13均线立即止损

止盈：反弹至前高压力位或涨幅20%开始分批止盈

单笔风险：最大亏损不超过总资金2%

策略优势：

简单明了，易于执行

三重条件确认，避免盲目抄底

明确的止损机制，风险可控

适合趋势行情中的回调买入
---
*注: 所有策略的position_size计算方法都遵循相同的逻辑，根据信号类型、投资组合价值和当前价格计算仓位大小，并根据中国市场习惯四舍五入到100股的整数倍。*


## 20. HMATurnoverStrategy (船体均线价格加速换手率过滤策略)

**策略思想**:
利用短期船体移动平均线(HMA)的价格加速特性，结合换手率过滤来识别具有上涨动力且流动性适中的股票。当短期HMA高于中期HMA且短期HMA呈上升趋势时，如果换手率在合理范围内(5-25%)，则产生买入信号。

**参数设置**:
- `short_period`: 短期HMA周期 (默认: 5天)
- `mid_period`: 中期HMA周期 (默认: 13天)
- `min_turnover`: 最小换手率阈值 (默认: 5.0%)
- `max_turnover`: 最大换手率阈值 (默认: 25.0%)

**输出含义**:
- `hma_short`: 当前短期HMA值
- `hma_mid`: 当前中期HMA值
- `turnover_rate`: 当前换手率
- `score`: 策略评分 (0 ~ 100)
- `position`: 仓位大小 (0 ~ 1, 满仓=1)

**Score 计算公式**:
```
score = max(
    0,
    min(
        100,
        40 * max(0, (hma_short - hma_mid) / hma_mid)  # HMA价差强度
      + 30 * max(0, (hma_short - hma_short_prev) / hma_short_prev)  # HMA加速强度
      + 30 * max(0, 1.0 - abs(turnover_rate - optimal_turnover) / (max_turnover - min_turnover))  # 换手率适配度
    )
)
```

**解释**:
- 第一项 (40%)：短期与中期HMA的距离，反映近期趋势强度
- 第二项 (30%)：短期HMA的加速程度，体现上涨动力
- 第三项 (30%)：换手率在最优区间内的适配度，过高或过低都不理想

**选股条件**:
1. HMA短期 > HMA中期
2. HMA短期 >= HMA短期前值
3. 换手率 ∈ [5%, 25%]

**仓位管理规则**:
- score ≥ 80: position = 1.0 （满仓）
- 70 ≤ score < 80: position = 0.7 （7成仓）
- 60 ≤ score < 70: position = 0.4 （4成仓）
- score < 60: position = 0.0 （不参与）

**风险控制**:
- 止损：收盘价跌破HMA中期线立即止损
- 止盈：采用移动止盈，最高点回撤5%止盈一半，回撤8%全部清仓
- 单只个股最大仓位不超过25%

**策略优势**:
- 结合价格趋势和流动性双重因素
- 使用HMA而非传统WMA，更准确反映价格趋势
- 换手率过滤避免过高或过低流动性的股票
- 量化评分体系便于参数优化和策略组合

## 21. SignalGenerationV1Strategy (信号生成V1策略)

**策略思想**:
统计pool数据集中每只股票满足的策略数量，计算平均分，并根据平均分和AI分析生成买卖信号。

**参数设置**:
- `min_strategies`: 最小满足策略数 (默认: 1)
- `score_threshold_buy`: 买入信号阈值 (默认: 0.7)
- `score_threshold_sell`: 卖出信号阈值 (默认: 0.4)

**输出含义**:
- `count`: 满足的策略数量
- `score_calc`: 计算的平均分
- `signal_calc`: 根据平均分计算的信号 (买入/持有/卖出)
- `score_ai`: AI分析得分
- `signal_ai`: AI分析信号 (买入/持有/卖出)

**功能特性**:
- 综合分析技术面(tech)、基本面(fund)和舆情面(pub)的策略结果
- 智能信号生成：基于多维度数据生成统一的买卖信号
- AI增强：提供AI驱动的分析结果作为参考
- 实时更新：自动更新pool数据中的信号信息

**信号逻辑**:
- **平均分计算**: 遍历股票在tech、fund、pub字段中的所有策略结果，收集每个策略的score值，计算所有score的平均值作为score_calc
- **信号判定规则**:
  - 买入信号: score_calc > 0.7
  - 持有信号: 0.4 ≤ score_calc ≤ 0.7
  - 卖出信号: score_calc < 0.4
- **AI增强分析**: 对所有策略的score和value进行综合分析，生成AI评分(score_ai)和AI信号(signal_ai)

**数据结构**:
策略分析结果存储在每个股票的`signals.信号生成V1`字段中:
```json
{
  "score": 0.71,
  "value": {
    "count": 3,
    "score_calc": 0.71,
    "signal_calc": "买入",
    "score_ai": 0.7129,
    "signal_ai": "买入"
  }
}
```

