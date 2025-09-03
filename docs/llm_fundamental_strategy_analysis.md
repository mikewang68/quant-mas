# LLM Fundamental Selector策略程序结构和运行逻辑分析

## 程序结构

### 1. 核心组件

1. **LLM基本面策略类** (`strategies/llm_fundamental_strategy.py`)
   - 继承自 `BaseStrategy` 基类
   - 实现了完整的LLM基本面分析功能

2. **基本面选择器代理** (`agents/fundamental_selector.py`)
   - 继承自 `BaseAgent` 和 `DataProviderInterface`
   - 负责动态加载和执行策略

3. **配置文件** (`strategies/config/llm_fundamental_strategy_config.json`)
   - 定义策略的元数据和参数配置

### 2. 类结构

#### LLMFundamentalStrategy 类
- `__init__`: 初始化策略，从参数中获取LLM配置
- 核心分析方法:
  - `analyze_stock_fundamentals`: 主分析函数（已添加重试机制）
  - `get_stock_info`: 获取股票基本信息
  - `get_financial_data`: 获取财务数据
  - `calculate_financial_ratios`: 计算财务比率
  - `get_industry_info`: 获取行业信息
  - `create_analysis_prompt`: 创建LLM分析提示
  - `get_llm_analysis`: 调用LLM API获取分析结果（已添加重试机制）
- 执行方法:
  - `execute`: 策略执行入口
  - `generate_signals`: 生成交易信号
  - `calculate_position_size`: 计算仓位大小

#### FundamentalStockSelector 类
- `__init__`: 初始化代理，加载策略
- `_load_strategies_from_db`: 从数据库加载策略配置
- `_load_dynamic_strategies`: 动态加载策略类
- `get_standard_data`: 获取标准化股票数据
- `update_pool_with_fundamental_analysis`: 执行基本面分析并更新股票池
- `update_latest_pool_record`: 更新数据库中的股票池记录

## 运行逻辑

### 1. 初始化阶段
1. FundamentalStockSelector 初始化时调用 `_load_strategies_from_db()`
2. 从MongoDB数据库中查找名为"基本面分析Agent"的代理配置
3. 获取分配给该代理的策略ID列表
4. 根据策略ID从数据库加载每个策略的配置信息
5. 调用 `_load_dynamic_strategies()` 动态导入策略类

### 2. 数据准备阶段
1. 调用 `update_pool_with_fundamental_analysis()` 开始执行
2. 从数据库的"pool"集合中获取最新的股票池记录
3. 提取需要分析的股票代码列表
4. 调用 `get_standard_data()` 为每只股票获取90天的历史数据
5. 数据来源优先级: 缓存(buf_data) -> 在线获取(akshare)

### 3. 策略执行阶段
1. 遍历所有动态加载的策略实例
2. 对每只股票调用策略的 `execute()` 方法
3. 在LLM策略中:
   - 调用 `analyze_stock_fundamentals()` 进行基本面分析（最多重试3次）
   - 获取股票信息、财务数据、行业信息
   - 计算各种财务比率
   - 构造提示词并调用LLM API（最多重试3次）
   - 返回分析结果(评分和详细说明)
   - 当解析失败或访问大模型失败时，返回默认分数0.0

### 4. 结果处理阶段
1. 收集所有策略的分析结果
2. 调用 `update_latest_pool_record()` 更新股票池
3. 将分析结果保存到数据库中股票记录的"fund"字段
4. 记录分析完成时间(fund_at)

## 关键特性

### 1. 动态加载
- 策略配置存储在数据库中，支持动态加载
- 通过"program"字段指定策略文件和类名
- 支持多个策略同时执行

### 2. LLM集成
- 支持多种LLM提供商(通过配置api_url)
- API密钥通过环境变量配置(安全性)
- 可配置的模型和超参数(timeout, temperature等)

### 3. 财务分析
- 自动获取股票基本信息和财务数据
- 计算20+个关键财务比率
- 包含流动性、盈利能力、杠杆、效率等多个维度

### 4. 数据缓存
- 使用buf_data集合缓存历史数据
- 减少对数据源的请求频率
- 实现1秒请求间隔避免API限制

### 5. 评分标准化
- 自动将不同范围的评分标准化到0-1区间
- 支持分数四舍五入到指定精度

#### 评分处理详细说明
- **评分范围处理**：LLM策略在提示词中明确要求返回0-1范围的分数，因此不需要额外的标准化处理
- **默认评分**：当解析失败或访问大模型失败时，返回默认分数0.0
- **评分验证**：确保最终评分在0-1范围内，超出范围的值会被裁剪
- **评分精度**：评分四舍五入到小数点后2位
- **重试机制影响**：重试过程中，如果任何一次尝试成功，使用成功结果；如果全部失败，使用默认评分0.0

### 6. 重试机制
- 在解析失败或访问大模型失败时，自动重试最多3次
- 使用指数退避策略（1秒、2秒、4秒延迟）
- 如果所有重试都失败，返回默认分数0.0并继续处理下一只股票

## 配置灵活性

策略通过JSON配置文件定义，支持:
- 灵活的LLM提供商配置
- 可配置的API密钥环境变量名
- 可调整的模型参数和超参数
- 无需修改代码即可切换LLM服务提供商

这种架构设计使得LLM基本面分析策略具有高度的可配置性和可扩展性，能够适应不同的LLM服务提供商和分析需求。新增的重试机制进一步提高了系统的鲁棒性，确保即使在某些股票分析失败的情况下，也能继续处理其他股票，而不会中断整个分析过程。

