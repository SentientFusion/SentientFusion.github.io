import numpy as np
import pandas as pd
from binance.client import Client

api_key = 'qIjf0Zlm1UW33VnTSXDNTEGt4lgK6t03KHX5GLVqZycWJmjZdiiF4gLt6SG2iR8U'
api_secret = '9BzlnqOZsTlNJq1snlqutvyQvrDOkLvwZhKxYGZsmSqUzD2TKL5ZNggTUDm8cA7a'

client = Client(api_key, api_secret)

def fetch_crypto_data(symbol, interval, lookback):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=lookback)
    df = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    return df[['close']]

def calculate_ewma_volatility(prices, lambda_value):
    returns = prices.pct_change().dropna()
    return returns.ewm(span=1/lambda_value).std().iloc[-1]

def calculate_stop_loss(current_price, volatility, multiplier):
    return current_price - (volatility * current_price * multiplier)

def main():
    symbol = input("Enter the cryptocurrency symbol (e.g., BTCUSDT): ").upper()
    interval = "1h"
    lookback = 50
    lambda_value = 0.94
    multiplier = 2

    data = fetch_crypto_data(symbol, interval, lookback)
    current_price = data['close'].iloc[-1]
    volatility = calculate_ewma_volatility(data['close'], lambda_value)
    stop_loss = calculate_stop_loss(current_price, volatility, multiplier)

    print(f"Current Price: {current_price}")
    print(f"EWMA Volatility: {volatility:.5f}")
    print(f"Stop-Loss Level: {stop_loss:.2f}")

if __name__ == "__main__":
    main()
