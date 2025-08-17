"""
Program Manager Utility
Handles automatic creation and management of strategy program files.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logger
logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
STRATEGIES_DIR = PROJECT_ROOT / "strategies"


def create_strategy_program_file(strategy_name: str, strategy_type: str = "technical") -> Optional[str]:
    """
    Automatically create an empty strategy program file if it doesn't exist.
    
    Args:
        strategy_name: Name of the strategy
        strategy_type: Type of strategy (technical, fundamental, etc.)
        
    Returns:
        Path to the created program file or None if creation failed
    """
    try:
        # Generate a valid filename from the strategy name
        # Convert to lowercase, replace spaces with underscores, remove special characters
        filename_base = "".join(c.lower() if c.isalnum() else "_" for c in strategy_name)
        # Remove multiple consecutive underscores
        while "__" in filename_base:
            filename_base = filename_base.replace("__", "_")
        # Remove leading/trailing underscores
        filename_base = filename_base.strip("_")
        
        # Add suffix
        filename = f"{filename_base}_strategy.py"
        file_path = STRATEGIES_DIR / filename
        
        # Check if file already exists
        if file_path.exists():
            logger.info(f"Program file {filename} already exists")
            return str(file_path)
        
        # Create the strategy class name
        class_name_words = [word.capitalize() for word in strategy_name.replace("_", " ").split()]
        class_name = "".join(class_name_words) + "Strategy"
        
        # Create the file content based on strategy type
        if strategy_type == "technical":
            content = _generate_technical_strategy_template(strategy_name, class_name)
        elif strategy_type == "fundamental":
            content = _generate_fundamental_strategy_template(strategy_name, class_name)
        elif strategy_type == "ml":
            content = _generate_ml_strategy_template(strategy_name, class_name)
        else:
            content = _generate_generic_strategy_template(strategy_name, class_name)
        
        # Write the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Created program file {filename} for strategy '{strategy_name}'")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"Error creating program file for strategy '{strategy_name}': {e}")
        return None


def _generate_technical_strategy_template(strategy_name: str, class_name: str) -> str:
    """Generate a template for technical analysis strategies."""
    return f'''"""
{strategy_name} Strategy
Auto-generated strategy template for {strategy_name}
"""

import pandas as pd
import numpy as np
import talib
from typing import Dict, Optional
from strategies.base_strategy import BaseStrategy

class {class_name}(BaseStrategy):
    """
    {strategy_name} Strategy
    TODO: Add strategy description here
    """
    
    def __init__(self, name: str = "{strategy_name}", params: Optional[Dict] = None):
        """
        Initialize the {strategy_name} strategy.
        
        Args:
            name: Strategy name
            params: Strategy parameters
                - TODO: Add parameter descriptions
        """
        super().__init__(name, params)
        
        # Strategy parameters
        # TODO: Add strategy parameters here
        self.logger.info(f"Initialized {{self.name}} strategy with params: {{self.params}}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals.
        
        Args:
            data: DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']
            
        Returns:
            DataFrame with signals
        """
        if not self.validate_data(data):
            return pd.DataFrame()
        
        # TODO: Implement signal generation logic
        signals = pd.DataFrame(index=data.index)
        signals['date'] = data['date']
        signals['close'] = data['close']
        signals['signal'] = 'HOLD'
        signals['position'] = 0.0
        
        # Example implementation (replace with actual logic):
        # for i in range(1, len(signals)):
        #     # Buy signal condition
        #     if some_condition:
        #         signals.loc[i, 'signal'] = 'BUY'
        #         signals.loc[i, 'position'] = 1.0
        #     
        #     # Sell signal condition
        #     elif some_other_condition:
        #         signals.loc[i, 'signal'] = 'SELL'
        #         signals.loc[i, 'position'] = -1.0
        #     
        #     # Hold signal
        #     else:
        #         signals.loc[i, 'signal'] = 'HOLD'
        #         signals.loc[i, 'position'] = signals.loc[i-1, 'position']
        
        return signals
    
    def calculate_position_size(self, signal: str, portfolio_value: float, 
                              price: float) -> float:
        """
        Calculate position size based on signal.
        
        Args:
            signal: Trading signal ('BUY', 'SELL', 'HOLD')
            portfolio_value: Current portfolio value
            price: Current asset price
            
        Returns:
            Position size (number of shares)
        """
        # TODO: Implement position sizing logic
        if signal == 'BUY':
            # Example: 10% of portfolio value
            position_value = portfolio_value * 0.1
            shares = position_value / price
            return float(shares)
        elif signal == 'SELL':
            return -100.0  # Placeholder
        else:
            return 0.0

# Example usage
if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    sample_data = pd.DataFrame({{
        'date': dates,
        'open': np.random.uniform(100, 110, 100),
        'high': np.random.uniform(110, 120, 100),
        'low': np.random.uniform(90, 100, 100),
        'close': np.random.uniform(100, 110, 100),
        'volume': np.random.uniform(1000000, 2000000, 100)
    }})
    
    # Initialize strategy
    strategy = {class_name}()
    
    # Generate signals
    signals = strategy.generate_signals(sample_data)
    print(f"Generated {{len(signals[signals['signal'] != 'HOLD'])}} trading signals")
    print(signals.tail(10))
'''


def _generate_fundamental_strategy_template(strategy_name: str, class_name: str) -> str:
    """Generate a template for fundamental analysis strategies."""
    return f'''"""
{strategy_name} Strategy
Auto-generated strategy template for {strategy_name}
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from strategies.base_strategy import BaseStrategy

class {class_name}(BaseStrategy):
    """
    {strategy_name} Strategy
    TODO: Add strategy description here
    """
    
    def __init__(self, name: str = "{strategy_name}", params: Optional[Dict] = None):
        """
        Initialize the {strategy_name} strategy.
        
        Args:
            name: Strategy name
            params: Strategy parameters
                - TODO: Add parameter descriptions
        """
        super().__init__(name, params)
        
        # Strategy parameters
        # TODO: Add strategy parameters here
        self.logger.info(f"Initialized {{self.name}} strategy with params: {{self.params}}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on fundamental data.
        
        Args:
            data: DataFrame with fundamental data
            
        Returns:
            DataFrame with signals
        """
        if not self.validate_data(data):
            return pd.DataFrame()
        
        # TODO: Implement signal generation logic
        signals = pd.DataFrame(index=data.index)
        signals['date'] = data['date']
        signals['close'] = data['close']
        signals['signal'] = 'HOLD'
        signals['position'] = 0.0
        
        return signals
    
    def calculate_position_size(self, signal: str, portfolio_value: float, 
                              price: float) -> float:
        """
        Calculate position size based on signal.
        
        Args:
            signal: Trading signal ('BUY', 'SELL', 'HOLD')
            portfolio_value: Current portfolio value
            price: Current asset price
            
        Returns:
            Position size (number of shares)
        """
        # TODO: Implement position sizing logic
        if signal == 'BUY':
            # Example: 10% of portfolio value
            position_value = portfolio_value * 0.1
            shares = position_value / price
            return float(shares)
        elif signal == 'SELL':
            return -100.0  # Placeholder
        else:
            return 0.0

# Example usage
if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # TODO: Add example usage
    pass
'''


def _generate_ml_strategy_template(strategy_name: str, class_name: str) -> str:
    """Generate a template for machine learning strategies."""
    return f'''"""
{strategy_name} Strategy
Auto-generated strategy template for {strategy_name}
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from strategies.base_strategy import BaseStrategy

class {class_name}(BaseStrategy):
    """
    {strategy_name} Strategy
    TODO: Add strategy description here
    """
    
    def __init__(self, name: str = "{strategy_name}", params: Optional[Dict] = None):
        """
        Initialize the {strategy_name} strategy.
        
        Args:
            name: Strategy name
            params: Strategy parameters
                - TODO: Add parameter descriptions
        """
        super().__init__(name, params)
        
        # Strategy parameters
        # TODO: Add strategy parameters here
        self.logger.info(f"Initialized {{self.name}} strategy with params: {{self.params}}")
        
        # ML model
        self.model = None
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals using ML model.
        
        Args:
            data: DataFrame with features for prediction
            
        Returns:
            DataFrame with signals
        """
        if not self.validate_data(data):
            return pd.DataFrame()
        
        # TODO: Implement ML model prediction logic
        signals = pd.DataFrame(index=data.index)
        signals['date'] = data['date']
        signals['close'] = data['close']
        signals['signal'] = 'HOLD'
        signals['position'] = 0.0
        
        return signals
    
    def calculate_position_size(self, signal: str, portfolio_value: float, 
                              price: float) -> float:
        """
        Calculate position size based on signal.
        
        Args:
            signal: Trading signal ('BUY', 'SELL', 'HOLD')
            portfolio_value: Current portfolio value
            price: Current asset price
            
        Returns:
            Position size (number of shares)
        """
        # TODO: Implement position sizing logic
        if signal == 'BUY':
            # Example: 10% of portfolio value
            position_value = portfolio_value * 0.1
            shares = position_value / price
            return float(shares)
        elif signal == 'SELL':
            return -100.0  # Placeholder
        else:
            return 0.0

# Example usage
if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # TODO: Add example usage
    pass
'''


def _generate_generic_strategy_template(strategy_name: str, class_name: str) -> str:
    """Generate a generic strategy template."""
    return f'''"""
{strategy_name} Strategy
Auto-generated strategy template for {strategy_name}
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from strategies.base_strategy import BaseStrategy

class {class_name}(BaseStrategy):
    """
    {strategy_name} Strategy
    TODO: Add strategy description here
    """
    
    def __init__(self, name: str = "{strategy_name}", params: Optional[Dict] = None):
        """
        Initialize the {strategy_name} strategy.
        
        Args:
            name: Strategy name
            params: Strategy parameters
                - TODO: Add parameter descriptions
        """
        super().__init__(name, params)
        
        # Strategy parameters
        # TODO: Add strategy parameters here
        self.logger.info(f"Initialized {{self.name}} strategy with params: {{self.params}}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals.
        
        Args:
            data: DataFrame with required data
            
        Returns:
            DataFrame with signals
        """
        if not self.validate_data(data):
            return pd.DataFrame()
        
        # TODO: Implement signal generation logic
        signals = pd.DataFrame(index=data.index)
        signals['date'] = data['date']
        signals['close'] = data['close']
        signals['signal'] = 'HOLD'
        signals['position'] = 0.0
        
        return signals
    
    def calculate_position_size(self, signal: str, portfolio_value: float, 
                              price: float) -> float:
        """
        Calculate position size based on signal.
        
        Args:
            signal: Trading signal ('BUY', 'SELL', 'HOLD')
            portfolio_value: Current portfolio value
            price: Current asset price
            
        Returns:
            Position size (number of shares)
        """
        # TODO: Implement position sizing logic
        if signal == 'BUY':
            # Example: 10% of portfolio value
            position_value = portfolio_value * 0.1
            shares = position_value / price
            return float(shares)
        elif signal == 'SELL':
            return -100.0  # Placeholder
        else:
            return 0.0

# Example usage
if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # TODO: Add example usage
    pass
'''


def validate_program_file(program_path: str) -> Dict[str, Any]:
    """
    Validate that a program file exists and is executable.
    
    Args:
        program_path: Path to the program file
        
    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": False,
        "exists": False,
        "is_file": False,
        "has_content": False,
        "is_python": False,
        "has_class": False,
        "errors": []
    }
    
    try:
        program_file = Path(program_path)
        
        # Check if file exists
        result["exists"] = program_file.exists()
        if not result["exists"]:
            result["errors"].append("File does not exist")
            return result
            
        # Check if it's a file (not directory)
        result["is_file"] = program_file.is_file()
        if not result["is_file"]:
            result["errors"].append("Path is not a file")
            return result
            
        # Check if file has content
        if program_file.stat().st_size > 0:
            result["has_content"] = True
        else:
            result["errors"].append("File is empty")
            
        # Check if it's a Python file
        if program_file.suffix.lower() == '.py':
            result["is_python"] = True
        else:
            result["errors"].append("File is not a Python file")
            
        # If we have a Python file with content, check for class definition
        if result["has_content"] and result["is_python"]:
            try:
                content = program_file.read_text(encoding='utf-8')
                # Simple check for class definition
                if 'class ' in content and '(BaseStrategy)' in content:
                    result["has_class"] = True
                else:
                    result["errors"].append("File does not contain a BaseStrategy class")
            except Exception as e:
                result["errors"].append(f"Error reading file content: {e}")
        
        # Mark as valid if no errors
        result["valid"] = len(result["errors"]) == 0
        
    except Exception as e:
        logger.error(f"Error validating program file {program_path}: {e}")
        result["errors"].append(f"Validation error: {e}")
        
    return result


def validate_strategy_class(program_path: str, expected_class_name: str = None) -> Dict[str, Any]:
    """
    Validate that a program file contains a proper strategy class.
    
    Args:
        program_path: Path to the program file
        expected_class_name: Expected class name (optional)
        
    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": False,
        "class_found": False,
        "inherits_base": False,
        "has_required_methods": False,
        "class_name": None,
        "errors": []
    }
    
    try:
        program_file = Path(program_path)
        
        # Check if file exists and is a file
        if not (program_file.exists() and program_file.is_file()):
            result["errors"].append("File does not exist or is not a file")
            return result
            
        # Read file content
        content = program_file.read_text(encoding='utf-8')
        
        # Look for class definition
        import re
        class_pattern = r"class\s+(\w+)\s*(?:\(([^)]+)\))?:"
        class_matches = re.findall(class_pattern, content)
        
        if not class_matches:
            result["errors"].append("No class definition found")
            return result
            
        # Check each class found
        for class_name, parent_classes in class_matches:
            result["class_name"] = class_name
            
            # Check if this is the expected class
            if expected_class_name and class_name != expected_class_name:
                continue
                
            result["class_found"] = True
            
            # Check inheritance
            if parent_classes and 'BaseStrategy' in parent_classes:
                result["inherits_base"] = True
            elif parent_classes:
                # Check if any parent imports BaseStrategy
                for parent in parent_classes.split(','):
                    parent = parent.strip()
                    if parent == 'BaseStrategy':
                        result["inherits_base"] = True
                        break
            
            # Check for required methods
            required_methods = ['generate_signals', 'calculate_position_size']
            method_pattern = r"def\s+(\w+)\s*\("
            methods = re.findall(method_pattern, content)
            
            found_methods = [method for method in required_methods if method in methods]
            if len(found_methods) == len(required_methods):
                result["has_required_methods"] = True
            else:
                missing = set(required_methods) - set(found_methods)
                result["errors"].append(f"Missing required methods: {', '.join(missing)}")
            
            # If this is the expected class, break
            if expected_class_name and class_name == expected_class_name:
                break
                
        if not result["class_found"]:
            if expected_class_name:
                result["errors"].append(f"Expected class '{expected_class_name}' not found")
            else:
                result["errors"].append("No valid strategy class found")
                
        # Mark as valid if all checks pass
        result["valid"] = (result["class_found"] and result["inherits_base"] and 
                          result["has_required_methods"] and len(result["errors"]) == 0)
        
    except Exception as e:
        logger.error(f"Error validating strategy class in {program_path}: {e}")
        result["errors"].append(f"Validation error: {e}")
        
    return result

