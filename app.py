from flask import Flask, render_template, request, redirect, url_for, session
from models import ensure_user_exists, get_user_balance, get_user_wallet, get_wallet_value, buy_crypto, sell_crypto, get_trade_history

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        ensure_user_exists(username)
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    balance = get_user_balance(username)
    wallet_value = get_wallet_value(username)  # This should now fetch the correct value
    holdings = get_user_wallet(username)
    
    return render_template('wallet.html', username=username, balance=balance, wallet_value=wallet_value, holdings=holdings)

@app.route('/buy', methods=['POST'])
def buy():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    symbol = request.form['symbol']
    amount = float(request.form['amount'])
    buy_crypto(username, symbol, amount)
    return redirect(url_for('index'))

@app.route('/sell', methods=['POST'])
def sell():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    symbol = request.form['symbol']
    amount = float(request.form['amount'])
    sell_crypto(username, symbol, amount)
    return redirect(url_for('index'))

@app.route('/trade_history')
def trade_history():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    history = get_trade_history(username)
    return render_template('trade_history.html', history=history)

if __name__ == '__main__':
    app.run(debug=True)
