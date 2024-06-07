import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Download price data from Yahoo Finance
def download_price_data(ticker, start_date, end_date):
    df = yf.download(ticker, start=start_date, end=end_date)
    return df['Adj Close']


# Calculate moving averages
def moving_average(data, window_size):
    return data.rolling(window=window_size).mean()


# Calculate Exponential Moving Average (EMA)
def ema(data, window_size):
    return data.ewm(span=window_size, min_periods=0, adjust=False).mean()


# Calculate MACD
def macd(data, short_window, long_window, signal_window):
    short_ema = ema(data, short_window)
    long_ema = ema(data, long_window)
    macd_line = short_ema - long_ema
    signal_line = ema(macd_line, signal_window)
    return macd_line, signal_line


# Generate signals
def generate_signals(price_data, short_window, long_window, signal_window):
    signals = pd.DataFrame(index=price_data.index)
    signals['Price'] = price_data
    signals['MA_short'] = moving_average(price_data, short_window)
    signals['MA_long'] = moving_average(price_data, long_window)
    signals['EMA_short'] = ema(price_data, short_window)
    signals['EMA_long'] = ema(price_data, long_window)
    signals['MACD'], signals['MACD_signal'] = macd(price_data, short_window, long_window, signal_window)

    # Generate crossover signals
    signals['MA_crossover'] = 0
    signals['EMA_crossover'] = 0
    signals.loc[signals['MA_short'] > signals['MA_long'], 'MA_crossover'] = 1
    signals.loc[signals['MA_short'] < signals['MA_long'], 'MA_crossover'] = -1
    signals.loc[signals['EMA_short'] > signals['EMA_long'], 'EMA_crossover'] = 1
    signals.loc[signals['EMA_short'] < signals['EMA_long'], 'EMA_crossover'] = -1

    return signals


# Define parameters
ticker = "TSLA"
start_date = "2023-06-01"
end_date = "2024-07-01"

# Download price data
price_data = download_price_data(ticker, start_date, end_date)

# Short and long periods for moving averages
short_ma_period = 50
long_ma_period = 200

# Short and long periods for MACD
short_ema_period = 12
long_ema_period = 26
signal_ema_period = 9

# Generate signals
signals = generate_signals(price_data, short_ma_period, long_ma_period, signal_ema_period)

# Plotting
plt.figure(figsize=(14, 7))
plt.plot(signals['Price'], label='Price')
plt.plot(signals['MA_short'], label='MA Short ({} days)'.format(short_ma_period))
plt.plot(signals['MA_long'], label='MA Long ({} days)'.format(long_ma_period))
plt.plot(signals['EMA_short'], label='EMA Short ({} days)'.format(short_ema_period))
plt.plot(signals['EMA_long'], label='EMA Long ({} days)'.format(long_ema_period))
plt.plot(signals['MACD'], label='MACD')
plt.plot(signals['MACD_signal'], label='MACD Signal')
plt.plot(signals.loc[signals['MA_crossover'] == 1].index,
         signals['Price'][signals['MA_crossover'] == 1],
         '^', markersize=10, color='g', lw=0, label='MA Buy Signal')
plt.plot(signals.loc[signals['MA_crossover'] == -1].index,
         signals['Price'][signals['MA_crossover'] == -1],
         'v', markersize=10, color='r', lw=0, label='MA Sell Signal')
plt.plot(signals.loc[signals['EMA_crossover'] == 1].index,
         signals['Price'][signals['EMA_crossover'] == 1],
         'o', markersize=7, color='b', lw=0, label='EMA Buy Signal')
plt.plot(signals.loc[signals['EMA_crossover'] == -1].index,
         signals['Price'][signals['EMA_crossover'] == -1],
         'x', markersize=7, color='y', lw=0, label='EMA Sell Signal')
plt.legend()
plt.title('MA vs MACD vs EMA Crossover Comparison')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()
