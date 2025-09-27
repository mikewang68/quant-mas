# Portfolio Assets API Documentation

## Overview

The Portfolio Assets API provides detailed daily portfolio performance data based on account trading orders and real-time stock prices. This API generates a comprehensive asset breakdown for each day, including stock holdings, cash positions, and total portfolio value.

## Endpoint

```
GET /api/portfolio-assets/{account_id}
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | string | The unique identifier of the account to analyze |

## Response Format

The API returns a JSON object with the following structure:

```json
{
  "account_id": "string",
  "account_name": "string",
  "initial_capital": number,
  "asset_data": [
    {
      "date": "YYYY-MM-DD",
      "stock_code": "string or null",
      "close_price": number,
      "quantity": number,
      "holding_value": number,
      "cash": number,
      "total_assets": number
    }
  ]
}
```

## Data Fields

| Field | Description |
|-------|-------------|
| `account_id` | The unique identifier of the account |
| `account_name` | The name of the account |
| `initial_capital` | The initial capital of the account |
| `asset_data` | Array of daily asset records |
| `date` | The date of the record |
| `stock_code` | Stock code for the holding (null when no holdings) |
| `close_price` | Closing price of the stock on that date |
| `quantity` | Number of shares held |
| `holding_value` | Total value of the stock holding (quantity × close_price) |
| `cash` | Available cash in the account |
| `total_assets` | Total portfolio value (cash + all stock holdings) |

## Implementation Details

### Data Processing Steps

1. **Account Retrieval**: The API first retrieves the account information from the database using the provided account ID.

2. **Order Collection**: All trading orders for the account are fetched and sorted chronologically by date.

3. **Date Range Determination**: The date range is determined from the first order date to the current date.

4. **Stock Data Collection**: For each unique stock in the orders, historical price data is fetched using the Akshare client from the first order date to the current date.

5. **Daily Processing**: For each day in the date range:
   - Process any orders that occurred on that date
   - Update cash and stock holdings accordingly
   - Calculate total portfolio value (cash + stock holdings)
   - Generate a record for each stock holding

6. **Special Cases**:
   - When stocks are sold, holdings are removed from the portfolio
   - On days with no holdings, only cash and total assets are recorded
   - Historical stock prices are used to calculate daily holding values

### Key Features

1. **Accurate Asset Tracking**: The API tracks the exact quantity of each stock held and calculates its value using historical closing prices.

2. **Cash Flow Management**: All buying and selling transactions properly update the cash balance, including commissions.

3. **Comprehensive Coverage**: The API covers all trading days from the first order to the current date, providing a complete historical view.

4. **Real-time Data Integration**: Stock prices are fetched using the Akshare client to ensure accurate historical pricing.

5. **Proper Date Handling**: The API correctly handles weekends and holidays by finding the closest available price data.

## Usage Examples

### JavaScript/Fetch API

```javascript
fetch('/api/portfolio-assets/507f1f77bcf86cd799439011')
  .then(response => response.json())
  .then(data => {
    console.log('Account:', data.account_name);
    console.log('Asset records:', data.asset_data.length);

    // Display first few records
    data.asset_data.slice(0, 5).forEach(record => {
      console.log(`${record.date}: ¥${record.total_assets.toFixed(2)} total assets`);
    });
  })
  .catch(error => {
    console.error('Error fetching portfolio assets:', error);
  });
```

### Python/Requests

```python
import requests

response = requests.get('http://localhost:5000/api/portfolio-assets/507f1f77bcf86cd799439011')
if response.status_code == 200:
    data = response.json()
    print(f"Account: {data['account_name']}")
    print(f"Asset records: {len(data['asset_data'])}")

    # Display first few records
    for record in data['asset_data'][:5]:
        print(f"{record['date']}: ¥{record['total_assets']:.2f} total assets")
else:
    print(f"Error: {response.status_code}")
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `200 OK`: Successful response with data
- `404 Not Found`: Account not found
- `500 Internal Server Error`: Database or processing error

Error responses include a JSON object with an `error` field describing the issue.

## Testing

A test script is available at `test/test_portfolio_assets_api.py` to verify the functionality of this endpoint.

## Related Endpoints

- `/api/accounts`: Get list of all accounts
- `/api/orders`: Get trading orders
- `/api/account-performance/{account_id}`: Get account performance data for charting

