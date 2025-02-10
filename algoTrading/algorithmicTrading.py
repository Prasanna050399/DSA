from kiteconnect import KiteConnect
import pandas as pd
import json
import os
from datetime import datetime

# Initialize Kite API
kite = KiteConnect(api_key="your_api_key")
kite.set_access_token("your_access_token")

# User-defined investment amount per stock
investment_amount = 500

# File paths
active_trades_file = "active_trades.json"
log_file = f"logs_{datetime.now().strftime('%Y-%m-%d')}.txt"
active_trades = {}

# Load active trades from file (if any)
if os.path.exists(active_trades_file):
    with open(active_trades_file, "r") as file:
        active_trades = json.load(file)

# Function to log messages to a file
def log_message(message):
    with open(log_file, "a") as log:
        log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# Function to save active trades to a file
def save_active_trades():
    with open(active_trades_file, "w") as file:
        json.dump(active_trades, file)

# Function to check available funds in the wallet
def check_funds():
    funds_info = kite.margins("equity")
    return funds_info['available']['cash']

# Function to screen stocks dynamically within the budget limit on NSE and BSE
def dynamic_stock_screener():
    nse_stocks = kite.instruments("NSE")
    bse_stocks = kite.instruments("BSE")
    affordable_stocks = []

    for exchange, stock_list in [("NSE", nse_stocks), ("BSE", bse_stocks)]:
        for stock in stock_list:
            if stock['instrument_type'] == 'EQ':  # Only equity stocks
                ltp = kite.ltp(f"{exchange}:{stock['tradingsymbol']}")[f"{exchange}:{stock['tradingsymbol']}"]['last_price']
                if ltp <= investment_amount and stock['tradingsymbol'] not in active_trades:
                    stock_info = kite.quote(f"{exchange}:{stock['tradingsymbol']}")
                    avg_volume = stock_info['volume']['average']
                    if stock_info['volume']['last'] > 1.5 * avg_volume:
                        affordable_stocks.append((exchange, stock['tradingsymbol']))
                        log_message(f"Stock added to monitoring list: {exchange}:{stock['tradingsymbol']} at price {ltp}")
    return affordable_stocks

# Function to calculate indicators for combined strategy
def calculate_indicators(stock_symbol, exchange):
    data = kite.historical_data(f"{exchange}:{stock_symbol}", "day", "2023-01-01", "2023-12-31")
    df = pd.DataFrame(data)
    df['20_MA'] = df['close'].rolling(window=20).mean()
    df['50_MA'] = df['close'].rolling(window=50).mean()
    df['5_MA'] = df['close'].rolling(window=5).mean()
    df['Volume_Avg'] = df['volume'].rolling(window=10).mean()
    df['RSI'] = compute_rsi(df['close'])
    return df

# Function to compute RSI
def compute_rsi(series, period=14):
    delta = series.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to enter trade with combined strategy
def enter_trade(stock_symbol, exchange):
    df = calculate_indicators(stock_symbol, exchange)
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    available_funds = check_funds()

    if available_funds < investment_amount:
        log_message(f"Insufficient funds to buy {stock_symbol}. Available funds: {available_funds}")
        return

    # Momentum Condition: MA crossover and RSI between 50-65
    if prev['20_MA'] < prev['50_MA'] and latest['20_MA'] > latest['50_MA'] \
            and 50 <= latest['RSI'] <= 65 and latest['volume'] > 1.5 * latest['Volume_Avg']:
        quantity = int(investment_amount // latest['close'])
        place_buy_order(stock_symbol, exchange, quantity, latest['close'])

    # Mean Reversion Condition: Price drop below 50-MA and RSI < 35
    elif latest['close'] < latest['50_MA'] and latest['RSI'] < 35:
        quantity = int(investment_amount // latest['close'])
        place_buy_order(stock_symbol, exchange, quantity, latest['close'])

# Function to place buy order
def place_buy_order(stock_symbol, exchange, quantity, price):
    kite.place_order(variety="regular",
                     exchange=exchange,
                     tradingsymbol=stock_symbol,
                     transaction_type="BUY",
                     quantity=quantity,
                     order_type="MARKET",
                     product="CNC")
    active_trades[stock_symbol] = {
        'exchange': exchange,
        'quantity': quantity,
        'purchase_price': price,
        'entry_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_active_trades()
    log_message(f"Buy order placed for {exchange}:{stock_symbol} with quantity {quantity}")

# Function to exit trade with combined strategy
def exit_trade(stock_symbol):
    stock_info = active_trades[stock_symbol]
    exchange = stock_info['exchange']
    df = calculate_indicators(stock_symbol, exchange)
    latest = df.iloc[-1]
    quantity = stock_info['quantity']

    # Trailing Stop Loss or Momentum Reversal
    highest_price_since_entry = max(df[df['date'] >= stock_info['entry_date']]['close'])
    trailing_stop_price = highest_price_since_entry * 0.985  # 1.5% below highest price

    if latest['RSI'] > 70 or latest['close'] <= trailing_stop_price or latest['5_MA'] < latest['20_MA']:
        place_sell_order(stock_symbol, exchange, quantity)

    # Mean Reversion Exit: RSI above 60
    elif latest['RSI'] > 60:
        place_sell_order(stock_symbol, exchange, quantity)

# Function to place sell order
def place_sell_order(stock_symbol, exchange, quantity):
    kite.place_order(variety="regular",
                     exchange=exchange,
                     tradingsymbol=stock_symbol,
                     transaction_type="SELL",
                     quantity=quantity,
                     order_type="MARKET",
                     product="CNC")
    del active_trades[stock_symbol]
    save_active_trades()
    log_message(f"Sell order placed for {exchange}:{stock_symbol}")

# Execute the strategy with combined conditions
def execute_strategy():
    affordable_stocks = dynamic_stock_screener()
    available_funds = check_funds()

    log_message("Executing strategy...")

    # Sort affordable stocks by price (low to high) to maximize shares bought
    affordable_stocks.sort(key=lambda x: kite.ltp(f"{x[0]}:{x[1]}")[f"{x[0]}:{x[1]}"]['last_price'])

    for exchange, stock in affordable_stocks:
        price = kite.ltp(f"{exchange}:{stock}")[f"{exchange}:{stock}"]['last_price']

        # Calculate the quantity that can be bought for each stock within both budget and available funds limits
        quantity = min(int(available_funds // price), int(investment_amount // price))

        # Check if funds and calculated quantity are sufficient for a purchase
        if quantity > 0 and available_funds >= price * quantity:
            enter_trade(stock, exchange)

    # Log existing trades read from file
    log_message(f"Existing trades from file: {json.dumps(active_trades)}")

    # Execute exit conditions for active trades
    for stock in list(active_trades.keys()):
        exit_trade(stock)

# Example loop for daily execution
while True:
    execute_strategy()
    # Schedule this to run
