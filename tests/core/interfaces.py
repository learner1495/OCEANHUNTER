
from abc import ABC, abstractmethod
from typing import Dict, Any

class IDataProvider(ABC):
    """Interface for fetching market data (Live or Backtest)."""
    
    @abstractmethod
    def get_next_candle(self) -> Dict[str, Any]:
        """Returns the next candle or None if EOF."""
        pass

    @abstractmethod
    def get_server_time(self) -> int:
        """Returns current simulated or real server time (ms)."""
        pass

class IExecutionEngine(ABC):
    """Interface for executing orders."""
    pass
