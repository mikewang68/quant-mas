import unittest
from agents.public_opinion_selector import PublicOpinionStockSelector
from data.akshare_client import AkshareClient
from data.mongodb_manager import MongoDBManager
import logging


class TestPublicOpinionAnalysis300339(unittest.TestCase):

    def setUp(self):
        # Initialize database connection
        self.db_manager = MongoDBManager()
        self.akshare_client = AkshareClient()
        self.stock_code = '300339'
        self.logger = logging.getLogger(__name__)
        self.public_opinion_selector = PublicOpinionStockSelector(
            db_manager=self.db_manager,
            data_fetcher=self.akshare_client,
            name="TestPublicOpinionStockSelector"
        )

    def test_public_opinion_analysis_300339(self):
        # Load all configured strategies and logic
        self.public_opinion_selector._load_strategies_from_db()
        self.public_opinion_selector._load_dynamic_strategies()

        # Execute public opinion analysis for the specified stock
        # result = self.public_opinion_selector.update_pool_with_public_opinion_analysis(stock_code=self.stock_code)
        # self.assertTrue(result)

        # Get the public opinion analysis result
        public_opinion_stocks = self.public_opinion_selector.get_public_opinion_analysis(stock_code=self.stock_code)

        # Check if the pub field is updated (example)
        if public_opinion_stocks:
            for stock in public_opinion_stocks:
                if 'pub' in stock:
                    for strategy_name, pub_data in stock['pub'].items():
                        if 'score' in pub_data and 'value' in pub_data:
                            print(f"Strategy: {strategy_name}, Score: {pub_data['score']}, Value: {pub_data['value']}")
                        else:
                            print(f"Strategy: {strategy_name}, Missing score or value")
                else:
                    print(f"Stock {stock['code']} has no pub field")
        else:
            print("No public opinion analysis results found")

