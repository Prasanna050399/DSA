from kiteconnect import KiteConnect
import pandas as pd

# Initialize Kite API
kite = KiteConnect(api_key="your_api_key")
kite.set_access_token("your_access_token")

# User-specified investment amount per stock
investment_amount = 500

# Active trades dictionary to track stocks with open positions
active_trades = {}

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
                    affordable_stocks.append((exchange, stock['tradingsymbol']))
    return affordable_stocks

# Function to calculate indicators for momentum
def calculate_indicators(stock_symbol, exchange):
    data = kite.historical_data(f"{exchange}:{stock_symbol}", "day", "2023-01-01", "2023-12-31")  # Adjust dates as needed
    df = pd.DataFrame(data)
    df['20_MA'] = df['close'].rolling(window=20).mean()
    df['50_MA'] = df['close'].rolling(window=50).mean()
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

    # Check if funds are available for the trade
    available_funds = check_funds()
    if available_funds < investment_amount:
        print(f"Insufficient funds to buy {stock_symbol}. Available funds: {available_funds}")
        return

    # Entry Condition: Momentum indicators + Price within investment amount
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
        print(f"Buy order placed for {exchange}:{stock_symbol} with quantity {quantity}")

# Function to exit a trade if exit conditions are met
def exit_trade(stock_symbol):
    stock_info = active_trades[stock_symbol]
    exchange = stock_info['exchange']
    df = calculate_indicators(stock_symbol, exchange)
    latest = df.iloc[-1]
    quantity = stock_info['quantity']

    # Exit Condition: Profit-taking or minimal stop-loss
    if latest['RSI'] > 70 or (latest['close'] < stock_info['purchase_price'] * 0.99):  # Reduced stop-loss to 1%
        kite.place_order(variety="regular",
                         exchange=exchange,
                         tradingsymbol=stock_symbol,
                         transaction_type="SELL",
                         quantity=quantity,
                         order_type="MARKET",
                         product="CNC")
        del active_trades[stock_symbol]
        print(f"Sell order placed for {exchange}:{stock_symbol}")

# Main function to execute the strategy daily
def execute_strategy():
    # Step 1: Screen stocks dynamically and consider only stocks within investment limit
    affordable_stocks = dynamic_stock_screener()

    # Step 2: Check for new trade entries
    for exchange, stock in affordable_stocks:
        enter_trade(stock, exchange)

    # Step 3: Monitor active trades (purchased stocks) for exit conditions
    for stock in list(active_trades.keys()):
        exit_trade(stock)

# Example loop for daily execution
while True:
    execute_strategy()
    # Schedule this to run daily at market open
