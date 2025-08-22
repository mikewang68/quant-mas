"""
Web interface for the quant trading system.
Provides REST API and web UI for system monitoring and control.
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import logging
from typing import Dict, Any
import os
import sys
import yaml
from bson.objectid import ObjectId
import akshare as ak
from datetime import datetime

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

# Configure logger
logger = logging.getLogger(__name__)


def create_app():
    """
    Create Flask application for the web interface.

    Returns:
        Flask application instance
    """
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
    )

    # Enable CORS
    CORS(app)

    # Configure app
    app.config["SECRET_KEY"] = "your-secret-key-here"

    # Initialize MongoDBManager
    try:
        mongo_manager = MongoDBManager()
        app.config["MONGO_MANAGER"] = mongo_manager
        app.config["MONGO_DB"] = mongo_manager.db
        logger.info("Successfully initialized MongoDBManager")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDBManager: {e}")
        app.config["MONGO_MANAGER"] = None
        app.config["MONGO_DB"] = None

    # Register routes
    register_routes(app)

    return app


def register_routes(app: Flask):
    """
    Register routes for the web application.

    Args:
        app: Flask application instance
    """

    @app.route("/")
    def index():
        """Main index page"""
        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():
        """Dashboard page"""
        return render_template("dashboard.html")

    @app.route("/strategies")
    def strategies():
        """Strategies page"""
        return render_template("strategies.html")

    @app.route("/backtest")
    def backtest():
        """Backtest page"""
        return render_template("backtest.html")

    @app.route("/stocks")
    def stocks():
        """Stocks page"""
        return render_template("stocks.html")

    @app.route("/settings")
    def settings():
        """Settings page"""
        return render_template("settings.html")

    @app.route("/api/status")
    def get_status():
        """Get system status"""
        status = {
            "system": "running",
            "timestamp": "2023-01-01T00:00:00Z",
            "version": "1.0.0",
        }
        return jsonify(status)

    @app.route("/api/stocks")
    def get_stocks():
        """Get list of tracked stocks"""
        stocks = [
            {"code": "000001", "name": "平安银行", "price": 15.23},
            {"code": "000002", "name": "万科A", "price": 22.45},
            {"code": "600000", "name": "浦发银行", "price": 9.87},
        ]
        return jsonify(stocks)

    @app.route("/api/stock-name/<code>")
    def get_stock_name(code):
        """Get stock name by code"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify({"error": "Database connection not available"}), 500

            # Query MongoDB for stock name using the correct collection from config
            db_config = app.config["DB_CONFIG"]
            stock_collection_name = db_config["collections"]["stock_codes"]
            stock_record = app.config["MONGO_DB"][stock_collection_name].find_one(
                {"code": code}
            )
            if stock_record and "name" in stock_record:
                return jsonify({"code": code, "name": stock_record["name"]})
            else:
                return jsonify({"code": code, "name": ""}), 404
        except Exception as e:
            logger.error(f"Error fetching stock name for {code}: {e}")
            return jsonify({"error": f"Failed to fetch stock name: {str(e)}"}), 500

    @app.route("/api/stock-price/<code>")
    def get_stock_price(code):
        """Get real-time stock price by code"""
        try:
            # Check if this is a cryptocurrency (based on common crypto trading pairs)
            if code.upper().endswith(('USDT', 'BTC', 'ETH', 'BNB')):
                # For cryptocurrency, we would need to implement Binance API
                # For now, return a mock price or fallback
                # In a real implementation, you would call Binance API here
                import requests
                try:
                    # Try to get price from Binance API
                    url = f"https://api.binance.com/api/v3/ticker/price?symbol={code.upper()}"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        return jsonify({"code": code, "price": float(data['price'])})
                    else:
                        # Fallback to mock data if Binance API fails
                        return jsonify({"code": code, "price": 0.0})
                except Exception as binance_error:
                    logger.error(f"Error getting crypto price from Binance for {code}: {binance_error}")
                    # Fallback to mock data if Binance API fails
                    return jsonify({"code": code, "price": 0.0})
            else:
                # Get real-time data using akshare for stocks
                stock_data = ak.stock_bid_ask_em(symbol=code)
                
                # Extract the current price (based on your example, it's at index 20 in the 'value' column)
                current_price = stock_data.iloc[20]["value"]
                
                if current_price is not None:
                    return jsonify({"code": code, "price": float(current_price)})
                else:
                    return jsonify({"error": "Failed to get current price"}), 404
                    
        except Exception as e:
            logger.error(f"Error getting stock price for {code}: {e}")
            return jsonify({"error": f"Failed to get stock price: {str(e)}"}), 500


    @app.route("/api/backtest", methods=["POST"])
    def run_backtest():
        """Run backtest for a strategy"""
        data = request.get_json()

        # In a real implementation, this would run an actual backtest
        result = {
            "strategy": data.get("strategy", "Unknown"),
            "start_date": data.get("start_date", "2023-01-01"),
            "end_date": data.get("end_date", "2023-12-31"),
            "initial_capital": data.get("initial_capital", 100000),
            "final_value": 125000,
            "total_return": 25.0,
            "annualized_return": 25.0,
            "sharpe_ratio": 1.5,
        }

        return jsonify(result)

    @app.route("/api/trade", methods=["POST"])
    def execute_trade():
        """Execute a trade"""
        data = request.get_json()

        # In a real implementation, this would execute an actual trade
        result = {
            "status": "success",
            "order_id": "12345",
            "symbol": data.get("symbol", ""),
            "action": data.get("action", ""),
            "quantity": data.get("quantity", 0),
            "price": data.get("price", 0),
        }

        return jsonify(result)

    @app.route("/api/accounts", methods=["GET"])
    def get_accounts():
        """Get all accounts"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                # Return mock data if there's no database connection
                accounts = []
            else:
                # Fetch accounts from MongoDB
                accounts_cursor = app.config["MONGO_DB"].accounts.find()
                accounts = []
                for account in accounts_cursor:
                    # Convert ObjectId to string for JSON serialization
                    account["_id"] = str(account["_id"])
                    accounts.append(account)
            return jsonify(accounts)
        except Exception as e:
            logger.error(f"Error fetching accounts: {e}")
            # Return mock data if there's an error
            accounts = []
            return jsonify(accounts)

    @app.route("/api/accounts", methods=["POST"])
    def create_account():
        """Create a new account"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            data = request.get_json()

            # Save account to MongoDB
            result = app.config["MONGO_DB"].accounts.insert_one(data)

            # Add the inserted ID to the response
            data["_id"] = str(result.inserted_id)

            return jsonify(
                {
                    "status": "success",
                    "message": "Account created successfully",
                    "account": data,
                }
            )
        except Exception as e:
            logger.error(f"Error creating account: {e}")
            return jsonify(
                {"status": "error", "message": f"Failed to create account: {str(e)}"}
            ), 500

    @app.route("/api/accounts/<string:account_id>", methods=["PUT"])
    def update_account(account_id):
        """Update an existing account"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            data = request.get_json()

            # Update account in MongoDB
            result = app.config["MONGO_DB"].accounts.update_one(
                {"_id": ObjectId(account_id)}, {"$set": data}
            )

            if result.modified_count > 0:
                return jsonify(
                    {
                        "status": "success",
                        "message": f"Account {account_id} updated successfully",
                        "account": data,
                    }
                )
            else:
                return jsonify(
                    {
                        "status": "error",
                        "message": f"Account {account_id} not found or not updated",
                    }
                ), 404
        except Exception as e:
            logger.error(f"Error updating account {account_id}: {e}")
            return jsonify(
                {"status": "error", "message": f"Failed to update account: {str(e)}"}
            ), 500

    @app.route("/api/accounts/<string:account_id>", methods=["DELETE"])
    def delete_account(account_id):
        """Delete an account"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            # Delete account from MongoDB
            result = app.config["MONGO_DB"].accounts.delete_one(
                {"_id": ObjectId(account_id)}
            )

            if result.deleted_count > 0:
                return jsonify(
                    {
                        "status": "success",
                        "message": f"Account {account_id} deleted successfully",
                    }
                )
            else:
                return jsonify(
                    {"status": "error", "message": f"Account {account_id} not found"}
                ), 404
        except Exception as e:
            logger.error(f"Error deleting account {account_id}: {e}")
            return jsonify(
                {"status": "error", "message": f"Failed to delete account: {str(e)}"}
            ), 500

    @app.route("/api/agents", methods=["GET"])
    def get_agents():
        """Get all agents"""
        try:
            # Check if MongoDBManager is available
            if app.config["MONGO_MANAGER"] is None:
                logger.error("MongoDBManager not available")
                return jsonify([]), 200

            # Fetch agents using MongoDBManager
            agents = app.config["MONGO_MANAGER"].get_agents()
            return jsonify(agents), 200
        except Exception as e:
            logger.error(f"Error fetching agents: {e}")
            return jsonify([]), 200

    @app.route("/api/agents", methods=["POST"])
    def create_agent():
        """Create a new agent"""
        try:
            # Check if MongoDBManager is available
            if app.config["MONGO_MANAGER"] is None:
                logger.error("MongoDBManager not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            data = request.get_json()
            
            # Save agent using MongoDBManager
            agent_id = app.config["MONGO_MANAGER"].create_agent(data)
            
            if agent_id:
                # Add the inserted ID to the response
                data["_id"] = agent_id
                return jsonify(
                    {
                        "status": "success",
                        "message": "Agent created successfully",
                        "agent": data,
                    }
                )
            else:
                return jsonify(
                    {"status": "error", "message": "Failed to create agent"}
                ), 500
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return jsonify(
                {"status": "error", "message": f"Failed to create agent: {str(e)}"}
            ), 500

    @app.route("/api/agents/<string:agent_id>", methods=["PUT"])
    def update_agent(agent_id):
        """Update an existing agent"""
        try:
            # Check if MongoDBManager is available
            if app.config["MONGO_MANAGER"] is None:
                logger.error("MongoDBManager not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            data = request.get_json()

            # Update agent using MongoDBManager
            success = app.config["MONGO_MANAGER"].update_agent(agent_id, data)

            if success:
                return jsonify(
                    {
                        "status": "success",
                        "message": f"Agent {agent_id} updated successfully",
                        "agent": data,
                    }
                )
            else:
                return jsonify(
                    {
                        "status": "error",
                        "message": f"Agent {agent_id} not found or not updated",
                    }
                ), 404
        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {e}")
            return jsonify(
                {"status": "error", "message": f"Failed to update agent: {str(e)}"}
            ), 500

    @app.route("/api/agents/<string:agent_id>", methods=["DELETE"])
    def delete_agent(agent_id):
        """Delete an agent"""
        try:
            # Check if MongoDBManager is available
            if app.config["MONGO_MANAGER"] is None:
                logger.error("MongoDBManager not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            # Delete agent using MongoDBManager
            success = app.config["MONGO_MANAGER"].delete_agent(agent_id)

            if success:
                return jsonify(
                    {
                        "status": "success",
                        "message": f"Agent {agent_id} deleted successfully",
                    }
                )
            else:
                return jsonify(
                    {"status": "error", "message": f"Agent {agent_id} not found"}
                ), 404
        except Exception as e:
            logger.error(f"Error deleting agent {agent_id}: {e}")
            return jsonify(
                {"status": "error", "message": f"Failed to delete agent: {str(e)}"}
            ), 500

    @app.route("/api/strategies", methods=["GET"])
    def get_strategies():
        """Get all strategies"""
        try:
            # Check if MongoDBManager is available
            if app.config["MONGO_MANAGER"] is None:
                logger.error("MongoDBManager not available")
                return jsonify([]), 200

            # Fetch strategies using MongoDBManager
            strategies = app.config["MONGO_MANAGER"].get_strategies()
            return jsonify(strategies), 200
        except Exception as e:
            logger.error(f"Error fetching strategies: {e}")
            return jsonify([]), 200

    @app.route("/api/strategies", methods=["POST"])
    def create_strategy():
        """Create a new strategy"""
        try:
            # Check if MongoDBManager is available
            if app.config["MONGO_MANAGER"] is None:
                logger.error("MongoDBManager not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            data = request.get_json()

            # Handle field mapping: convert file/class_name to program for backward compatibility
            if "file" in data and "class_name" in data:
                data["program"] = {"file": data["file"], "class": data["class_name"]}

            # Save strategy using MongoDBManager
            strategy_id = app.config["MONGO_MANAGER"].create_strategy(data)

            if strategy_id:
                # Add the inserted ID to the response
                data["_id"] = strategy_id
                return jsonify(
                    {
                        "status": "success",
                        "message": "Strategy created successfully",
                        "strategy": data,
                    }
                )
            else:
                return jsonify(
                    {"status": "error", "message": "Failed to create strategy"}
                ), 500
        except Exception as e:
            logger.error(f"Error creating strategy: {e}")
            return jsonify(
                {"status": "error", "message": f"Failed to create strategy: {str(e)}"}
            ), 500

    @app.route("/api/strategies/<string:strategy_id>", methods=["PUT"])
    def update_strategy(strategy_id):
        """Update an existing strategy"""
        try:
            # Check if MongoDBManager is available
            if app.config["MONGO_MANAGER"] is None:
                logger.error("MongoDBManager not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            data = request.get_json()

            # Handle field mapping: convert file/class_name to program for backward compatibility
            if "file" in data and "class_name" in data:
                data["program"] = {"file": data["file"], "class": data["class_name"]}

            # Update strategy using MongoDBManager
            success = app.config["MONGO_MANAGER"].update_strategy(strategy_id, data)

            if success:
                return jsonify(
                    {
                        "status": "success",
                        "message": f"Strategy {strategy_id} updated successfully",
                        "strategy": data,
                    }
                )
            else:
                return jsonify(
                    {
                        "status": "error",
                        "message": f"Strategy {strategy_id} not found or not updated",
                    }
                ), 404
        except Exception as e:
            logger.error(f"Error updating strategy {strategy_id}: {e}")
            return jsonify(
                {"status": "error", "message": f"Failed to update strategy: {str(e)}"}
            ), 500

    @app.route("/api/strategies/<string:strategy_id>", methods=["DELETE"])
    def delete_strategy(strategy_id):
        """Delete a strategy"""
        try:
            # Check if MongoDBManager is available
            if app.config["MONGO_MANAGER"] is None:
                logger.error("MongoDBManager not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            # Delete strategy using MongoDBManager
            success = app.config["MONGO_MANAGER"].delete_strategy(strategy_id)

            if success:
                return jsonify(
                    {
                        "status": "success",
                        "message": f"Strategy {strategy_id} deleted successfully",
                    }
                )
            else:
                return jsonify(
                    {"status": "error", "message": f"Strategy {strategy_id} not found"}
                ), 404
        except Exception as e:
            logger.error(f"Error deleting strategy {strategy_id}: {e}")
            return jsonify(
                {"status": "error", "message": f"Failed to delete strategy: {str(e)}"}
            ), 500

    @app.route("/api/run-agent", methods=["POST"])
    def run_agent():
        """Run a specific agent"""
        logger.info("Entering run_agent function")
        data = None
        try:
            # Check if MongoDBManager is available
            if app.config["MONGO_MANAGER"] is None:
                logger.error("MongoDBManager not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            data = request.get_json()
            if not data:
                return jsonify(
                    {"status": "error", "message": "Invalid JSON data"}
                ), 400
                
            agent_id = data.get("agent_id")
            strategy_ids = data.get("strategy_ids", [])
            
            if not agent_id:
                return jsonify(
                    {"status": "error", "message": "Agent ID is required"}
                ), 400

            # Get agent details
            agent = app.config["MONGO_MANAGER"].get_agent(agent_id)
            if not agent:
                return jsonify(
                    {"status": "error", "message": f"Agent {agent_id} not found"}
                ), 404

            # Determine agent type based on agent name
            agent_name = agent.get("name", "")
            logger.info(f"Agent name: {agent_name}")
            is_weekly_selector = "趋势选股" in agent_name
            logger.info(f"Is weekly selector: {is_weekly_selector}")
            
            # Check if this is the weekly selector agent
            if is_weekly_selector:
                # Actually run the weekly selector agent with strategy parameters
                logger.info(f"Running weekly selector agent {agent['name']}")
                
                try:
                    # Initialize components
                    db_manager = app.config["MONGO_MANAGER"]
                    from utils.akshare_client import AkshareClient
                    data_fetcher = AkshareClient()
                    from agents.weekly_selector import WeeklyStockSelector
                    
                    # Get strategies associated with this agent
                    strategy_ids = agent.get('strategies', [])
                    logger.info(f"Agent has {len(strategy_ids)} strategies: {strategy_ids}")
                    
                    # Execute each strategy with its specific parameters and collect all selected stocks
                    all_selected_stocks = []
                    selectors = []  # Keep track of all selector instances
                    last_data_date = None  # Track the latest data date
                    all_golden_cross_flags = {}
                    all_selected_scores = {}
                    all_technical_analysis_data = {}

                    # If no strategies specified, use default parameters
                    if not strategy_ids:
                        logger.info("No strategies specified, using default parameters")
                        # Initialize selector with default parameters
                        selector = WeeklyStockSelector(db_manager, data_fetcher)
                        selectors.append(selector)

                        # Select stocks
                        selected_stocks, strategy_last_data_date, golden_cross_flags, selected_scores, technical_analysis_data = selector.select_stocks()
                        all_selected_stocks.extend(selected_stocks)
                        all_golden_cross_flags.update(golden_cross_flags)
                        all_selected_scores.update(selected_scores)
                        all_technical_analysis_data.update(technical_analysis_data)

                        # Update last_data_date
                        if strategy_last_data_date and (not last_data_date or strategy_last_data_date > last_data_date):
                            last_data_date = strategy_last_data_date
                    else:
                        # Execute each strategy with its specific parameters
                        for strategy_id in strategy_ids:
                            # Get strategy details
                            strategy = app.config["MONGO_MANAGER"].get_strategy(strategy_id)
                            if not strategy:
                                logger.warning(f"Strategy {strategy_id} not found")
                                continue

                            logger.info(f"Executing strategy {strategy['name']} with parameters: {strategy.get('parameters', {})}")

                            # Initialize selector
                            selector = WeeklyStockSelector(db_manager, data_fetcher)
                            selectors.append(selector)

                            # Select stocks using this strategy
                            selected_stocks, strategy_last_data_date, golden_cross_flags, selected_scores, technical_analysis_data = selector.select_stocks()
                            all_selected_stocks.extend(selected_stocks)
                            all_golden_cross_flags.update(golden_cross_flags)
                            all_selected_scores.update(selected_scores)
                            all_technical_analysis_data.update(technical_analysis_data)
                            logger.info(f"Strategy {strategy['name']} selected {len(selected_stocks)} stocks")

                            # Update last_data_date to the latest date among all strategies
                            if strategy_last_data_date and (not last_data_date or strategy_last_data_date > last_data_date):
                                last_data_date = strategy_last_data_date

                    # Remove duplicates while preserving order
                    selected_stocks = list(dict.fromkeys(all_selected_stocks))
                    logger.info(f"Total selected {len(selected_stocks)} stocks: {selected_stocks}")

                    # Save selection to pool collection using the first selector instance or create a default one if needed
                    if selectors:
                        selector_to_use = selectors[0]  # Use the first selector instance
                    else:
                        selector_to_use = WeeklyStockSelector(db_manager, data_fetcher)

                    if selected_stocks is not None:
                        success = selector_to_use.save_selected_stocks(
                            stocks=selected_stocks,
                            golden_cross_flags=all_golden_cross_flags,
                            date=datetime.now().strftime('%Y-%m-%d'),
                            last_data_date=last_data_date,
                            scores=all_selected_scores,
                            technical_analysis_data=all_technical_analysis_data
                        )
                        if success:
                            logger.info("Successfully saved selected stocks to pool collection")
                        else:
                            logger.error("Failed to save selected stocks to pool collection")
                    else:
                        logger.warning("No stocks selected")
                        # Still save an empty selection to pool collection
                        success = selector_to_use.save_selected_stocks(
                            stocks=[],
                            golden_cross_flags={},
                            date=datetime.now().strftime('%Y-%m-%d'),
                            last_data_date=last_data_date,
                            scores={},
                            technical_analysis_data={}
                        )
                        if success:
                            logger.info("Successfully saved empty selection to pool collection")
                        else:
                            logger.error("Failed to save empty selection to pool collection")
                    
                    return jsonify(
                        {
                            "status": "success",
                            "message": f"Agent {agent['name']} completed successfully",
                            "agent_id": agent_id,
                            "result": {
                                "selected_stocks": selected_stocks,
                                "count": len(selected_stocks)
                            }
                        }
                    )
                except Exception as selector_error:
                    logger.error(f"Error running weekly selector agent: {selector_error}")
                    return jsonify(
                        {"status": "error", "message": f"Failed to run weekly selector agent: {str(selector_error)}"}
                    ), 500
            elif "技术分析" in agent_name:
                # Handle technical analysis agents
                logger.info(f"Running technical analysis agent {agent['name']} with strategies {strategy_ids}")

                try:
                    # Initialize components
                    db_manager = app.config["MONGO_MANAGER"]
                    from utils.akshare_client import AkshareClient
                    data_fetcher = AkshareClient()

                    # Initialize the technical stock selector
                    from agents.technical_selector import TechnicalStockSelector
                    selector = TechnicalStockSelector(db_manager, data_fetcher)

                    # Execute technical analysis and update pool
                    success = selector.update_pool_with_technical_analysis()

                    if success:
                        logger.info("Successfully executed technical analysis agent")
                        return jsonify(
                            {
                                "status": "success",
                                "message": f"Agent {agent['name']} completed successfully",
                                "agent_id": agent_id,
                                "result": {
                                    "analysis_complete": True,
                                    "stocks_updated": True
                                }
                            }
                        )
                    else:
                        logger.error("Failed to execute technical analysis agent")
                        return jsonify(
                            {
                                "status": "error",
                                "message": f"Failed to run technical analysis agent: Execution failed",
                                "agent_id": agent_id
                            }
                        ), 500

                except Exception as selector_error:
                    logger.error(f"Error running technical analysis agent: {selector_error}")
                    return jsonify(
                        {
                            "status": "error",
                            "message": f"Failed to run technical analysis agent: {str(selector_error)}",
                            "agent_id": agent_id
                        }
                    ), 500
            else:
                # For other agents, simulate a successful run
                logger.info(f"Running agent {agent['name']} with strategies {strategy_ids}")

                # Simulate some processing time
                import time
                time.sleep(2)

                return jsonify(
                    {
                        "status": "success",
                        "message": f"Agent {agent['name']} completed successfully",
                        "agent_id": agent_id,
                        "result": {
                            "profit": 1500.50,
                            "trades": 5,
                            "win_rate": 0.6
                        }
                    }
                )
        except Exception as e:
            # Handle case where agent_id might not be defined
            agent_id = data.get("agent_id") if 'data' in locals() and data else "unknown"
            if agent_id and agent_id != "unknown":
                logger.error(f"Error running agent {agent_id}: {e}")
                message = f"Failed to run agent {agent_id}: {str(e)}"
            else:
                logger.error(f"Error running agent: {e}")
                message = f"Failed to run agent: {str(e)}"
            return jsonify(
                {"status": "error", "message": message}
            ), 500

    @app.route("/api/config", methods=["GET"])
    def get_config():
        """Get system configuration"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify({}), 200

            # Fetch config from MongoDB
            config_record = app.config["MONGO_DB"].config.find_one()
            
            if config_record:
                # Remove the MongoDB _id field
                config_record.pop("_id", None)
                return jsonify(config_record), 200
            else:
                # Return default config if none exists
                return jsonify({}), 200
        except Exception as e:
            logger.error(f"Error fetching config: {e}")
            return jsonify({}), 200

    @app.route("/api/config", methods=["POST"])
    def save_config():
        """Save system configuration"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            data = request.get_json()
            
            # Update or insert config in MongoDB
            result = app.config["MONGO_DB"].config.update_one(
                {}, {"$set": data}, upsert=True
            )
            
            return jsonify(
                {
                    "status": "success",
                    "message": "Configuration saved successfully",
                }
            )
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return jsonify(
                {"status": "error", "message": f"Failed to save configuration: {str(e)}"}
            ), 500


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create and run app
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
