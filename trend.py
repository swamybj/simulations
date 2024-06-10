import pandas_ta as ta
import yfinance as yf
import requests
import pandas as pd
import numpy as np
ticker = 'NVDA'

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Using apply with a lambda function for more complex logic

def trend_signal_compare(row):
    if (row['Close'] > row['EMA_12']) & (row['MACD'] > row['MACD_Signal']):
        return 'Upside'
    elif (row['Close'] < row['EMA_12']) & (row['MACD'] < row['MACD_Signal']):
        return 'DownSide'
    else:
        return'Uncertain'

def stoch_signal_compare(row):
    if row['%K'] > 80 and row['%D']>80:
        return 'OverBought'
    elif row['%K'] > 20 and row['%D']<20:
        return 'OverSold'
    else:
        return'Uncertain'

def mean_reversion_compare(row):
    if row['Mean'] > row['Close']:
        return 'Above Mean'
    elif row['Mean'] < row['Close']:
        return 'Below Mean'
    else:
        return'Equal to Mean'

def long_trend_compare(row):
    long_term_trend=None
    if row['EMA_50'] > row['EMA_200']:
        long_term_trend = "Long-term uptrend"
    elif row['EMA_50'] < row['EMA_200']:
        long_term_trend = "Long-term downtrend"
    else:
        long_term_trend = "Long-term trend is uncertain"
    return long_term_trend

def getTickers(market='nasdaq100', pnl='gainers'):
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

def get_hist_data(ticker):
    data = yf.download(ticker, period="1y", interval="1d")
    if len(data)==0:
        return data
    # Ensure the data is sorted by date in ascending order
    data.reset_index(inplace=True)
    data = data.sort_values(by='Date')

    # Set the Date column as the index
    data.set_index('Date', inplace=True)
    # Calculate the percentage change
    data['Daily Change'] = data['Close'].pct_change() * 100
    data['Weekly Change'] = data['Close'].pct_change(periods=7) * 100
    data['Monthly Change'] = data['Close'].pct_change(periods=30) * 100
    data['Quarterly Change'] = data['Close'].pct_change(periods=90) * 100

    # Handle the first row which will have NaN for percentage change
    data['Daily Change'].fillna(0, inplace=True)
    data['Weekly Change'].fillna(0, inplace=True)
    data['Monthly Change'].fillna(0, inplace=True)
    data['Quarterly Change'].fillna(0, inplace=True)


    weekly_data = data.resample('W-MON').ffill()

    # Calculate the weekly percentage change
    weekly_data['Weekly % Change'] = weekly_data['Close'].pct_change() * 100

    # Merge the weekly percentage change back to the original data
    data = data.merge(weekly_data['Weekly % Change'], left_index=True, right_index=True, how='left')

    # Forward fill the weekly percentage change for days within the same week
    data['Weekly % Change'] = data['Weekly % Change'].fillna(method='ffill')

    # Handle NaN values (first week will have NaN)
    data['Weekly % Change'].fillna(0, inplace=True)

    # Resample data to monthly frequency starting on the 1st, forward-fill missing data
    monthly_data = data.resample('MS').ffill()

    # Calculate the monthly percentage change
    monthly_data['Monthly % Change'] = monthly_data['Close'].pct_change() * 100

    # Resample data to quarterly frequency starting on the 1st, forward-fill missing data
    quarterly_data = data.resample('QS-JAN').ffill()

    # Calculate the quarterly percentage change
    quarterly_data['Quarterly % Change'] = quarterly_data['Close'].pct_change() * 100

    # Merge the monthly and quarterly percentage changes back to the original data
    data = data.merge(monthly_data['Monthly % Change'], left_index=True, right_index=True, how='left')
    data = data.merge(quarterly_data['Quarterly % Change'], left_index=True, right_index=True, how='left')

    # Forward fill the monthly and quarterly percentage changes for days within the same period
    data['Monthly % Change'] = data['Monthly % Change'].fillna(method='ffill')
    data['Quarterly % Change'] = data['Quarterly % Change'].fillna(method='ffill')

    # Handle NaN values (first month and quarter will have NaN)
    data['Monthly % Change'].fillna(0, inplace=True)
    data['Quarterly % Change'].fillna(0, inplace=True)
    # Reset index to bring Date back as a column
    # Reset index to bring Date back as a column
    data.reset_index(inplace=True)

    # Calculate Indicators
    data['SMA_20'] = data['Close'].rolling(window=20).mean().fillna(0)
    data['SMA_50'] = data['Close'].rolling(window=50).mean().fillna(0)
    # Calculate EMA
    data['EMA_12'] = ta.ema(data['Close'], length=12).fillna(0)
    data['EMA_26'] = ta.ema(data['Close'], length=26).fillna(0)
    data['EMA_50'] = ta.ema(data['Close'], length=50).fillna(0)
    data['EMA_200'] = ta.ema(data['Close'], length=200).fillna(0)
    data['EMA_20'] = ta.ema(data['Close'], length=20).fillna(0)
    # data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean().fillna(0)

    # RSI Calculation
    delta = data['Close'].diff().fillna(0)
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().fillna(0)
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().fillna(0)
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs)).fillna(0)

    # MACD Calculation
    # Calculate MACD
    # macd = ta.macd(data['Close'], fast=50, slow=150, signal=26)
    # data['MACD_50_150_26'] = macd['MACD_50_150_26'].fillna(0)
    macd = ta.macd(data['Close'], fast=12, slow=26, signal=9)
    data['MACD'] = macd['MACD_12_26_9'].fillna(0)
    data['MACD_Signal'] = macd['MACDs_12_26_9'].fillna(0)
    data['MACD'] = data['MACD'].fillna(0)
    data['MACD_Signal'] = data['MACD_Signal'].fillna(0)
    # Calculate Stochastic Oscillator
    stoch = ta.stoch(data['High'], data['Low'], data['Close'], k=14, d=3)

    data['%K'] = stoch['STOCHk_14_3_3'].fillna(0)
    data['%D'] = stoch['STOCHd_14_3_3'].fillna(0)
    data['%K'] = data['%K'].fillna(0).astype(float)
    data['%D'] = data['%D'].fillna(0).astype(float)
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean().fillna(0)

    # Bollinger Bands Calculation
    data['Middle_Band'] = data['Close'].rolling(window=20).mean().fillna(0)
    data['Upper_Band'] = (data['Middle_Band'] + 2 * data['Close'].rolling(window=20).std()).fillna(0)
    data['Lower_Band'] = (data['Middle_Band'] - 2 * data['Close'].rolling(window=20).std()).fillna(0)

    # Buy/Sell Signals
    buy_signals = []
    sell_signals = []

    for i in range(len(data)):
        if i == 0:
            buy_signals.append(0)
            sell_signals.append(0)
        else:
            # SMA and EMA Crosses
            if data['SMA_20'][i] > data['SMA_50'][i] and data['SMA_20'][i - 1] <= data['SMA_50'][i - 1]:
                buy_signals.append(data['Close'][i])
                sell_signals.append(0)
            elif data['SMA_20'][i] < data['SMA_50'][i] and data['SMA_20'][i - 1] >= data['SMA_50'][i - 1]:
                sell_signals.append(data['Close'][i])
                buy_signals.append(0)
            # RSI
            elif data['RSI'][i] < 30:
                buy_signals.append(data['Close'][i])
                sell_signals.append(0)
            elif data['RSI'][i] > 70:
                sell_signals.append(data['Close'][i])
                buy_signals.append(0)
            # Bollinger Bands
            elif data['Close'][i] < data['Lower_Band'][i]:
                buy_signals.append(data['Close'][i])
                sell_signals.append(0)
            elif data['Close'][i] > data['Upper_Band'][i]:
                sell_signals.append(data['Close'][i])
                buy_signals.append(0)
            # MACD
            elif data['MACD'][i] > data['Signal_Line'][i] and data['MACD'][i - 1] <= data['Signal_Line'][i - 1]:
                buy_signals.append(data['Close'][i])
                sell_signals.append(0)
            elif data['MACD'][i] < data['Signal_Line'][i] and data['MACD'][i - 1] >= data['Signal_Line'][i - 1]:
                sell_signals.append(data['Close'][i])
                buy_signals.append(0)
            else:
                buy_signals.append(0)
                sell_signals.append(0)

    data['Buy_Signal'] = buy_signals
    data['Sell_Signal'] = sell_signals
    # Calculate Mean
    mean = data['Close'].mean()
    data['Mean'] = mean

    # Current values for the latest data point
    current_price = data['Close'].iloc[-1]
    ema_12 = data['EMA_12'].iloc[-1]
    ema_26 = data['EMA_26'].iloc[-1]
    ema_50 = data['EMA_50'].iloc[-1]
    ema_200 = data['EMA_200'].iloc[-1]
    macd_value = data['MACD'].iloc[-1]
    macd_signal = data['MACD_Signal'].iloc[-1]
    stoch_k = data['%K'].iloc[-1]
    stoch_d = data['%D'].iloc[-1]
    mean = data['Mean'].iloc[-1]
    buy_flag=True

    # data['trend'] = np.where((data['Close'] > data['EMA_12']) & (data['MACD'] > data['MACD_Signal']), 'Uptrend','Uncertain')
    data['trend_signal'] = data.apply(trend_signal_compare, axis=1)
    data['stoch_signal'] = data.apply(stoch_signal_compare, axis=1)
    data['mean_reversion'] = data.apply(mean_reversion_compare, axis=1)
    data['long_term_trend'] = data.apply(long_trend_compare, axis=1)

    return data


def get_ticker_trend(ticker):
    # Load your stock price data into a DataFrame
    data = yf.download(ticker, period="2y", interval="1d")
    data = yf.download(ticker, start="2024-06-06", end="2024-06-07", interval="1m")
    if len(data) == 0:
        return

    # Calculate EMA
    data['EMA_12'] = ta.ema(data['Close'], length=12)
    data['EMA_26'] = ta.ema(data['Close'], length=26)
    data['EMA_50'] = ta.ema(data['Close'], length=50)
    data['EMA_200'] = ta.ema(data['Close'], length=200)

    # Calculate MACD
    macd = ta.macd(data['Close'], fast=12, slow=26, signal=9)
    data['MACD'] = macd['MACD_12_26_9']
    data['MACD_Signal'] = macd['MACDs_12_26_9']

    # Calculate Stochastic Oscillator
    stoch = ta.stoch(data['High'], data['Low'], data['Close'], k=14, d=3)
    data['%K'] = stoch['STOCHk_14_3_3']
    data['%D'] = stoch['STOCHd_14_3_3']

    # Calculate Mean
    data['Mean'] = data['Close'].rolling(window=200).mean()

    # Current values for the latest data point
    current_price = data['Close'].iloc[-1]
    ema_12 = data['EMA_12'].iloc[-1]
    ema_26 = data['EMA_26'].iloc[-1]
    ema_50 = data['EMA_50'].iloc[-1]
    ema_200 = data['EMA_200'].iloc[-1]
    macd_value = data['MACD'].iloc[-1]
    macd_signal = data['MACD_Signal'].iloc[-1]
    stoch_k = data['%K'].iloc[-1]
    stoch_d = data['%D'].iloc[-1]
    mean = data['Mean'].iloc[-1]
    buy_flag=True

    # Analysis based on indicators
    if current_price > ema_12 and macd_value > macd_signal:
        trend = "Uptrend likely to continue"
    elif current_price < ema_26 and macd_value < macd_signal:
        trend = "Downtrend likely to continue"
        buy_flag=False
    else:
        trend = "Trend is uncertain"

    if stoch_k > 80 and stoch_d > 80:
        stoch_signal = "Stock is overbought, potential for reversal downward"
    elif stoch_k < 20 and stoch_d < 20:
        stoch_signal = "Stock is oversold, potential for reversal upward"
        buy_flag=False
    else:
        stoch_signal = "No strong reversal signal from Stochastic Oscillator"

    if current_price > mean:
        mean_reversion = "Price is above the mean, potential for downward correction"
        buy_flag=False
    elif current_price < mean:
        mean_reversion = "Price is below the mean, potential for upward correction"
    else:
        mean_reversion = "Price is at the mean, no strong mean reversion signal"

    # Long-term trend analysis using EMA 50 and EMA 200
    if ema_50 > ema_200:
        long_term_trend = "Long-term uptrend"
    elif ema_50 < ema_200:
        buy_flag=False
        long_term_trend = "Long-term downtrend"
    else:
        long_term_trend = "Long-term trend is uncertain"

    # Combined analysis
    print(f"Ticker: {ticker}")
    print(f"Trend Analysis: {trend}")
    print(f"Stochastic Oscillator Analysis: {stoch_signal}")
    print(f"Mean Reversion Analysis: {mean_reversion}")
    print(f"Long-term Trend Analysis: {long_term_trend}")

    # Example output for further actions or insights
    if trend == "Uptrend likely to continue" and stoch_signal != "Stock is overbought, potential for reversal downward":
        print("Consider holding or buying the stock.")
    elif trend == "Downtrend likely to continue" and stoch_signal != "Stock is oversold, potential for reversal upward":
        print("Consider selling or shorting the stock.")
    elif mean_reversion == "Price is above the mean, potential for downward correction":
        print("Be cautious of a potential downward correction.")
    elif mean_reversion == "Price is below the mean, potential for upward correction":
        print("Be cautious of a potential upward correction.")

    # Consider long-term trend in decision making
    if long_term_trend == "Long-term uptrend" and trend == "Uptrend likely to continue":
        print("The stock is in a strong uptrend.")
    elif long_term_trend == "Long-term downtrend" and trend == "Downtrend likely to continue":
        print("The stock is in a strong downtrend.")

    if buy_flag:
        print('consider the stock '+ticker+' to buy')

index_tickers=['TECL','SOXL','TQQQ','QQQ','DIA','SPY']
custom_tickers=['NVDA','ORCL','ILMN','HPE','AVGO','ADSK']
index_tickers = custom_tickers+index_tickers
index_tickers = custom_tickers
index_ticker_data_dict={}
for ticker in index_tickers:
    data=get_hist_data(ticker)
    data['ticker']=ticker
    if len(data)==0:
        continue
    dataResult = data.sort_values(by=['Quarterly % Change','Monthly % Change','Weekly % Change','Daily Change'], ascending=False)
    index_ticker_data_dict[ticker]=data
    print(ticker,'size=> ',len(data),'size(>0.75)=> ',len(data[data['Daily Change']>0.75]),
          'size(>0.25)=> ',len(data[data['Daily Change']>0.25]),'size(>0)=> ',len(data[data['Daily Change']>0]),
          'size(<0)=> ',len(data[data['Daily Change']<0]))
    print(data['Close'][len(data)-1],data['Close'][0],((data['Close'][len(data)-1]-data['Close'][0])/data['Close'][0])*100)
    print(data.tail(10))
    # print(data.head(10))
