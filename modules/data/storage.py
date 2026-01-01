# modules/data/storage.py
import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional

class DataStorage:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            current = os.path.dirname(os.path.abspath(__file__))
            root = os.path.dirname(os.path.dirname(current))
            data_dir = os.path.join(root, "data", "ohlcv")
        self.data_dir = data_dir
        self._ensure_dir()

    def _ensure_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _get_filepath(self, symbol: str) -> str:
        safe_symbol = symbol.replace("/", "_").upper()
        return os.path.join(self.data_dir, f"{safe_symbol}.csv")

    def save_ohlcv(self, symbol: str, data: List[Dict]) -> bool:
        if not data:
            return False
        filepath = self._get_filepath(symbol)
        file_exists = os.path.exists(filepath)
        try:
            existing_timestamps = set()
            if file_exists:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        existing_timestamps.add(row.get('timestamp', ''))
            new_data = [row for row in data if str(row.get('timestamp', '')) not in existing_timestamps]
            if not new_data:
                return True
            fieldnames = ['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume']
            with open(filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                for row in new_data:
                    ts = row.get('timestamp', 0)
                    dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts else ''
                    writer.writerow({
                        'timestamp': ts, 'datetime': dt,
                        'open': row.get('open', 0), 'high': row.get('high', 0),
                        'low': row.get('low', 0), 'close': row.get('close', 0),
                        'volume': row.get('volume', 0)
                    })
            return True
        except Exception as e:
            print(f"[Storage] Error saving {symbol}: {e}")
            return False

    def get_latest(self, symbol: str, count: int = 100) -> List[Dict]:
        filepath = self._get_filepath(symbol)
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            return rows[-count:] if len(rows) > count else rows
        except Exception as e:
            print(f"[Storage] Error reading {symbol}: {e}")
            return []

    def get_stats(self, symbol: str) -> Dict[str, Any]:
        filepath = self._get_filepath(symbol)
        if not os.path.exists(filepath):
            return {"exists": False, "rows": 0}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            if not rows:
                return {"exists": True, "rows": 0}
            return {
                "exists": True, "rows": len(rows),
                "first_date": rows[0].get('datetime', 'N/A'),
                "last_date": rows[-1].get('datetime', 'N/A'),
                "file_size_kb": round(os.path.getsize(filepath) / 1024, 2)
            }
        except Exception as e:
            return {"exists": True, "rows": 0, "error": str(e)}

_storage: Optional[DataStorage] = None
def get_storage() -> DataStorage:
    global _storage
    if _storage is None:
        _storage = DataStorage()
    return _storage
