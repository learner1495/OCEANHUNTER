
import pandas as pd
import logging
from .interfaces import IDataProvider

logger = logging.getLogger("DataEngine")

class CsvCandlePlayer(IDataProvider):
    """
    Reads historical data from CSV and serves it candle by candle.
    Compatible with:
    1. Generated Test Data (timestamp, open, high...)
    2. Binance/MEXC Export (Open time, Open, High...)
    """
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.data = pd.DataFrame()
        self.current_index = 0
        self._load_data()

    def _load_data(self):
        try:
            df = pd.read_csv(self.csv_path)
            
            # 1. Normalize Column Names (Lowercase & Strip)
            df.columns = [c.lower().strip() for c in df.columns]
            
            # 2. Map Standard Names
            rename_map = {
                'open time': 'timestamp',
                'time': 'timestamp',
                'date': 'timestamp',
                'vol': 'volume'
            }
            df.rename(columns=rename_map, inplace=True)
            
            # 3. Validate Required Columns
            required = {'timestamp', 'open', 'high', 'low', 'close', 'volume'}
            if not required.issubset(df.columns):
                missing = required - set(df.columns)
                raise ValueError(f"CSV missing columns: {missing}. Found: {list(df.columns)}")
                
            # 4. Sort by time
            df.sort_values('timestamp', inplace=True)
            df.reset_index(drop=True, inplace=True)
            
            self.data = df
            logger.info(f"Loaded {len(df)} candles from {self.csv_path}")
            
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise

    def get_next_candle(self):
        if self.current_index < len(self.data):
            # Convert row to dict
            candle = self.data.iloc[self.current_index].to_dict()
            self.current_index += 1
            return candle
        return None

    def get_server_time(self):
        # Return time of current candle (Simulation Time)
        if self.current_index > 0:
            return self.data.iloc[self.current_index - 1]['timestamp']
        return 0
