
import pandas as pd
import logging
import os
from datetime import datetime
from .interfaces import IDataProvider

logger = logging.getLogger("DataEngine")

class CsvCandlePlayer(IDataProvider):
    """
    Reads a CSV file and yields candles one by one to simulate live market.
    Expected CSV columns: 'Open time', 'Open', 'High', 'Low', 'Close', 'Volume'
    """

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.data = None
        self.current_index = 0
        self.current_timestamp = 0
        
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Data file not found: {self.csv_path}")
            
        try:
            # Load CSV
            df = pd.read_csv(self.csv_path)
            
            # Standardize columns (strip spaces)
            df.columns = [c.strip() for c in df.columns]
            
            # Ensure required columns exist
            required = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required):
                raise ValueError(f"CSV missing columns. Required: {required}")
                
            # Sort by time just in case
            df = df.sort_values('Open time').reset_index(drop=True)
            
            self.data = df
            logger.info(f"Loaded {len(df)} candles from {os.path.basename(self.csv_path)}")
            
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise

    def get_next_candle(self):
        """Returns the next row as a dictionary."""
        if self.current_index >= len(self.data):
            return None # End of Data
            
        row = self.data.iloc[self.current_index]
        self.current_index += 1
        
        # Convert row to dict
        candle = {
            'timestamp': int(row['Open time']),
            'open': float(row['Open']),
            'high': float(row['High']),
            'low': float(row['Low']),
            'close': float(row['Close']),
            'volume': float(row['Volume'])
        }
        
        # Update internal clock
        self.current_timestamp = candle['timestamp']
        
        return candle

    def get_server_time(self) -> int:
        """Returns the close time of the LAST processed candle (simulated 'now')."""
        return self.current_timestamp
