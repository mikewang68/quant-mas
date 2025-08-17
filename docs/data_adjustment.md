# Data Adjustment Feature

## Overview

The quant trading system now supports configurable data adjustment settings. Users can choose between three types of data adjustment:

1. **No Adjustment** (default): Raw price data without any adjustments
2. **Pre-adjusted** (`qfq`): Forward adjusted prices that adjust historical prices for dividends and splits
3. **Post-adjusted** (`hfq`): Backward adjusted prices that adjust historical prices for dividends and splits

## Configuration

The data adjustment setting is stored in the MongoDB `config` collection and can be configured through the web interface:

1. Navigate to the Settings page
2. In the "交易参数" (Trading Parameters) section, find the "数据复权方式" (Data Adjustment Method) dropdown
3. Select one of the following options:
   - 不复权 (No Adjustment)
   - 前复权 (Pre-adjusted)
   - 后复权 (Post-adjusted)
4. Click "保存交易参数" (Save Trading Parameters)

## Implementation Details

### Backend

The data adjustment setting is implemented in the following components:

1. **MongoDBManager**: 
   - `get_adjustment_setting()` method retrieves the setting from the `config` collection
   - `get_k_data()` method uses the setting to select the appropriate price columns

2. **Web Interface**:
   - Settings page includes a dropdown for selecting the adjustment method
   - Configuration is saved to the `config` collection in MongoDB
   - Configuration is loaded when the page is initialized

### Data Storage

The system stores three versions of price data in MongoDB:

- **Raw prices**: `开盘`, `最高`, `最低`, `收盘` (open, high, low, close)
- **Pre-adjusted prices**: `开盘q`, `最高q`, `最低q`, `收盘q` (open_qfq, high_qfq, low_qfq, close_qfq)
- **Post-adjusted prices**: `开盘h`, `最高h`, `最低h`, `收盘h` (open_hfq, high_hfq, low_hfq, close_hfq)

When retrieving data, the system automatically selects the appropriate columns based on the user's configuration.

## Usage in Strategies

Strategies and backtesting modules automatically use the configured adjustment setting when retrieving data from MongoDB. No changes are needed in existing strategy code.

## API Endpoints

The following API endpoints handle the data adjustment configuration:

- `GET /api/config`: Retrieve current configuration including data adjustment setting
- `POST /api/config`: Save configuration including data adjustment setting

## Example Usage

```python
from data.mongodb_manager import MongoDBManager

# Initialize MongoDB manager
db_manager = MongoDBManager()

# Get current adjustment setting
adjust_setting = db_manager.get_adjustment_setting()
print(f"Current adjustment setting: {adjust_setting}")

# Get stock data with automatic adjustment
k_data = db_manager.get_k_data("000001", "2023-01-01", "2023-12-31")
# The data will be automatically adjusted based on the configuration
```

