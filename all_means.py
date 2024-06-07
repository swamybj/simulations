import yfinance as yf
import pandas as pd
import numpy as np

# Define the list of NASDAQ 100 tickers
nasdaq_100_tickers = ["AAPL", "MSFT", "AMZN", "GOOGL", "META"]

# Function to fetch historical data and calculate indicators
def fetch_data_and_calculate_indicators(ticker):
    data = yf.download(ticker, period="1y", interval="1d")
    data['21_MA'] = data['Close'].rolling(window=21).mean()
    data['50_MA'] = data['Close'].rolling(window=50).mean()
    data['RSI'] = calculate_rsi(data['Close'])
    data['MACD'], data['Signal'] = calculate_macd(data['Close'])
    return data

# Function to calculate RSI
def calculate_rsi(series, period=14):
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to calculate mean of the last 12 cycles
def calculate_mean_of_last_12_cycles(data):
    last_12_cycles = data.tail(12)
    mean_21_MA = last_12_cycles['21_MA'].mean()
    mean_50_MA = last_12_cycles['50_MA'].mean()
    mean_RSI = last_12_cycles['RSI'].mean()
    return mean_21_MA, mean_50_MA, mean_RSI

# Function to calculate MACD
def calculate_macd(series, short_period=12, long_period=26, signal_period=9):
    short_ema = series.ewm(span=short_period, adjust=False).mean()
    long_ema = series.ewm(span=long_period, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    return macd, signal


# Function to check trading signals
def check_trading_signals(ticker,data):
    signals = []

    for i in range(1, len(data)):
        if data['21_MA'][i] > data['50_MA'][i] and data['RSI'][i] < 70 and data['MACD'][i] > data['Signal'][i]:
            signals.append(f"Buy signal for {data.index[i].date()}")
        elif data['21_MA'][i] < data['50_MA'][i] and data['RSI'][i] > 30 and data['MACD'][i] < data['Signal'][i]:
            signals.append(f"Sell signal for {data.index[i].date()}")
    return signals

# Main script
all_means = {}
for ticker in nasdaq_100_tickers:
    data = fetch_data_and_calculate_indicators(ticker)
    mean_21_MA, mean_50_MA, mean_RSI = calculate_mean_of_last_12_cycles(data)
    signals = check_trading_signals(ticker,data)
    all_means[ticker] = {
        'Mean_21_MA': mean_21_MA,
        'Mean_50_MA': mean_50_MA,
        'Mean_RSI': mean_RSI,
        'signals': signals
    }

# Display the results
for ticker, means in all_means.items():
    print(f"Ticker: {ticker}")
    print(f"Mean 21 MA: {means['Mean_21_MA']}")
    print(f"Mean 50 MA: {means['Mean_50_MA']}")
    print(f"Mean RSI: {means['Mean_RSI']}")
    print(f"signals: {means['signals']}")
    print("\n")
