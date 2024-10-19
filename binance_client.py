from binance.client import Client
import os

API_KEY = 'qIjf0Zlm1UW33VnTSXDNTEGt4lgK6t03KHX5GLVqZycWJmjZdiiF4gLt6SG2iR8U'
API_SECRET = '9BzlnqOZsTlNJq1snlqutvyQvrDOkLvwZhKxYGZsmSqUzD2TKL5ZNggTUDm8cA7a'

client = Client(API_KEY, API_SECRET)

def get_all_crypto_usdt_pairs():
    # Fetch all symbols and filter for crypto-USDT pairs
    exchange_info = client.get_exchange_info()
    pairs = [s['symbol'] for s in exchange_info['symbols'] if 'USDT' in s['symbol']]
    return pairs

def get_price(symbol):
    # Get the latest price for the specified symbol
    avg_price = client.get_avg_price(symbol=symbol)
    return avg_price['price']