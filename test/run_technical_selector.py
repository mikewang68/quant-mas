#!/usr/bin/env python3
"""
Run the technical stock selector to select stocks using multiple strategies 
and save results to pool collection
"""

import sys
import os
import logging

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.technical_selector import TechnicalStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def get_agent_strategies(db_manager):
    """Get strategy IDs associated with the technical analysis agent"""
    try:
        # Find the technical analysis agent
        agents = db_manager.get_agents()
        technical_agent = None
        for agent in agents:
            if "技术分析" in agent.get("name", ""):
                technical_agent = agent
                break
        
        if not technical_agent:
            logger.error("Technical analysis agent not found")
            return []
            
        strategy_ids = technical_agent.get("strategies", [])
        logger.info(f"Found {len(strategy_ids)} strategies for technical analysis agent: {strategy_ids}")
        return strategy_ids
        
    except Exception as e:
        logger.error(f"Error getting agent strategies: {e}")
        return []


def main():
    """Main function to run the technical stock selector"""
    try:
        # Initialize components
        logger.info("Initializing components...")
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()
        
        # Get strategy IDs associated with the technical analysis agent
        strategy_ids = get_agent_strategies(db_manager)
        
        if not strategy_ids:
            logger.error("No strategies found for technical analysis agent")
            sys.exit(1)
        
        # Initialize selector with empty default params (strategies will provide their own params)
        logger.info("Initializing technical stock selector...")
        selector = TechnicalStockSelector(db_manager, data_fetcher, {})
        
        # Execute strategies
        logger.info(f"Executing {len(strategy_ids)} strategies...")
        results = selector.run(strategy_ids)
        logger.info(f"Execution completed: {results}")
        
        # Close database connection
        db_manager.close_connection()
        logger.info("Technical stock selection completed")
        
    except Exception as e:
        logger.error(f"Error running technical stock selector: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

