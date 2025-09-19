"""
Web interface for the quant trading system.
Provides REST API and web UI for system monitoring and control.
"""

import os
import sys
from datetime import datetime
from bson import ObjectId

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import logging
from typing import Dict, Any, Optional, List
import yaml
from bson.objectid import ObjectId
import akshare as ak
from datetime import datetime

# Import additional modules for agent execution
from utils.akshare_client import AkshareClient
from agents.fundamental_selector import FundamentalStockSelector
from agents.technical_selector import TechnicalStockSelector
from agents.weekly_selector import WeeklyStockSelector

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

    @app.route("/positions")
    def positions():
        """Positions page"""
        return render_template("positions.html")

    @app.route("/stock-kline")
    def stock_kline_page():
        """Stock K-line chart page"""
        code = request.args.get('code', '')
        name = request.args.get('name', code)
        # Debug logging
        app.logger.info(f"Rendering stock_kline_v2.html with code={code}, name={name}")
        try:
            return render_template("stock_kline_v2.html", code=code, name=name)
        except Exception as e:
            app.logger.error(f"Error rendering stock_kline_v2.html: {str(e)}")
            # Fallback to old template
            return render_template("stock_kline.html", code=code, name=name)

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
        """Get stock name by code from code collection"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify({"error": "Database connection not available"}), 500

            # Find stock by code in the code collection
            stock_record = app.config["MONGO_DB"].code.find_one({"code": code})

            if stock_record and "name" in stock_record:
                return jsonify({"code": code, "name": stock_record["name"]}), 200
            else:
                return jsonify({"code": code, "name": ""}), 200

        except Exception as e:
            logger.error(f"Error getting stock name for {code}: {e}")
            return jsonify({"error": f"Failed to get stock name: {str(e)}"}), 500

    @app.route("/api/stock-price/<code>")
    def get_stock_price(code):
        """Get real-time stock price by code"""
        try:
            # Check if this is a cryptocurrency (based on common crypto trading pairs)
            if code.upper().endswith(("USDT", "BTC", "ETH", "BNB")):
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
                        return jsonify({"code": code, "price": float(data["price"])})
                    else:
                        # Fallback to mock data if Binance API fails
                        return jsonify({"code": code, "price": 0.0})
                except Exception as binance_error:
                    logger.error(
                        f"Error getting crypto price from Binance for {code}: {binance_error}"
                    )
                    # Fallback to mock data if Binance API fails
                    return jsonify({"code": code, "price": 0.0})
            else:
                # Get latest closing price using AkshareClient for stocks
                try:
                    # Initialize AkshareClient
                    akshare_client = AkshareClient()

                    # Get recent daily K-line data (last 5 days to ensure we get data)
                    from datetime import datetime, timedelta
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')

                    k_data = akshare_client.get_daily_k_data(code, start_date, end_date)

                    if not k_data.empty and len(k_data) > 0:
                        # Get the latest closing price
                        latest_close = k_data.iloc[-1]['close']

                        if latest_close is not None:
                            return jsonify({"code": code, "price": float(latest_close)})
                        else:
                            return jsonify({"error": "Failed to get closing price"}), 404
                    else:
                        return jsonify({"error": "No K-line data found for stock"}), 404

                except Exception as akshare_error:
                    logger.error(
                        f"Error getting stock price from Akshare for {code}: {akshare_error}"
                    )
                    # Fallback to real-time data if K-line data fails
                    try:
                        # Initialize AkshareClient
                        akshare_client = AkshareClient()

                        # Get real-time data for the stock
                        realtime_data = akshare_client.get_realtime_data([code])

                        if not realtime_data.empty and len(realtime_data) > 0:
                            # Extract the current price (latest price)
                            current_price = realtime_data.iloc[0]['price']

                            if current_price is not None:
                                return jsonify({"code": code, "price": float(current_price)})
                            else:
                                return jsonify({"error": "Failed to get current price"}), 404
                        else:
                            return jsonify({"error": "No data found for stock"}), 404
                    except Exception as fallback_error:
                        logger.error(
                            f"Fallback method also failed for {code}: {fallback_error}"
                        )
                        # Last fallback to old method
                        try:
                            stock_data = ak.stock_bid_ask_em(symbol=code)
                            current_price = stock_data.iloc[20]["value"]

                            if current_price is not None:
                                return jsonify({"code": code, "price": float(current_price)})
                            else:
                                return jsonify({"error": "Failed to get current price"}), 404
                        except Exception as last_fallback_error:
                            logger.error(
                                f"Last fallback method also failed for {code}: {last_fallback_error}"
                            )
                            return jsonify({"error": f"Failed to get stock price: {str(last_fallback_error)}"}), 500

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
                return jsonify({"status": "error", "message": "Invalid JSON data"}), 400

            agent_id = data.get("agent_id")

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
                    strategy_ids = agent.get("strategies", [])
                    logger.info(
                        f"Agent has {len(strategy_ids)} strategies: {strategy_ids}"
                    )

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
                        (
                            selected_stocks,
                            strategy_last_data_date,
                            golden_cross_flags,
                            selected_scores,
                            technical_analysis_data,
                        ) = selector.select_stocks()
                        all_selected_stocks.extend(selected_stocks)
                        all_golden_cross_flags.update(golden_cross_flags)
                        all_selected_scores.update(selected_scores)
                        all_technical_analysis_data.update(technical_analysis_data)

                        # Update last_data_date
                        if strategy_last_data_date and (
                            not last_data_date
                            or strategy_last_data_date > last_data_date
                        ):
                            last_data_date = strategy_last_data_date
                    else:
                        # Execute each strategy with its specific parameters
                        for strategy_id in strategy_ids:
                            # Get strategy details
                            strategy = app.config["MONGO_MANAGER"].get_strategy(
                                strategy_id
                            )
                            if not strategy:
                                logger.warning(f"Strategy {strategy_id} not found")
                                continue

                            logger.info(
                                f"Executing strategy {strategy['name']} with parameters: {strategy.get('parameters', {})}"
                            )

                            # Initialize selector with specific strategy ID
                            selector = WeeklyStockSelector(
                                db_manager, data_fetcher, strategy_id
                            )
                            selectors.append(selector)

                            # Select stocks using this strategy
                            (
                                selected_stocks,
                                strategy_last_data_date,
                                golden_cross_flags,
                                selected_scores,
                                technical_analysis_data,
                            ) = selector.select_stocks()
                            all_selected_stocks.extend(selected_stocks)
                            all_golden_cross_flags.update(golden_cross_flags)
                            all_selected_scores.update(selected_scores)
                            all_technical_analysis_data.update(technical_analysis_data)
                            logger.info(
                                f"Strategy {strategy['name']} selected {len(selected_stocks)} stocks"
                            )

                            # Update last_data_date to the latest date among all strategies
                            if strategy_last_data_date and (
                                not last_data_date
                                or strategy_last_data_date > last_data_date
                            ):
                                last_data_date = strategy_last_data_date

                    # Remove duplicates while preserving order
                    selected_stocks = list(dict.fromkeys(all_selected_stocks))
                    logger.info(
                        f"Total selected {len(selected_stocks)} stocks: {selected_stocks}"
                    )

                    # Save selection to pool collection using the first selector instance or create a default one if needed
                    if selectors:
                        selector_to_use = selectors[
                            0
                        ]  # Use the first selector instance
                    else:
                        selector_to_use = WeeklyStockSelector(db_manager, data_fetcher)

                    if selected_stocks is not None:
                        success = selector_to_use.save_selected_stocks(
                            stocks=selected_stocks,
                            golden_cross_flags=all_golden_cross_flags,
                            date=datetime.now().strftime("%Y-%m-%d"),
                            last_data_date=last_data_date,
                            scores=all_selected_scores,
                            technical_analysis_data=all_technical_analysis_data,
                        )
                        if success:
                            logger.info(
                                "Successfully saved selected stocks to pool collection"
                            )
                        else:
                            logger.error(
                                "Failed to save selected stocks to pool collection"
                            )
                    else:
                        logger.warning("No stocks selected")
                        # Still save an empty selection to pool collection
                        success = selector_to_use.save_selected_stocks(
                            stocks=[],
                            golden_cross_flags={},
                            date=datetime.now().strftime("%Y-%m-%d"),
                            last_data_date=last_data_date,
                            scores={},
                            technical_analysis_data={},
                        )
                        if success:
                            logger.info(
                                "Successfully saved empty selection to pool collection"
                            )
                        else:
                            logger.error(
                                "Failed to save empty selection to pool collection"
                            )

                    return jsonify(
                        {
                            "status": "success",
                            "message": f"Agent {agent['name']} completed successfully",
                            "agent_id": agent_id,
                            "result": {
                                "selected_stocks": selected_stocks,
                                "count": len(selected_stocks),
                            },
                        }
                    )
                except Exception as selector_error:
                    logger.error(
                        f"Error running weekly selector agent: {selector_error}"
                    )
                    return jsonify(
                        {
                            "status": "error",
                            "message": f"Failed to run weekly selector agent: {str(selector_error)}",
                        }
                    ), 500
            elif "技术分析" in agent_name:
                # Handle technical analysis agents
                strategy_ids = agent.get("strategies", [])
                logger.info(
                    f"Running technical analysis agent {agent['name']} with strategies {strategy_ids}"
                )

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
                                    "stocks_updated": True,
                                },
                            }
                        )
                    else:
                        logger.error("Failed to execute technical analysis agent")
                        return jsonify(
                            {
                                "status": "error",
                                "message": f"Failed to run technical analysis agent: Execution failed",
                                "agent_id": agent_id,
                            }
                        ), 500

                except Exception as selector_error:
                    logger.error(
                        f"Error running technical analysis agent: {selector_error}"
                    )
                    return jsonify(
                        {
                            "status": "error",
                            "message": f"Failed to run technical analysis agent: {str(selector_error)}",
                            "agent_id": agent_id,
                        }
                    ), 500
            elif "基本面分析" in agent_name:
                # Handle fundamental analysis agents
                strategy_ids = agent.get("strategies", [])
                logger.info(
                    "Running fundamental analysis agent %s with strategies %s",
                    agent["name"],
                    strategy_ids,
                )

                try:
                    # Initialize components
                    db_manager = app.config["MONGO_MANAGER"]
                    from utils.akshare_client import AkshareClient

                    data_fetcher = AkshareClient()

                    # Initialize the fundamental stock selector
                    selector = FundamentalStockSelector(db_manager, data_fetcher)

                    # Execute fundamental analysis and update pool
                    success = selector.update_pool_with_fundamental_analysis()

                    if success:
                        logger.info("Successfully executed fundamental analysis agent")
                        return jsonify(
                            {
                                "status": "success",
                                "message": f"Agent {agent['name']} completed successfully",
                                "agent_id": agent_id,
                                "result": {
                                    "analysis_complete": True,
                                    "stocks_updated": True,
                                },
                            }
                        )
                    else:
                        logger.error("Failed to execute fundamental analysis agent")
                        return jsonify(
                            {
                                "status": "error",
                                "message": "Failed to run fundamental analysis agent: Execution failed",
                                "agent_id": agent_id,
                            }
                        ), 500

                except Exception as selector_error:
                    logger.error(
                        "Error running fundamental analysis agent: %s", selector_error
                    )
                    return jsonify(
                        {
                            "status": "error",
                            "message": f"Failed to run fundamental analysis agent: {str(selector_error)}",
                            "agent_id": agent_id,
                        }
                    ), 500
            elif "舆情分析" in agent_name:
                # Handle public opinion analysis agents
                strategy_ids = agent.get("strategies", [])
                logger.info(
                    f"Running public opinion analysis agent {agent['name']} with strategies {strategy_ids}"
                )

                try:
                    # Initialize components
                    db_manager = app.config["MONGO_MANAGER"]
                    from utils.akshare_client import AkshareClient

                    data_fetcher = AkshareClient()

                    # Initialize the public opinion stock selector
                    from agents.public_opinion_selector import (
                        PublicOpinionStockSelector,
                    )

                    selector = PublicOpinionStockSelector(db_manager, data_fetcher)

                    # Execute public opinion analysis and update pool
                    success = selector.update_pool_with_public_opinion_analysis()

                    if success:
                        logger.info(
                            "Successfully executed public opinion analysis agent"
                        )
                        return jsonify(
                            {
                                "status": "success",
                                "message": f"Agent {agent['name']} completed successfully",
                                "agent_id": agent_id,
                                "result": {
                                    "analysis_complete": True,
                                    "stocks_updated": True,
                                },
                            }
                        )
                    else:
                        logger.error("Failed to execute public opinion analysis agent")
                        return jsonify(
                            {
                                "status": "error",
                                "message": "Failed to run public opinion analysis agent: Execution failed",
                                "agent_id": agent_id,
                            }
                        ), 500

                except Exception as selector_error:
                    logger.error(
                        f"Error running public opinion analysis agent: {selector_error}"
                    )
                    return jsonify(
                        {
                            "status": "error",
                            "message": f"Failed to run public opinion analysis agent: {str(selector_error)}",
                            "agent_id": agent_id,
                        }
                    ), 500
            elif "信号生成" in agent_name:
                # Handle signal generator agents
                strategy_ids = agent.get("strategies", [])
                logger.info(
                    f"Running signal generator agent {agent['name']} with strategies {strategy_ids}"
                )

                try:
                    # Initialize components
                    db_manager = app.config["MONGO_MANAGER"]
                    from utils.akshare_client import AkshareClient

                    data_fetcher = AkshareClient()

                    # Initialize the signal generator
                    from agents.signal_generator import SignalGenerator

                    signal_generator = SignalGenerator(db_manager, data_fetcher)

                    # Execute signal generation
                    success = signal_generator.run()

                    if success:
                        logger.info("Successfully executed signal generator agent")
                        return jsonify(
                            {
                                "status": "success",
                                "message": f"Agent {agent['name']} completed successfully",
                                "agent_id": agent_id,
                                "result": {
                                    "generation_complete": True,
                                    "signals_updated": True,
                                },
                            }
                        )
                    else:
                        logger.error("Failed to execute signal generator agent")
                        return jsonify(
                            {
                                "status": "error",
                                "message": "Failed to run signal generator agent: Execution failed",
                                "agent_id": agent_id,
                            }
                        ), 500

                except Exception as generator_error:
                    logger.error(
                        f"Error running signal generator agent: {generator_error}"
                    )
                    return jsonify(
                        {
                            "status": "error",
                            "message": f"Failed to run signal generator agent: {str(generator_error)}",
                            "agent_id": agent_id,
                        }
                    ), 500
        except Exception as e:
            # Handle case where agent_id might not be defined
            agent_id = (
                data.get("agent_id") if "data" in locals() and data else "unknown"
            )
            if agent_id and agent_id != "unknown":
                logger.error(f"Error running agent {agent_id}: {e}")
                message = f"Failed to run agent {agent_id}: {str(e)}"
            else:
                logger.error(f"Error running agent: {e}")
                message = f"Failed to run agent: {str(e)}"
            return jsonify({"status": "error", "message": message}), 500

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
                {
                    "status": "error",
                    "message": f"Failed to save configuration: {str(e)}",
                }
            ), 500

    @app.route("/api/llm-config", methods=["POST"])
    def save_llm_config():
        """Save LLM configuration"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            data = request.get_json()

            # Update or insert LLM config in MongoDB
            # We'll store LLM config as a sub-document in the config collection
            result = app.config["MONGO_DB"].config.update_one(
                {}, {"$set": {"llm": data}}, upsert=True
            )

            return jsonify(
                {
                    "status": "success",
                    "message": "LLM configuration saved successfully",
                }
            )
        except Exception as e:
            logger.error(f"Error saving LLM config: {e}")
            return jsonify(
                {
                    "status": "error",
                    "message": f"Failed to save LLM configuration: {str(e)}",
                }
            ), 500

    @app.route("/api/llm-config", methods=["GET"])
    def get_llm_config():
        """Get LLM configuration"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify({}), 200

            # Fetch config from MongoDB
            config_record = app.config["MONGO_DB"].config.find_one()

            if config_record and "llm" in config_record:
                return jsonify(config_record["llm"]), 200
            else:
                # Return default LLM config if none exists
                return jsonify({}), 200
        except Exception as e:
            logger.error(f"Error fetching LLM config: {e}")
            return jsonify({}), 200

    @app.route("/api/llm-configs", methods=["GET"])
    def list_llm_configs():
        """List all LLM configurations"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify([]), 200

            # Fetch config from MongoDB
            config_record = app.config["MONGO_DB"].config.find_one()

            if config_record and "llm_configs" in config_record:
                return jsonify(config_record["llm_configs"]), 200
            else:
                # Return empty array if no LLM configs exist
                return jsonify([]), 200
        except Exception as e:
            logger.error(f"Error fetching LLM configs: {e}")
            return jsonify([]), 200

    @app.route("/api/llm-configs", methods=["POST"])
    def save_llm_configs():
        """Save all LLM configurations"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            data = request.get_json()

            # Update or insert LLM configs in MongoDB
            result = app.config["MONGO_DB"].config.update_one(
                {}, {"$set": {"llm_configs": data}}, upsert=True
            )

            return jsonify(
                {
                    "status": "success",
                    "message": "LLM configurations saved successfully",
                }
            )
        except Exception as e:
            logger.error(f"Error saving LLM configs: {e}")
            return jsonify(
                {
                    "status": "error",
                    "message": f"Failed to save LLM configurations: {str(e)}",
                }
            ), 500

    @app.route("/api/latest-pool-stocks")
    def get_latest_pool_stocks():
        """Get the latest pool record with stock information"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify([]), 200

            # Get pool collection
            pool_collection = app.config["MONGO_DB"]["pool"]

            # Find the latest record sorted by _id (which contains the date)
            latest_record = pool_collection.find_one(sort=[("_id", -1)])

            if not latest_record:
                logger.warning("No records found in pool collection")
                return jsonify([]), 200

            # Extract stocks information
            stocks = latest_record.get("stocks", [])

            # Get stock codes for fetching data
            stock_codes = [stock.get("code") for stock in stocks if stock.get("code")]

            # Get stock names from code collection
            stock_names = {}
            if stock_codes:
                try:
                    # Get database configuration
                    db_config = app.config["MONGO_MANAGER"].config_loader.get_collections_config()
                    code_collection_name = db_config.get("stock_codes", "code")
                    code_collection = app.config["MONGO_DB"][code_collection_name]

                    # Get stock names for all codes
                    code_records = code_collection.find({"code": {"$in": stock_codes}})
                    for record in code_records:
                        code = record.get("code")
                        name = record.get("name", "")
                        if code:
                            stock_names[code] = name
                except Exception as e:
                    logger.error(f"Error getting stock names from code collection: {e}")

            # Get latest data from buf_data collection
            buf_data = {}
            if stock_codes:
                try:
                    buf_data_collection = app.config["MONGO_DB"]["buf_data"]

                    # For each stock, get the latest record from buf_data
                    for code in stock_codes:
                        latest_buf_record = buf_data_collection.find_one(
                            {"code": code},
                            sort=[("date", -1)]  # Sort by date descending to get latest
                        )
                        if latest_buf_record:
                            buf_data[code] = {
                                "price": float(latest_buf_record.get("close", 0.0)),
                                "change_percent": float(latest_buf_record.get("pct_change", 0.0)),
                                "turnover_rate": float(latest_buf_record.get("turnover_rate", 0.0)),
                            }
                except Exception as e:
                    logger.error(f"Error getting data from buf_data collection: {e}")

            # Combine pool data with stock names and buf_data
            result_stocks = []
            for stock in stocks:
                code = stock.get("code", "")
                stock_info = {
                    "code": code,
                    "name": stock_names.get(code, ""),
                    "price": buf_data.get(code, {}).get("price", 0.0),
                    "change_percent": buf_data.get(code, {}).get("change_percent", 0.0),
                    "turnover_rate": buf_data.get(code, {}).get("turnover_rate", 0.0),
                    "signal": stock.get("signals", {}),
                    "trend": {
                        "score": stock.get("trend", {}).get("score", 0.0)
                        if stock.get("trend")
                        else 0.0,
                        "value": stock.get("trend", {}).get("value", "")
                        if stock.get("trend")
                        else "",
                    },
                    "tech": stock.get("tech", {}),
                    "fund": stock.get("fund", {}),
                    "pub": stock.get("pub", {}),
                }
                result_stocks.append(stock_info)

            return jsonify(result_stocks), 200

        except Exception as e:
            logger.error(f"Error getting latest pool stocks: {e}")
            return jsonify([]), 200

    @app.route("/api/stock-kline/<code>")
    def get_stock_kline_data(code):
        """Get K-line data for a specific stock from buf_data collection"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify({"error": "Database connection not available"}), 500

            # Get buf_data collection
            buf_data_collection = app.config["MONGO_DB"]["buf_data"]

            # Get all data for the stock, sorted by date ascending
            kline_records = list(buf_data_collection.find(
                {"code": code}
            ).sort("date", 1))

            if not kline_records:
                logger.warning(f"No K-line data found for stock {code}")
                return jsonify({"error": "No K-line data found"}), 404

            # Process the data for charting
            kline_data = []
            for record in kline_records:
                kline_data.append({
                    "date": record.get("date"),
                    "open": float(record.get("open", 0.0)),
                    "high": float(record.get("high", 0.0)),
                    "low": float(record.get("low", 0.0)),
                    "close": float(record.get("close", 0.0)),
                    "volume": float(record.get("volume", 0.0)),
                    "amount": float(record.get("amount", 0.0)) if "amount" in record else 0.0,
                    "turnover_rate": float(record.get("turnover_rate", 0.0)) if "turnover_rate" in record else 0.0,
                })

            return jsonify(kline_data), 200

        except Exception as e:
            logger.error(f"Error getting K-line data for stock {code}: {e}")
            return jsonify({"error": f"Failed to get K-line data: {str(e)}"}), 500

    @app.route("/api/strategy-by-name/<string:strategy_name>", methods=["GET"])
    def get_strategy_by_name(strategy_name):
        """Get a specific strategy by name"""
        try:
            # Check if MongoDBManager is available
            if app.config["MONGO_MANAGER"] is None:
                logger.error("MongoDBManager not available")
                return jsonify({"error": "Database connection not available"}), 500

            # Get strategy using MongoDBManager
            strategy = app.config["MONGO_MANAGER"].get_strategy_by_name(strategy_name)

            if strategy:
                return jsonify(strategy), 200
            else:
                return jsonify({"error": f"Strategy {strategy_name} not found"}), 404
        except Exception as e:
            logger.error(f"Error getting strategy {strategy_name}: {e}")
            return jsonify({"error": f"Failed to get strategy: {str(e)}"}), 500

    @app.route("/api/pool-data/<code>")
    def get_pool_data_by_code(code):
        """Get pool data for a specific stock code"""
        try:
            # Get MongoDB manager instance from app config
            db_manager = app.config["MONGO_MANAGER"]

            # Access the pool collection
            pool_collection = db_manager.get_collection('pool')

            # Find the latest pool record (sorted by _id descending)
            latest_record = pool_collection.find_one(
                sort=[("_id", -1)]  # Sort by _id descending to get the latest
            )

            if not latest_record:
                return jsonify({"error": "No pool data found"}), 404

            # Extract stocks from the latest record
            stocks = latest_record.get("stocks", [])

            # Find the specific stock by code
            target_stock = None
            for stock in stocks:
                if stock.get("code") == code:
                    target_stock = stock
                    break

            if not target_stock:
                return jsonify({"error": f"No data found for stock code {code}"}), 404

            # Add the stock code and name to the response
            target_stock["code"] = code

            # Try to get stock name from code collection
            try:
                code_collection = db_manager.get_collection('code')
                code_record = code_collection.find_one({"code": code})
                if code_record and "name" in code_record:
                    target_stock["name"] = code_record["name"]
            except Exception as name_error:
                logger.warning(f"Could not fetch stock name for {code}: {name_error}")

            return jsonify(target_stock), 200

        except Exception as e:
            logger.error(f"Error getting pool data for stock {code}: {e}")
            return jsonify({"error": f"Failed to get pool data: {str(e)}"}), 500


    @app.route("/api/orders", methods=["GET"])
    def get_orders():
        """Get all orders"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify([]), 500

            # Fetch orders from MongoDB
            orders_cursor = app.config["MONGO_DB"].orders.find().sort("date", -1)
            orders = []
            for order in orders_cursor:
                # Convert ObjectId to string for JSON serialization
                order["_id"] = str(order["_id"])
                orders.append(order)
            return jsonify(orders)
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return jsonify([]), 500
    
    @app.route("/api/orders", methods=["POST"])
    def create_order():
        """Create a new order"""
        try:
            # Check if MongoDB connection is available
            if app.config["MONGO_DB"] is None:
                logger.error("MongoDB connection not available")
                return jsonify(
                    {"status": "error", "message": "Database connection not available"}
                ), 500

            data = request.get_json()

            # Validate required fields
            required_fields = ["date", "account_id", "code", "name", "price", "quantity"]
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify(
                        {"status": "error", "message": f"Missing required field: {field}"}
                    ), 400

            # Determine action based on quantity (positive = buy, negative = sell)
            quantity = int(data["quantity"])
            action = "buy" if quantity > 0 else "sell" if quantity < 0 else "unknown"

            # Prepare order document
            order = {
                "date": data["date"],
                "account_id": data["account_id"],
                "account_name": data.get("account_name", ""),  # Add account_name field
                "code": data["code"],
                "name": data["name"],
                "price": float(data["price"]),
                "quantity": quantity,
                "action": action,  # Add action field
                "created_at": datetime.now()
            }

            # Add commission if provided
            if "commission" in data:
                order["commission"] = float(data["commission"])

            # Calculate total_amount based on action and commission
            base_amount = float(data["price"]) * abs(quantity)
            if "commission" in data:
                commission = float(data["commission"])
                if action == "buy":
                    # For buying, total_amount includes commission
                    order["total_amount"] = base_amount + commission
                else:
                    # For selling, total_amount is the base amount
                    order["total_amount"] = base_amount
            else:
                # If no commission, total_amount is base amount
                order["total_amount"] = base_amount

            # Add net_amount if provided or calculate it
            if "net_amount" in data:
                order["net_amount"] = float(data["net_amount"])
            elif "commission" in data:
                commission = float(data["commission"])
                if action == "buy":
                    # For buying, net amount is the base amount (what you get for the stocks)
                    order["net_amount"] = base_amount
                else:
                    # For selling, net amount is base amount minus commission
                    order["net_amount"] = base_amount - commission

            # Save order to MongoDB
            result = app.config["MONGO_DB"].orders.insert_one(order)

            # Update account cash and stock holdings
            update_account_holdings(data["account_id"], data["code"], data["name"],
                                  float(data["price"]), quantity, order.get("commission", 0))

            if result.inserted_id:
                # Add the inserted ID to the response
                order["_id"] = str(result.inserted_id)
                return jsonify(
                    {
                        "status": "success",
                        "message": "Order created successfully",
                        "order": order,
                    }
                )
            else:
                return jsonify(
                    {"status": "error", "message": "Failed to create order"}
                ), 500
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return jsonify(
                {"status": "error", "message": f"Failed to create order: {str(e)}"}
            ), 500

    def update_account_holdings(account_id, stock_code, stock_name, price, quantity, commission=0):
        """Update account cash and stock holdings after an order"""
        try:
            # Get account information
            account = app.config["MONGO_DB"].accounts.find_one({"_id": ObjectId(account_id)})
            if not account:
                logger.error(f"Account {account_id} not found")
                return False

            # Calculate order value (positive for selling, negative for buying)
            order_value = price * quantity  # For selling, quantity is negative, so order_value is positive

            # Update cash
            # For buying: subtract (order_value + commission)
            # For selling: add (order_value - commission)
            cash_change = -order_value  # Base change (negative for buying, positive for selling)
            if commission > 0:
                cash_change -= commission  # Deduct commission for both buying and selling

            new_cash = account.get("cash", 0) + cash_change

            # Update stock holdings
            stocks = account.get("stocks", [])
            stock_found = False

            if quantity < 0:  # Selling stocks
                # Find the stock in holdings and reduce quantity
                for stock in stocks:
                    if stock["code"] == stock_code:
                        stock_found = True
                        new_quantity = stock["quantity"] + quantity  # quantity is negative
                        if new_quantity <= 0:
                            # Remove stock if quantity is zero or negative
                            stocks.remove(stock)
                        else:
                            # Update quantity
                            stock["quantity"] = new_quantity
                        break
            else:  # Buying stocks
                # Find the stock in holdings and increase quantity or add new stock
                for stock in stocks:
                    if stock["code"] == stock_code:
                        stock_found = True
                        # Update quantity and cost (weighted average)
                        total_quantity = stock["quantity"] + quantity
                        total_value = (stock["quantity"] * stock["cost"]) + (quantity * price)
                        stock["quantity"] = total_quantity
                        stock["cost"] = total_value / total_quantity if total_quantity > 0 else 0
                        break

                # If stock not found, add it to holdings
                if not stock_found:
                    stocks.append({
                        "code": stock_code,
                        "name": stock_name,
                        "quantity": quantity,
                        "cost": price
                    })

            # Update account in database
            update_data = {
                "cash": new_cash,
                "stocks": stocks
            }

            result = app.config["MONGO_DB"].accounts.update_one(
                {"_id": ObjectId(account_id)},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"Successfully updated account {account_id} holdings")
                return True
            else:
                logger.warning(f"No changes made to account {account_id} holdings")
                return False

        except Exception as e:
            logger.error(f"Error updating account holdings: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create and run app
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
