import yfinance as yf
import pandas as pd
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

# Define the list of NASDAQ 100 tickers
nasdaq_100_tickers = getTickers()

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
    today = date.today()
    for i in range(1, len(data)):
        if today==data.index[i].date():
            if data['21_MA'][i] > data['50_MA'][i] and data['RSI'][i] < 70 and data['MACD'][i] > data['Signal'][i]:
                signals.append(f"Buy signal for {data.index[i].date()}, 21_MA:{data['21_MA'][i]}, 50_MA:{data['50_MA'][i]}, Signal:{data['Signal'][i]}, MACD:{data['MACD'][i]}, RSI:{data['RSI'][i]}")
            elif data['21_MA'][i] < data['50_MA'][i] and data['RSI'][i] > 30 and data['MACD'][i] < data['Signal'][i]:
                signals.append(f"Sell signal for {data.index[i].date()}, 21_MA:{data['21_MA'][i]}, 50_MA:{data['50_MA'][i]}, Signal:{data['Signal'][i]}, MACD:{data['MACD'][i]}, RSI:{data['RSI'][i]}")
    return signals

# Function to send email alert
def send_email(subject, body):
    sender_email = "your_email@gmail.com"
    receiver_email = "receiver_email@gmail.com"
    password = "your_password"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)

# Main script
alerts = []
for ticker in nasdaq_100_tickers:
    data = fetch_data_and_calculate_indicators(ticker)
    signals = check_trading_signals(ticker,data)
    if len(signals)!=0:
        alerts.append(f"Ticker: {ticker}\n" + "\n".join(signals) + "\n\n")
    # if signals:
    #     alerts.append(f"Ticker: {ticker}\n" + "\n".join(signals) + "\n\n")
print(alerts)
# if alerts:
#     send_email("Swing Trading Alerts", "\n".join(alerts))
# else:
#     send_email("Swing Trading Alerts", "No trading signals found.")

