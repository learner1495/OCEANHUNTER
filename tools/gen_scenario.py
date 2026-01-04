
import pandas as pd
import numpy as np
import os

def create_winning_scenario():
    print("🎨 Generating Synthetic 'Perfect Setup' Data...")
    
    # 1. Create a baseline
    length = 300
    # FIX: Use '15min' instead of '15T' to avoid FutureWarning
    dates = pd.date_range(start='2024-01-01', periods=length, freq='15min') 
    
    # 2. Pattern: Stable -> Crash (Buy) -> Pump (Sell) -> Stable
    prices = []
    base_price = 100.0
    
    for i in range(length):
        if i < 50: 
            # Stable
            price = base_price + np.random.normal(0, 0.2)
        elif 50 <= i < 70:
            # CRASH (Trigger RSI < 30)
            base_price -= 1.5 # Fast drop
            price = base_price
        elif 70 <= i < 100:
            # Bottom Consolidation
            price = base_price + np.random.normal(0, 0.5)
        elif 100 <= i < 130:
            # PUMP (Trigger Sell)
            base_price += 1.5 # Fast pump
            price = base_price
        else:
            # Stable again
            price = base_price + np.random.normal(0, 0.2)
            
        prices.append(price)

    # 3. Create DataFrame
    # FIX: Column MUST be named 'timestamp' and be Unix/Int format for DataEngine compatibility
    df = pd.DataFrame({
        'timestamp': dates.astype('int64') // 10**9, 
        'open': prices,
        'high': [p + 0.5 for p in prices],
        'low': [p - 0.5 for p in prices],
        'close': prices,
        'volume': [1000 + np.random.randint(0, 500) for _ in range(length)]
    })
    
    # Save
    os.makedirs("tests/data/scenarios", exist_ok=True)
    path = "tests/data/scenarios/SCENARIO_WIN.csv"
    df.to_csv(path, index=False)
    print(f"✅ Created: {path}")
    return path

if __name__ == "__main__":
    create_winning_scenario()
