import sqlite3
from binance.client import Client

DB_NAME = 'crypto_sim.db'

# Initialize the Binance API client
binance_client = Client(api_key='your_api_key', api_secret='your_api_secret')

# Function to initialize the database (create tables)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create users table to store USDT balance and user info
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        usdt_balance REAL
    )''')

    # Create wallet table to store user's crypto holdings
    cursor.execute('''CREATE TABLE IF NOT EXISTS wallet (
        username TEXT,
        symbol TEXT,
        amount REAL,
        PRIMARY KEY (username, symbol),
        FOREIGN KEY (username) REFERENCES users(username)
    )''')

    # Create trade history table
    cursor.execute('''CREATE TABLE IF NOT EXISTS trade_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        symbol TEXT,
        action TEXT,  -- 'buy' or 'sell'
        amount REAL,
        price REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (username) REFERENCES users(username)
    )''')

    conn.commit()
    conn.close()

# Function to get current crypto prices from Binance
def get_price():
    # Fetch current prices for all crypto-USDT pairs
    prices = {}
    try:
        # Get ticker prices for all pairs
        ticker_data = binance_client.get_all_tickers()
        for item in ticker_data:
            symbol = item['symbol']
            if symbol.endswith('USDT'):
                prices[symbol] = float(item['price'])
    except Exception as e:
        print(f"Error fetching prices: {e}")

    return prices

# Function to get the user's crypto holdings (wallet)
def get_user_wallet(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT symbol, amount FROM wallet WHERE username=?", (username,))
    holdings = cursor.fetchall()

    conn.close()
    return holdings

# Function to calculate the total wallet value in USDT
def get_wallet_value(username):
    holdings = get_user_wallet(username)
    prices = get_price()
    total_value = 0.0

    for symbol, amount in holdings:
        # Append 'USDT' to symbol if not present
        if not symbol.endswith('USDT'):
            symbol += 'USDT'

        # Get the current price of the crypto
        price = prices.get(symbol, 0.0)
        if price > 0:
            value = amount * price
            total_value += value
            print(f"Symbol: {symbol}, Amount: {amount}, Price: {price}, Value: {value}")  # Debug statement
        else:
            print(f"Warning: No price found for {symbol}.")  # Debug statement

    print(f"Total Wallet Value for {username}: {total_value}")  # Debug statement
    return total_value

# Function to get the user's USDT balance
def get_user_balance(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT usdt_balance FROM users WHERE username=?", (username,))
    balance = cursor.fetchone()[0]

    conn.close()
    return balance

# Function to get the user's trade history
def get_trade_history(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT symbol, action, amount, price, timestamp FROM trade_history WHERE username=? ORDER BY timestamp DESC", (username,))
    history = cursor.fetchall()

    conn.close()
    return history

# Function to check if user exists and create a new user if not
def ensure_user_exists(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT usdt_balance FROM users WHERE username=?", (username,))
    result = cursor.fetchone()

    if not result:
        # If user does not exist, create user with default USDT balance
        cursor.execute("INSERT INTO users (username, usdt_balance) VALUES (?, ?)", (username, 100000.0))  # Default balance: 100,000 USDT
        conn.commit()

    conn.close()

# Buy crypto
def buy_crypto(username, symbol, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Ensure the user exists
    ensure_user_exists(username)

    # Ensure symbol ends with 'USDT' for trading pair
    symbol_pair = symbol if symbol.endswith('USDT') else symbol + 'USDT'
    
    # Get price of the crypto
    try:
        price = float(get_price()[symbol_pair])
    except KeyError:
        raise ValueError(f"Price for symbol {symbol_pair} not found.")

    total_cost = amount * price

    # Check if user has enough USDT balance
    cursor.execute("SELECT usdt_balance FROM users WHERE username=?", (username,))
    balance = cursor.fetchone()[0]

    if balance < total_cost:
        raise ValueError("Insufficient USDT balance.")

    # Deduct from USDT balance and update holdings
    new_balance = balance - total_cost
    cursor.execute("UPDATE users SET usdt_balance=? WHERE username=?", (new_balance, username))

    cursor.execute("SELECT amount FROM wallet WHERE username=? AND symbol=?", (username, symbol))
    result = cursor.fetchone()

    if result:
        new_amount = result[0] + amount
        cursor.execute("UPDATE wallet SET amount=? WHERE username=? AND symbol=?", (new_amount, username, symbol))
    else:
        cursor.execute("INSERT INTO wallet (username, symbol, amount) VALUES (?, ?, ?)", (username, symbol, amount))

    # Add trade to history
    cursor.execute("INSERT INTO trade_history (username, symbol, action, amount, price) VALUES (?, ?, 'buy', ?, ?)",
                   (username, symbol, amount, price))

    conn.commit()
    conn.close()

# Sell crypto
def sell_crypto(username, symbol, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Ensure the user exists
    ensure_user_exists(username)

    # Ensure symbol ends with 'USDT' for trading pair
    symbol_pair = symbol if symbol.endswith('USDT') else symbol + 'USDT'
    
    # Get price of the crypto
    try:
        price = float(get_price()[symbol_pair])
    except KeyError:
        raise ValueError(f"Price for symbol {symbol_pair} not found.")

    # Check if user has enough crypto holdings to sell
    cursor.execute("SELECT amount FROM wallet WHERE username=? AND symbol=?", (username, symbol))
    result = cursor.fetchone()

    if not result or result[0] < amount:
        raise ValueError("Insufficient crypto holdings.")

    # Calculate USDT earned and update USDT balance
    total_value = amount * price
    cursor.execute("SELECT usdt_balance FROM users WHERE username=?", (username,))
    balance = cursor.fetchone()[0]
    new_balance = balance + total_value
    cursor.execute("UPDATE users SET usdt_balance=? WHERE username=?", (new_balance, username))

    # Update crypto holdings
    new_amount = result[0] - amount
    if new_amount > 0:
        cursor.execute("UPDATE wallet SET amount=? WHERE username=? AND symbol=?", (new_amount, username, symbol))
    else:
        cursor.execute("DELETE FROM wallet WHERE username=? AND symbol=?", (username, symbol))

    # Add trade to history
    cursor.execute("INSERT INTO trade_history (username, symbol, action, amount, price) VALUES (?, ?, 'sell', ?, ?)",
                   (username, symbol, amount, price))

    conn.commit()
    conn.close()
