import pandas as pd
import pandas_ta as ta
import yfinance as yf
from newsapi import NewsApiClient
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download NLTK VADER lexicon
import nltk

nltk.download('vader_lexicon')

# Fetch stock data for the last 200 days
ticker = 'NVDA'
company='NVDA'
data = yf.download(ticker, period='200d')

# Initialize the NewsAPI client
newsapi = NewsApiClient(api_key='707377e9e3104972a687c5b9288514c0')

# Fetch recent news articles related to the stock
articles = newsapi.get_everything(q=company, sort_by='publishedAt', language='en')

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()


# Function to analyze the sentiment of a text
def analyze_sentiment(text):
    sentiment = analyzer.polarity_scores(text)
    return sentiment


# Analyze the sentiment of the fetched articles
sentiments = []
for article in articles['articles']:  # Analyze the first 20 articles
    if 'content' in article and article['content'] is not None:
        sentiment = analyze_sentiment(article['content'])
        sentiments.append(sentiment)

# Average sentiment scores
avg_sentiment = {
    'neg': sum([s['neg'] for s in sentiments]) / len(sentiments),
    'neu': sum([s['neu'] for s in sentiments]) / len(sentiments),
    'pos': sum([s['pos'] for s in sentiments]) / len(sentiments),
    'compound': sum([s['compound'] for s in sentiments]) / len(sentiments)
}

print("Average Sentiment Scores:", avg_sentiment)

# Calculate technical indicators
data['EMA_Short'] = ta.ema(data['Close'], length=12)  # Short-term EMA
data['EMA_Long'] = ta.ema(data['Close'], length=26)  # Long-term EMA
data['RSI'] = ta.rsi(data['Close'], length=14)  # RSI
bbands = ta.bbands(data['Close'], length=20, std=2)  # Bollinger Bands
data = data.join(bbands)
macd = ta.macd(data['Close'])  # MACD
data = data.join(macd)


# Define a strategy combining Bollinger Bands, RSI, MACD, EMA, and sentiment
def buy_sell_signals(data, avg_sentiment, threshold_compound=0.05, threshold_pos=0.05, threshold_neg=0.05):
    buy_signals = []
    sell_signals = []
    neu_signals = []

    for i in range(len(data)):
        buy_condition = (
                avg_sentiment['compound'] > threshold_compound and
                avg_sentiment['pos'] > threshold_pos and
                data['Close'][i] < data['BBL_20_2.0'][i] and
                data['RSI'][i] < 30 and
                data['EMA_Short'][i] > data['EMA_Long'][i] and
                data['MACD_12_26_9'][i] > data['MACDs_12_26_9'][i]
        )

        sell_condition = (
                avg_sentiment['compound'] < -threshold_compound and
                avg_sentiment['neg'] > threshold_neg and
                data['Close'][i] > data['BBU_20_2.0'][i] and
                data['RSI'][i] > 70 and
                data['EMA_Short'][i] < data['EMA_Long'][i] and
                data['MACD_12_26_9'][i] < data['MACDs_12_26_9'][i]
        )

        neu_condition = (
                avg_sentiment['compound'] < -threshold_compound and
                avg_sentiment['neu'] > threshold_neg and
                data['Close'][i] > data['BBU_20_2.0'][i] and
                data['RSI'][i] > 70 and
                data['EMA_Short'][i] < data['EMA_Long'][i] and
                data['MACD_12_26_9'][i] < data['MACDs_12_26_9'][i]
        )

        if buy_condition:
            buy_signals.append(1)  # Buy signal
            sell_signals.append(0)
            neu_signals.append(0)
        elif sell_condition:
            buy_signals.append(0)
            sell_signals.append(1)  # Sell signal
            neu_signals.append(0)
        else:
            buy_signals.append(0)
            sell_signals.append(0)
            neu_signals.append(1)

    return buy_signals, sell_signals, neu_signals


# Generate buy/sell signals
data['Buy_Signal'], data['Sell_Signal'], data['Neutral_Signal'] = buy_sell_signals(data, avg_sentiment)

# Print the latest data with signals
print("Data with Buy/Sell Signals:")
print(data.tail())

# Output the final signals
final_buy_signals = data[data['Buy_Signal'] == 1]
final_sell_signals = data[data['Sell_Signal'] == 1]
final_Neu_signals = data[data['Neutral_Signal'] == 1]

print("\nFinal Buy Signals:")
print(final_buy_signals)

print("\nFinal Sell Signals:")
print(final_sell_signals)

print("\nFinal Neutral Signals:")
print(final_Neu_signals)
