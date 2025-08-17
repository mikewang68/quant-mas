"""
Data module for the quant trading system.
Contains modules for data fetching, storage, and management.
"""

# Import main classes for easy access
from .mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

__all__ = [
    "MongoDBManager",
    "AkshareClient"
]

