"""
Base agent class for the multi-agent quant trading system.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import pandas as pd

# Configure logger
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the quant trading system.
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """
        Initialize the base agent.
        
        Args:
            name: Name of the agent
            config: Configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """
        Main execution method for the agent.
        Must be implemented by subclasses.
        """
        pass
    
    def log_info(self, message: str):
        """Log info message with agent name"""
        self.logger.info(f"[{self.name}] {message}")
    
    def log_warning(self, message: str):
        """Log warning message with agent name"""
        self.logger.warning(f"[{self.name}] {message}")
    
    def log_error(self, message: str):
        """Log error message with agent name"""
        self.logger.error(f"[{self.name}] {message}")

# Example usage
if __name__ == "__main__":
    # This is an abstract class, so we can't instantiate it directly
    pass

