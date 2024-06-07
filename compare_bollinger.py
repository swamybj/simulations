import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator, WilliamsRIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands


# Fetch historical stock data
def fetch_data(ticker, period="1y"):
    data = yf.download(ticker, period=period, interval="1d")
    return data


# Calculate Fibonacci retracement levels
def calculate_fibonacci_levels(data):
    max_price = data['Close'].max()
    min_price = data['Close'].min()
    diff = max_price - min_price
    levels = {
        '0%': max_price,
        '23.6%': max_price - 0.236 * diff,
        '38.2%': max_price - 0.382 * diff,
        '50%': max_price - 0.5 * diff,
        '61.8%': max_price - 0.618 * diff,
        '100%': min_price
    }
    return levels


# Calculate technical indicators
def calculate_indicators(data):
    # Bollinger Bands
    bb = BollingerBands(close=data['Close'], window=20, window_dev=2)
    data['bb_bbm'] = bb.bollinger_mavg()
    data['bb_bbh'] = bb.bollinger_hband()
    data['bb_bbl'] = bb.bollinger_lband()

    # RSI
    rsi = RSIIndicator(close=data['Close'], window=14)
    data['RSI'] = rsi.rsi()

    # Williams %R
    wr = WilliamsRIndicator(high=data['High'], low=data['Low'], close=data['Close'], lbp=14)
    data['Williams %R'] = wr.williams_r()

    # MACD
    macd = MACD(close=data['Close'])
    data['MACD'] = macd.macd()
    data['MACD Signal'] = macd.macd_signal()
    data['MACD Hist'] = macd.macd_diff()

    # EMAs
    data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
    data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
    data['EMA100'] = data['Close'].ewm(span=100, adjust=False).mean()
    data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()

    return data


# Analyze market conditions
def analyze_market_conditions(data):
    bb_signal = ('Overbought' if data['Close'].iloc[-1] > data['bb_bbh'].iloc[-1]
                 else 'Oversold' if data['Close'].iloc[-1] < data['bb_bbl'].iloc[-1]
    else 'Neutral')

    rsi_signal = ('Overbought' if data['RSI'].iloc[-1] > 70
                  else 'Oversold' if data['RSI'].iloc[-1] < 30
    else 'Neutral')

    wr_signal = ('Overbought' if data['Williams %R'].iloc[-1] > -20
                 else 'Oversold' if data['Williams %R'].iloc[-1] < -80
    else 'Neutral')

    return bb_signal, rsi_signal, wr_signal


# Generate buy and sell signals
def generate_signals(data):
    buy_signals = []
    sell_signals = []

    for i in range(1, len(data)):
        if data['MACD'].iloc[i] > data['MACD Signal'].iloc[i] and data['MACD'].iloc[i - 1] <= data['MACD Signal'].iloc[
            i - 1]:
            buy_signals.append(i)
        elif data['MACD'].iloc[i] < data['MACD Signal'].iloc[i] and data['MACD'].iloc[i - 1] >= \
                data['MACD Signal'].iloc[i - 1]:
            sell_signals.append(i)

        if data['RSI'].iloc[i] < 30:
            buy_signals.append(i)
        elif data['RSI'].iloc[i] > 70:
            sell_signals.append(i)

        if data['EMA20'].iloc[i] > data['EMA50'].iloc[i] and data['EMA20'].iloc[i - 1] <= data['EMA50'].iloc[i - 1]:
            buy_signals.append(i)
        elif data['EMA20'].iloc[i] < data['EMA50'].iloc[i] and data['EMA20'].iloc[i - 1] >= data['EMA50'].iloc[i - 1]:
            sell_signals.append(i)

    data['Buy Signal'] = [np.nan] * len(data)
    data['Sell Signal'] = [np.nan] * len(data)

    for signal in buy_signals:
        data['Buy Signal'].iloc[signal] = data['Close'].iloc[signal]
    for signal in sell_signals:
        data['Sell Signal'].iloc[signal] = data['Close'].iloc[signal]

    return data


# Plot the data
def plot_data(data, ticker, fib_levels):
    plt.figure(figsize=(14, 10))

    # Plot close price, Bollinger Bands, and Fibonacci levels
    plt.subplot(3, 1, 1)
    plt.plot(data['Close'], label='Close Price')
    plt.plot(data['bb_bbm'], label='Bollinger Middle Band')
    plt.plot(data['bb_bbh'], label='Bollinger Upper Band')
    plt.plot(data['bb_bbl'], label='Bollinger Lower Band')
    for level, price in fib_levels.items():
        plt.axhline(y=price, color='r', linestyle='--', label=f'Fib {level}')
    plt.scatter(data.index, data['Buy Signal'], marker='^', color='g', label='Buy Signal', alpha=1)
    plt.scatter(data.index, data['Sell Signal'], marker='v', color='r', label='Sell Signal', alpha=1)
    plt.title(f'{ticker} Price with Bollinger Bands, Fibonacci Levels, and Signals')
    plt.legend()

    # Plot RSI
    plt.subplot(3, 1, 2)
    plt.plot(data['RSI'], label='RSI', color='purple')
    plt.axhline(y=70, color='r', linestyle='--')
    plt.axhline(y=30, color='r', linestyle='--')
    plt.title('Relative Strength Index (RSI)')
    plt.legend()

    # Plot Williams %R
    plt.subplot(3, 1, 3)
    plt.plot(data['Williams %R'], label='Williams %R', color='green')
    plt.axhline(y=-20, color='r', linestyle='--')
    plt.axhline(y=-80, color='r', linestyle='--')
    plt.title('Williams %R')
    plt.legend()

    plt.tight_layout()
    plt.show()


import requests
import pandas as pd
from datetime import date

def getTickers(market='nasdaq100',pnl='gainers'):
    # URL of the Slickcharts page containing S&P 500 tickers
    url = 'https://www.slickcharts.com/sp500'
    # url = 'https://www.slickcharts.com/'+market+'/'+pnl

    # Define the headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Request the page with headers
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Check that the request was successful

    # Read the page content into a pandas DataFrame
    tables = pd.read_html(response.text)

    # The first table on the page contains the tickers
    df = tables[0]

    # Extract the ticker symbols
    tickers = df['Symbol'].tolist()
    return tickers


# Main function to run the analysis for multiple tickers
def main(tickers):
    for ticker in tickers:
        data = fetch_data(ticker)
        if len(data)!=0:
            fib_levels = calculate_fibonacci_levels(data)
            data = calculate_indicators(data)
            data = generate_signals(data)

            bb_signal, rsi_signal, wr_signal = analyze_market_conditions(data)
            print(f"Ticker: {ticker}")
            print(f"Bollinger Bands Signal: {bb_signal}")
            print(f"RSI Signal: {rsi_signal}")
            print(f"Williams %R Signal: {wr_signal}")

            plot_data(data, ticker, fib_levels)


# Example usage
tickers = getTickers()
main(tickers)
