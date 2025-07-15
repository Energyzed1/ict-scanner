"""
Base interface for market data sources
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, AsyncGenerator
import pandas as pd

class DataSource(ABC):
    """Abstract base class for market data sources"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the data source
        
        Args:
            config: Data source configuration
        """
        self.config = config
        self.connected = False
        
    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to the data source
        
        Raises:
            ConnectionError: If connection fails
        """
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the data source"""
        pass
        
    @abstractmethod
    async def subscribe(self, symbol: str, timeframes: List[str]) -> None:
        """
        Subscribe to market data for a symbol
        
        Args:
            symbol: Instrument symbol
            timeframes: List of timeframes to subscribe to
            
        Raises:
            ValueError: If symbol or timeframes are invalid
            ConnectionError: If subscription fails
        """
        pass
        
    @abstractmethod
    async def unsubscribe(self, symbol: str, timeframes: List[str]) -> None:
        """
        Unsubscribe from market data for a symbol
        
        Args:
            symbol: Instrument symbol
            timeframes: List of timeframes to unsubscribe from
        """
        pass
        
    @abstractmethod
    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start_time: pd.Timestamp,
        end_time: pd.Timestamp
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data
        
        Args:
            symbol: Instrument symbol
            timeframe: Timeframe string (e.g. "5m", "1h")
            start_time: Start time for historical data
            end_time: End time for historical data
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
            
        Raises:
            ValueError: If parameters are invalid
            ConnectionError: If data fetch fails
        """
        pass
        
    @abstractmethod
    async def get_latest_data(
        self,
        symbol: str,
        timeframe: str
    ) -> pd.DataFrame:
        """
        Get latest OHLCV data
        
        Args:
            symbol: Instrument symbol
            timeframe: Timeframe string
            
        Returns:
            DataFrame with latest candle data
            
        Raises:
            ValueError: If parameters are invalid
            ConnectionError: If data fetch fails
        """
        pass
        
    @abstractmethod
    async def stream_data(
        self,
        symbol: str,
        timeframe: str
    ) -> AsyncGenerator[pd.DataFrame, None]:
        """
        Stream real-time OHLCV data
        
        Args:
            symbol: Instrument symbol
            timeframe: Timeframe string
            
        Yields:
            DataFrame with latest candle data
            
        Raises:
            ValueError: If parameters are invalid
            ConnectionError: If streaming fails
        """
        pass 