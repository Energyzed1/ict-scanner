"""
Interactive Brokers data source implementation
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, AsyncGenerator
import pandas as pd
from ib_insync import IB, Contract, BarData
from loguru import logger

from .base import DataSource

class IBDataSource(DataSource):
    """Interactive Brokers data source implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize IB connection settings"""
        super().__init__(config)
        self.ib = IB()
        self.subscriptions = {}  # symbol -> Contract mapping
        self.data_queues = {}   # (symbol, timeframe) -> asyncio.Queue
        
    async def connect(self) -> None:
        """Connect to IB TWS or Gateway"""
        try:
            host = self.config["credentials"]["ib_host"]
            port = self.config["credentials"]["ib_port"]
            client_id = self.config["credentials"]["ib_client_id"]
            
            await self.ib.connectAsync(host, port, client_id)
            self.connected = True
            logger.info(f"Connected to IB on {host}:{port}")
            
        except Exception as e:
            self.connected = False
            raise ConnectionError(f"Failed to connect to IB: {str(e)}")
            
    async def disconnect(self) -> None:
        """Disconnect from IB"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IB")
            
    def _create_contract(self, symbol: str) -> Contract:
        """Create an IB contract for the symbol"""
        # For futures, we need to determine the active contract month
        if symbol in ["MES", "MNQ"]:
            # Get next quarterly expiration
            today = datetime.now()
            month = (today.month - 1) // 3 * 3 + 3
            year = today.year if month > today.month else today.year + 1
            expiry = f"{year}{month:02d}"
            
            contract = Contract(
                symbol=symbol,
                secType="FUT",
                exchange="CME",
                currency="USD",
                lastTradeDateOrContractMonth=expiry
            )
        else:
            raise ValueError(f"Unsupported symbol: {symbol}")
            
        return contract
        
    async def subscribe(self, symbol: str, timeframes: List[str]) -> None:
        """Subscribe to market data for the symbol"""
        if not self.connected:
            raise ConnectionError("Not connected to IB")
            
        try:
            # Create contract if not already subscribed
            if symbol not in self.subscriptions:
                contract = self._create_contract(symbol)
                self.subscriptions[symbol] = contract
            else:
                contract = self.subscriptions[symbol]
                
            # Subscribe to each timeframe
            for tf in timeframes:
                queue = asyncio.Queue()
                self.data_queues[(symbol, tf)] = queue
                
                # Start historical data stream
                self.ib.reqRealTimeBars(
                    contract,
                    barSize=self._timeframe_to_seconds(tf),
                    whatToShow="TRADES",
                    useRTH=True
                )
                
            logger.info(f"Subscribed to {symbol} on timeframes: {timeframes}")
            
        except Exception as e:
            raise ConnectionError(f"Failed to subscribe to {symbol}: {str(e)}")
            
    async def unsubscribe(self, symbol: str, timeframes: List[str]) -> None:
        """Unsubscribe from market data"""
        if symbol in self.subscriptions:
            contract = self.subscriptions[symbol]
            for tf in timeframes:
                self.ib.cancelRealTimeBars(contract)
                if (symbol, tf) in self.data_queues:
                    del self.data_queues[(symbol, tf)]
                    
            if not any(k[0] == symbol for k in self.data_queues):
                del self.subscriptions[symbol]
                
            logger.info(f"Unsubscribed from {symbol} on timeframes: {timeframes}")
            
    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start_time: pd.Timestamp,
        end_time: pd.Timestamp
    ) -> pd.DataFrame:
        """Get historical bar data from IB"""
        if not self.connected:
            raise ConnectionError("Not connected to IB")
            
        contract = self._create_contract(symbol)
        duration = self._calc_duration(start_time, end_time)
        bar_size = self._timeframe_to_ib_size(timeframe)
        
        try:
            bars = await self.ib.reqHistoricalDataAsync(
                contract,
                endDateTime=end_time.strftime("%Y%m%d %H:%M:%S"),
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow="TRADES",
                useRTH=True,
                formatDate=1
            )
            
            return self._bars_to_dataframe(bars)
            
        except Exception as e:
            raise ConnectionError(f"Failed to get historical data: {str(e)}")
            
    async def get_latest_data(
        self,
        symbol: str,
        timeframe: str
    ) -> pd.DataFrame:
        """Get latest bar data"""
        # Get last 1 bar of historical data
        end_time = pd.Timestamp.now()
        start_time = end_time - pd.Timedelta(self._timeframe_to_seconds(timeframe), unit="s")
        return await self.get_historical_data(symbol, timeframe, start_time, end_time)
        
    async def stream_data(
        self,
        symbol: str,
        timeframe: str
    ) -> AsyncGenerator[pd.DataFrame, None]:
        """Stream real-time bar data"""
        if not self.connected:
            raise ConnectionError("Not connected to IB")
            
        if (symbol, timeframe) not in self.data_queues:
            raise ValueError(f"Not subscribed to {symbol} {timeframe}")
            
        queue = self.data_queues[(symbol, timeframe)]
        while True:
            bar = await queue.get()
            yield self._bars_to_dataframe([bar])
            
    def _bars_to_dataframe(self, bars: List[BarData]) -> pd.DataFrame:
        """Convert IB bars to pandas DataFrame"""
        data = []
        for bar in bars:
            data.append({
                "timestamp": pd.Timestamp(bar.date),
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume
            })
        return pd.DataFrame(data)
        
    @staticmethod
    def _timeframe_to_seconds(timeframe: str) -> int:
        """Convert timeframe string to seconds"""
        unit = timeframe[-1]
        value = int(timeframe[:-1])
        
        if unit == "m":
            return value * 60
        elif unit == "h":
            return value * 3600
        else:
            raise ValueError(f"Invalid timeframe: {timeframe}")
            
    @staticmethod
    def _timeframe_to_ib_size(timeframe: str) -> str:
        """Convert timeframe to IB bar size setting"""
        unit = timeframe[-1]
        value = timeframe[:-1]
        
        if unit == "m":
            return f"{value} mins"
        elif unit == "h":
            return f"{value} hour"
        else:
            raise ValueError(f"Invalid timeframe: {timeframe}")
            
    @staticmethod
    def _calc_duration(start_time: pd.Timestamp, end_time: pd.Timestamp) -> str:
        """Calculate IB duration string"""
        delta = end_time - start_time
        days = delta.days
        
        if days <= 1:
            return "1 D"
        elif days <= 7:
            return "1 W"
        elif days <= 31:
            return "1 M"
        elif days <= 365:
            return "1 Y"
        else:
            return "5 Y" 