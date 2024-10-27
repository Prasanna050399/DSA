from kiteconnect import KiteConnect
import pandas as pd
import json
import os

# Initialize Kite API
kite = KiteConnect(api_key="your_api_key")
kite.set_access_token("your_access_token")

# User-specified investment amount per stock
investment_amount = 500

# File path for storing active trades
active_trades_file = "active_trades.json"
active_trades = {}

# Load active trades from file (if any)
if os.path.exists(active_trades_file):
    with open(active_trades_file, "r") as file:
        active_trades = json.load(file)

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
                ltp = kite.ltp(f"{exchange}:{stock['tradingsymbol']}")[f"{exchange}:" + stock['tradingsymbol']]['last_price']
                if ltp <= investment_amount and stock['tradingsymbol'] not in active_trades:
                    # Only add stock if it has sufficient trading volume
                    stock_info = kite.quote(f"{exchange}:{stock['tradingsymbol']}")
                    avg_volume = stock_info['volume']['average']
                    if stock_info['volume']['last'] > 1.5 * avg_volume:
                        affordable_stocks.append((exchange, stock['tradingsymbol']))
    return affordable_stocks

# Function to calculate indicators for momentum
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

# Function to enter a trade if entry conditions and funds are met
def enter_trade(stock_symbol, exchange):
    df = calculate_indicators(stock_symbol, exchange)
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    available_funds = check_funds()
    if available_funds < investment_amount:
        print(f"Insufficient funds to buy {stock_symbol}. Available funds: {available_funds}")
        return

    if prev['20_MA'] < prev['50_MA'] and latest['20_MA'] > latest['50_MA'] \
            and 50 <= latest['RSI'] <= 65 and latest['volume'] > 1.5 * latest['Volume_Avg']:
        quantity = int(investment_amount / latest['close'])
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
            'purchase_price': latest['close'],
            'entry_date': latest['date']
        }
        save_active_trades()
        print(f"Buy order placed for {exchange}:{stock_symbol} with quantity {quantity}")

# Function to exit a trade if exit conditions (RSI, Trailing Stop-Loss, Moving Average Crossover) are met
def exit_trade(stock_symbol):
    stock_info = active_trades[stock_symbol]
    exchange = stock_info['exchange']
    df = calculate_indicators(stock_symbol, exchange)
    latest = df.iloc[-1]
    quantity = stock_info['quantity']

    highest_price_since_entry = max(df[df['date'] >= stock_info['entry_date']]['close'])
    trailing_stop_price = highest_price_since_entry * 0.985  # 1.5% below highest price

    if latest['RSI'] > 70 or latest['close'] <= trailing_stop_price or latest['5_MA'] < latest['20_MA']:
        kite.place_order(variety="regular",
                         exchange=exchange,
                         tradingsymbol=stock_symbol,
                         transaction_type="SELL",
                         quantity=quantity,
                         order_type="MARKET",
                         product="CNC")
        del active_trades[stock_symbol]
        save_active_trades()
        print(f"Sell order placed for {exchange}:{stock_symbol}")

# Main function to execute the strategy daily
def execute_strategy():
    affordable_stocks = dynamic_stock_screener()
    for exchange, stock in affordable_stocks:
        enter_trade(stock, exchange)
    for stock in list(active_trades.keys()):
        exit_trade(stock)

# Example loop for daily execution
while True:
    execute_strategy()
    # Schedule this to run daily at market open
