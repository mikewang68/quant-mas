# Benchmark Index Data Implementation

## Overview
This document describes the implementation of benchmark index data fetching for the dashboard, allowing users to compare their portfolio performance against major Chinese indices.

## Implementation Details

### 1. Backend Implementation

#### AkshareClient Enhancement
A new method `get_index_data` was added to the `AkshareClient` class in `utils/akshare_client.py`:

```python
def get_index_data(self, index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Get historical data for an index.

    Args:
        index_code: Index code (e.g., '000016' for 上证50, '000300' for 沪深300, '000905' for 中证500)
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'

    Returns:
        DataFrame with index historical data
    """
```

This method uses akshare's `index_zh_a_hist` function to fetch historical data for Chinese indices.

#### API Endpoint
A new API endpoint was added in `web/app.py`:

```python
@app.route("/api/benchmark-data/<string:index_code>", methods=["GET"])
def get_benchmark_data(index_code):
    """Get benchmark index data for charting"""
```

This endpoint:
- Takes an index code as a parameter
- Fetches the last 2 years of historical data for that index
- Returns the data in JSON format for the frontend to consume

### 2. Frontend Implementation

#### Benchmark Selection
The dashboard HTML includes a dropdown for benchmark selection:

```html
<select class="form-select d-inline-block" id="benchmarkSelect" style="font-size: 0.9rem; padding: 0.25rem 0.5rem;">
    <option value="none">无对比</option>
    <option value="000016">上证50</option>
    <option value="000300" selected>沪深300</option>
    <option value="000905">中证500</option>
</select>
```

#### JavaScript Integration
The frontend JavaScript was modified to:
1. Fetch real benchmark data from the new API endpoint
2. Display the data on the dual Y-axis chart
3. Handle errors gracefully when data is not available

Key functions:
- `loadBenchmarkData()` - Fetches benchmark data from the API
- `updatePortfolioChart()` - Updates the chart with both portfolio and benchmark data

### 3. Chart Implementation

The portfolio performance chart now supports:
- Left Y-axis: Portfolio values (in currency)
- Right Y-axis: Index points
- Dual line display showing both portfolio performance and benchmark performance
- Interactive tooltips showing appropriate units for each axis

## Supported Benchmarks

1. **上证50 (000016)** - Shanghai Stock Exchange 50 Index
2. **沪深300 (000300)** - CSI 300 Index (default selection)
3. **中证500 (000905)** - CSI 500 Index

## Data Fetching Process

1. User selects a benchmark from the dropdown
2. Frontend JavaScript makes a request to `/api/benchmark-data/{index_code}`
3. Backend fetches historical data using akshare
4. Data is returned as JSON and plotted on the chart
5. Chart updates to show both portfolio performance and benchmark performance

## Error Handling

- If benchmark data is not available, the chart displays only portfolio data
- Network errors are logged to the console
- Invalid index codes return empty data sets gracefully

## Docker Permissions Issue

There is a known issue with Docker permissions that may prevent akshare from retrieving real data. See `docs/docker_permissions_fix.md` for instructions on how to fix this issue.

## Testing

To test the implementation:
1. Ensure Docker permissions are properly configured
2. Navigate to the dashboard
3. Select different benchmarks from the dropdown
4. Observe the chart updating with real index data
5. Verify that the dual Y-axis correctly displays portfolio values and index points

