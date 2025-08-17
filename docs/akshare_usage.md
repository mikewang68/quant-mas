# Akshare 使用说明文档

## 简介

Akshare 是一个基于 Python 的开源金融数据接口库，提供了丰富的中国金融市场数据接口。本项目使用 Akshare 来获取股票、期货、外汇等金融数据。

## 安装

Akshare 已包含在项目的 requirements.txt 文件中。如果需要单独安装，可以使用以下命令：

```bash
pip install akshare
```

## 主要功能

### 1. 股票数据获取

#### 获取股票列表
```python
from utils.akshare_client import akshare_client

# 获取所有A股股票代码
stock_codes = akshare_client.get_stock_list()
print(f"共获取到 {len(stock_codes)} 只股票")
```

#### 获取股票详细信息
```python
# 获取特定股票的详细信息
stock_info = akshare_client.get_stock_info("000001")
if stock_info:
    print(stock_info)
```

#### 获取日K线数据
```python
# 获取股票日K线数据
start_date = "2023-01-01"
end_date = "2023-12-31"
k_data = akshare_client.get_daily_k_data("000001", start_date, end_date, adjust_type="q")
print(k_data.head())
```

#### 获取周K线数据
```python
# 获取股票周K线数据
k_data = akshare_client.get_weekly_k_data("000001", start_date, end_date)
print(k_data.head())
```

#### 获取实时数据
```python
# 获取股票实时数据
realtime_data = akshare_client.get_realtime_data(["000001", "000002"])
print(realtime_data)
```

### 2. 调整类型说明

Akshare 支持多种价格调整类型：

- `none`: 不复权
- `q`: 前复权 (默认)
- `h`: 后复权

## 数据字段说明

### K线数据字段
| 字段名 | 说明 |
|--------|------|
| date | 日期 |
| open | 开盘价 |
| close | 收盘价 |
| high | 最高价 |
| low | 最低价 |
| volume | 成交量 |
| amount | 成交额 |

### 实时数据字段
| 字段名 | 说明 |
|--------|------|
| code | 股票代码 |
| name | 股票名称 |
| price | 最新价 |
| pct_change | 涨跌幅 |
| change_amount | 涨跌额 |
| volume | 成交量 |
| amount | 成交额 |
| open | 开盘价 |
| high | 最高价 |
| low | 最低价 |
| prev_close | 昨收价 |

## 使用示例

```python
from utils.akshare_client import akshare_client
from datetime import datetime, timedelta

# 初始化客户端
client = akshare_client

# 获取股票列表
codes = client.get_stock_list()
print(f"获取到 {len(codes)} 只股票")

# 选择一只股票进行分析
if codes:
    stock_code = codes[0]
    
    # 获取股票信息
    info = client.get_stock_info(stock_code)
    print(f"{stock_code} 的信息: {info}")
    
    # 获取最近30天的日K线数据
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    daily_k_data = client.get_daily_k_data(stock_code, start_date, end_date)
    print(f"{stock_code} 最近30天的日K线数据:")
    print(daily_k_data)
```

## 注意事项

1. **网络连接**: Akshare 需要稳定的网络连接来获取数据，请确保网络畅通。

2. **请求频率**: 避免过于频繁的数据请求，以免对数据源服务器造成压力。

3. **数据时效性**: 实时数据可能存在一定的延迟，请以实际交易为准。

4. **错误处理**: 在使用 Akshare 接口时，应适当处理可能出现的异常情况。

5. **数据格式**: 返回的数据通常为 pandas DataFrame 格式，便于进一步处理和分析。

## 常见问题

### 1. 数据获取失败
如果遇到数据获取失败的情况，请检查：
- 网络连接是否正常
- 股票代码是否正确
- 日期格式是否正确 (YYYY-MM-DD)

### 2. 数据为空
如果返回的数据为空，可能是因为：
- 请求的时间段内没有交易数据
- 股票代码不存在或已退市
- 数据源暂时不可用

## 参考资源

- [Akshare 官方文档](https://akshare.readthedocs.io/)
- [Akshare GitHub 仓库](https://github.com/akfamily/akshare)

