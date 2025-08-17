# Strategy Program Creation Documentation

## Overview

This document explains how the automatic strategy program file creation functionality works in the quant trading system. When a new strategy is created through the web interface or API, the system can automatically generate a template program file for that strategy.

## How It Works

### 1. Automatic Program File Creation

When a strategy is created or updated with a `program` field in the database, the system automatically:

1. Checks if a program file with that name already exists
2. If not, creates a new program file in the `strategies/` directory
3. Generates a template based on the strategy type (technical, fundamental, ML, etc.)

### 2. Program Manager Utility

The `utils/program_manager.py` module contains the `create_strategy_program_file()` function that handles program file creation:

```python
def create_strategy_program_file(strategy_name: str, strategy_type: str = "technical") -> Optional[str]:
    """
    Automatically create an empty strategy program file if it doesn't exist.
    
    Args:
        strategy_name: Name of the strategy
        strategy_type: Type of strategy (technical, fundamental, etc.)
        
    Returns:
        Path to the created program file or None if creation failed
    """
```

### 3. Integration with MongoDB

The `data/mongodb_manager.py` module has been modified to automatically call the program creation function when strategies are created or updated:

- In `create_strategy()` method
- In `update_strategy()` method

## Strategy Types and Templates

The system supports different strategy types with specific templates:

### Technical Analysis Strategies
- Template includes TA-Lib integration
- Example signal generation logic
- Common technical indicators setup

### Fundamental Analysis Strategies
- Template for fundamental data processing
- Structure for financial ratio analysis
- Position sizing based on valuation metrics

### Machine Learning Strategies
- Template for ML model integration
- Structure for feature engineering
- Prediction-based signal generation

## Web Interface Integration

The web interface at `/strategies` allows users to:

1. Create new strategies with a "执行程序" (execution program) field
2. Edit existing strategies and update the program field
3. The system automatically creates program files when needed

## File Naming Convention

Program files are automatically named based on the strategy name:

1. Convert to lowercase
2. Replace spaces and special characters with underscores
3. Add `_strategy.py` suffix
4. Example: "Moving Average Crossover" becomes `moving_average_crossover_strategy.py`

## Class Naming Convention

Strategy classes are automatically named based on the strategy name:

1. Convert to CamelCase
2. Append "Strategy" suffix
3. Example: "Moving Average Crossover" becomes `MovingAverageCrossoverStrategy`

## Testing

A test script is available at `test/test_program_creation.py` to verify the functionality:

```bash
python test/test_program_creation.py
```

## Usage Examples

### Creating a Strategy via API

When creating a strategy via the API, include the `program` field:

```json
{
  "name": "My New Strategy",
  "type": "technical",
  "description": "A new technical strategy",
  "program": "my_new_strategy.py",
  "parameters": {}
}
```

The system will automatically create `strategies/my_new_strategy.py` with a proper template.

### Updating a Strategy

When updating a strategy and changing the program field, a new program file will be created if it doesn't exist.

## Best Practices

1. **Naming**: Use descriptive strategy names for better file and class naming
2. **Types**: Specify the correct strategy type for appropriate template generation
3. **Parameters**: Define strategy parameters in the database for use in the program
4. **Implementation**: Customize the generated template with your specific strategy logic

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the `utils/program_manager.py` file is accessible
2. **Permission Errors**: Check write permissions for the `strategies/` directory
3. **Naming Conflicts**: Avoid special characters in strategy names for cleaner file names

### Logs

Check the application logs for program creation success/failure messages:
- Successful creation: "Created program file: /path/to/file.py"
- Failure: "Failed to create program file for strategy: StrategyName"

## Future Enhancements

1. **Template Customization**: Allow custom templates based on strategy categories
2. **Validation**: Add program file validation to ensure proper structure
3. **Integration**: Better integration with strategy execution and backtesting

