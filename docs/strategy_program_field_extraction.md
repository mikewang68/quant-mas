# Strategy Field Extraction Documentation

## Overview
This document describes the modifications made to extract file and class information from the `program` field in strategy documents.

## Changes Made

### 1. Weekly Selector Modification
Modified `agents/weekly_selector.py` to properly extract file and class information from the `program` field:

```python
# Extract file and class from program field if it exists
if 'program' in first_strategy and isinstance(first_strategy['program'], dict):
    self.strategy_file = first_strategy['program'].get('file', '')
    self.strategy_class_name = first_strategy['program'].get('class', '')
    self.logger.info(f"Loaded strategy file and class from program field")
else:
    # Fallback to direct file and class_name fields
    self.strategy_file = first_strategy.get('file', '')
    self.strategy_class_name = first_strategy.get('class_name', '')
```

### 2. Database Manager Modification
Modified `data/mongodb_manager.py` to handle field mapping for backward compatibility:

```python
# Handle backward compatibility: convert program field to file/class_name if needed
if 'program' in strategy and isinstance(strategy['program'], dict):
    if 'file' in strategy['program']:
        strategy['file'] = strategy['program']['file']
    if 'class' in strategy['program']:
        strategy['class_name'] = strategy['program']['class']
```

## Field Structure
Strategy documents can now have two formats:

### Format 1: Program Field (New Format)
```json
{
  "name": "Strategy Name",
  "type": "technical",
  "description": "Strategy description",
  "program": {
    "file": "strategy_file_name",
    "class": "StrategyClassName"
  },
  "parameters": {}
}
```

### Format 2: Direct Fields (Legacy Format)
```json
{
  "name": "Strategy Name",
  "type": "technical",
  "description": "Strategy description",
  "file": "strategy_file_name",
  "class_name": "StrategyClassName",
  "parameters": {}
}
```

## Testing
A test script `test/test_weekly_selector_program_field.py` has been created to verify that both formats are handled correctly.

## Benefits
1. Better organization of file and class information in a single `program` field
2. Backward compatibility with existing strategies using direct fields
3. Cleaner database structure for strategy documents

