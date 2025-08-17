# Strategy Output Saving to Pool Collection

This document explains how to automatically save strategy output results to the MongoDB "pool" collection using the new utility functions.

## Overview

The system now provides built-in functionality to automatically save strategy results to the pool collection, making it easy for any strategy to persist its output without manual implementation.

## Key Components

### 1. DatabaseOperations.save_strategy_output_to_pool()

This method in `data/database_operations.py` provides a standardized way to save strategy results:

```python
def save_strategy_output_to_pool(self, strategy_key: str, agent_name: str, strategy_id: str,
                               strategy_name: str, stocks: List[Dict], date: str,
                               last_data_date: Optional[str] = None,
                               strategy_params: Optional[Dict] = None,
                               additional_metadata: Optional[Dict] = None) -> bool:
```

**Parameters:**
- `strategy_key`: Unique identifier for this strategy execution
- `agent_name`: Name of the agent executing the strategy
- `strategy_id`: Strategy identifier
- `strategy_name`: Human-readable strategy name
- `stocks`: List of selected stocks with analysis data
- `date`: Selection date
- `last_data_date`: Reference date for data used (optional)
- `strategy_params`: Strategy parameters used (optional)
- `additional_metadata`: Additional information to store (optional)

### 2. BaseStrategy.save_to_pool()

This convenience method in `strategies/base_strategy.py` makes it even easier for strategies to save their results:

```python
def save_to_pool(self, db_manager, agent_name: str, stocks: List[Dict], 
                 date: str, strategy_params: Optional[Dict] = None,
                 additional_metadata: Optional[Dict] = None) -> bool:
```

## Usage Examples

### Using BaseStrategy.save_to_pool() (Recommended)

```python
from strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def execute(self, stock_data: Dict[str, pd.DataFrame], 
                agent_name: str, db_manager) -> List[Dict]:
        # Your strategy logic here
        selected_stocks = []
        
        # ... analysis code ...
        
        # Automatically save results to pool
        if selected_stocks:
            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            self.save_to_pool(
                db_manager=db_manager,
                agent_name=agent_name,
                stocks=selected_stocks,
                date=current_date,
                strategy_params=self.params,  # Optional
                additional_metadata={'version': '1.0'}  # Optional
            )
        
        return selected_stocks
```

### Using DatabaseOperations.save_strategy_output_to_pool() Directly

```python
from data.database_operations import DatabaseOperations

# In your code
db_ops = DatabaseOperations(db_manager)

success = db_ops.save_strategy_output_to_pool(
    strategy_key="my_strategy_2025-32",
    agent_name="MyAgent",
    strategy_id="my_strategy",
    strategy_name="My Strategy",
    stocks=selected_stocks,
    date="2025-08-15",
    strategy_params={"param1": "value1"},
    additional_metadata={"execution_time": datetime.now()}
)
```

## Data Structure

The saved records in the pool collection will have the following structure:

```json
{
  "_id": "strategy_key",
  "agent_name": "Agent Name",
  "strategy_id": "strategy_id",
  "strategy_name": "Strategy Name",
  "strategy_parameters": {"param1": "value1"},
  "year": 2025,
  "week": 32,
  "selection_date": "2025-08-15T00:00:00",
  "reference_date": "2025-08-15T00:00:00",
  "stocks": [
    {
      "code": "000001",
      "selection_reason": "Reason for selection",
      "score": 0.85,
      "technical_analysis": {
        "rsi": 55.2,
        "macd": {"line": 0.12, "signal": 0.08}
      }
    }
  ],
  "count": 1,
  "created_at": "2025-08-15T10:30:00",
  "updated_at": "2025-08-15T10:30:00"
}
```

## Best Practices

1. **Use Unique Strategy Keys**: Create meaningful strategy keys to avoid conflicts
2. **Include Metadata**: Add relevant metadata for better tracking and analysis
3. **Handle Errors**: Always check the return value to ensure saving was successful
4. **Consistent Stock Data Structure**: Follow the standard structure for stock data to ensure consistency

## Testing

See the test scripts for examples:
- `test/demo_strategy_output_saving.py`: Basic demonstration
- `test/test_strategy_pool_saving.py`: Complete workflow test
- `strategies/demo_strategy.py`: Example strategy implementation

Run tests with:
```bash
python test/demo_strategy_output_saving.py
python test/test_strategy_pool_saving.py
```

