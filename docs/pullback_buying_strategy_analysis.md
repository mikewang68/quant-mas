# Pullback Buying Strategy 分析文档

## 概述

Pullback Buying Strategy（回踩低吸型策略）是一种在长期趋势向上的背景下，寻找价格有效回踩重要支撑位的机会进行低吸买入的策略。该策略通过趋势、超卖和支撑三重确认，在相对低位进行布局。

## 策略逻辑

### 核心原理

1. **趋势确认**：使用移动平均线确认长期趋势向上
2. **超卖识别**：通过KDJ和RSI指标识别超卖状态
3. **支撑验证**：价格在回踩时未跌破重要支撑位
4. **综合评分**：结合多个维度计算策略得分

### 技术指标

1. **移动平均线（MA）**：
   - 默认周期：13日
   - 用于判断长期趋势方向

2. **KDJ指标**：
   - N周期：9日
   - 用于识别超买超卖状态

3. **RSI指标**：
   - 周期：14日
   - 默认超卖阈值：30

### 策略条件

1. **趋势条件**：
   - 移动平均线呈上升趋势
   - 当前价格在移动平均线附近（默认±3%范围内）

2. **超卖条件**：
   - KDJ J值 < 20 或 RSI值 < 30

3. **支撑条件**：
   - 价格未有效跌破移动平均线支撑

## 策略实现

### 主要函数功能

1. **`__init__`**：初始化策略参数
   - `ma_period`：趋势移动平均周期（默认13）
   - `kdj_n`：KDJ N周期（默认9）
   - `rsi_period`：RSI周期（默认14）
   - `oversold_threshold`：超卖阈值（默认30）
   - `support_band_pct`：支撑带百分比（默认0.03即3%）

2. **`analyze`**：核心分析方法
   - 检查数据有效性
   - 计算技术指标
   - 判断是否满足策略条件
   - 计算策略得分
   - 返回分析结果

3. **`get_technical_analysis_data`**：获取技术分析数据
   - 供Weekly Selector格式化使用
   - 返回包含价格、均线、KDJ、RSI等数据的字典

4. **`_calculate_ma_trend`**：计算移动平均线趋势方向
   - 1：上升趋势
   - 0：横盘趋势
   - -1：下降趋势

5. **`_is_valid_pullback`**：判断是否为有效回踩
   - 价格在均线附近
   - 处于超卖状态
   - 趋势向上

6. **`_calculate_score`**：计算策略得分
   - KDJ超卖程度（40%权重）
   - RSI超卖程度（30%权重）
   - 回踩深度（30%权重）
   - 得分范围：0-100

### 策略返回值说明

`analyze`方法返回一个四元组(Tuple)：

```python
Tuple[bool, str, Optional[float], bool]
```

#### 返回值各元素说明

1. **第一个元素 (bool)**: `meets_criteria` - 是否满足选股条件
   - `True`表示股票符合回踩低吸策略的选股条件
   - `False`表示不符合条件

2. **第二个元素 (str)**: `selection_reason` - 选股原因/描述
   - 当满足条件时，返回类似"回踩低吸条件: 收盘价=XX.XX, 均线值=XX.XX, KDJ_J=XX.XX, RSI=XX.XX (满足有效回踩)"的描述
   - 当不满足条件时，返回具体原因，如"低吸机会不足，得分=XX.XX"或"数据不足，需要XX条数据"

3. **第三个元素 (Optional[float])**: `score` - 策略得分
   - 类型为可选的浮点数
   - 得分范围在0-100之间
   - 计算公式：
     ```
     score = max(
         0,
         min(
             100,
             40 * max(0, (oversold_threshold - kdj_j)) / oversold_threshold  # KDJ超卖程度
           + 30 * max(0, (oversold_threshold - rsi_value)) / oversold_threshold  # RSI超卖程度
           + 30 * max(0, (ma_value - close)) / ma_value  # 回踩深度
         )
     )
     ```

4. **第四个元素 (bool)**: `pullback_signal` - 是否为有效回踩
   - `True`表示当前为有效回踩状态
   - `False`表示不是有效回踩状态

#### 代码中的具体返回语句

在满足条件的情况下：
```python
return True, reason, score, is_valid_pullback
```

在不满足条件的情况下：
```python
return False, f"低吸机会不足，得分={score:.2f}", score, False
```

在出现异常的情况下：
```python
return False, f"分析错误: {e}", None, False
```

## 数据格式化

### Technical Analysis Data 生成机制

在`get_technical_analysis_data`方法中生成的数据字典包含：
- `price`: 当前收盘价
- `ma_value`: 移动平均线值
- `ma_trend`: 移动平均线趋势（1:上升, 0:横盘, -1:下降）
- `kdj_j`: KDJ J值
- `rsi_value`: RSI值
- `is_valid_pullback`: 是否为有效回踩

### Value字段格式化

在Weekly Selector中，该策略的value字段格式化为：
```
"收盘价=XX.XX, 均线值=XX.XX, KDJ_J=XX.XX, RSI=XX.XX, 状态=有效回踩"
```

## 策略使用

### 在Weekly Selector中的调用

Weekly Selector通过以下方式调用该策略：

1. **策略加载**：从数据库读取策略配置，动态导入策略文件并实例化
2. **数据处理**：为每只股票获取一年的日K线数据，转换为周K线后交给策略分析
3. **策略执行**：调用`analyze`方法进行分析，根据返回结果判断是否符合选股条件
4. **结果保存**：将符合条件的股票保存到数据库的池中，供后续交易使用

### 信号生成

`generate_signals`方法可以生成交易信号：
- 当满足所有条件且得分>60时生成BUY信号
- 根据得分确定仓位大小（80分以上80%，70-80分60%，60-70分40%）

### 仓位计算

`calculate_position_size`方法根据信号和投资组合价值确定持仓量：
- BUY信号：默认分配10%的投资组合价值
- SELL信号：卖出100股
- HOLD信号：保持现有仓位

## 策略优势

1. **趋势跟踪**：只在上升趋势中寻找买入机会，避免逆势操作
2. **多重确认**：通过趋势、超卖、支撑三重确认提高准确率
3. **风险控制**：在相对低位买入，控制入场风险
4. **量化评分**：通过综合评分机制对机会进行排序

## 策略局限

1. **趋势依赖**：在震荡市场中可能错过机会
2. **滞后性**：基于历史数据计算，存在一定的滞后性
3. **参数敏感**：参数设置对策略效果有较大影响

