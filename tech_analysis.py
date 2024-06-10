import pandas as pd
import pandas_ta as ta
import yfinance as yf
from newsapi import NewsApiClient
from newspaper import Article
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# Download NLTK VADER lexicon
import nltk
nltk.download('vader_lexicon')

# Fetch stock data for the last 200 days
ticker = 'INTC'
company='Intel'
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
counter=0
for article in articles['articles']:  # Analyze the first 20 articles
    if 'content' in article and article['content'] is not None:
        sentiment = analyze_sentiment(article['content'])
        sentiments.append(sentiment)
        counter+=1

# Average sentiment scores
avg_sentiment = {
    'neg': sum([s['neg'] for s in sentiments]) / len(sentiments),
    'neu': sum([s['neu'] for s in sentiments]) / len(sentiments),
    'pos': sum([s['pos'] for s in sentiments]) / len(sentiments),
    'compound': sum([s['compound'] for s in sentiments]) / len(sentiments)
}

print("Average Sentiment Scores:", avg_sentiment)

# Calculate technical indicators
data['SMA'] = ta.sma(data['Close'], length=20)
data['EMA'] = ta.ema(data['Close'], length=20)
data['RSI'] = ta.rsi(data['Close'], length=14)
bbands = ta.bbands(data['Close'], length=20, std=2)
data = data.join(bbands)
macd = ta.macd(data['Close'])
data = data.join(macd)

# Define a simple strategy combining technical and sentiment analysis
def buy_sell_signals(data, avg_sentiment, threshold=0.05):
    buy_signals = []
    sell_signals = []
    for i in range(len(data)):
        if avg_sentiment['compound'] > threshold and data['EMA'][i] > data['SMA'][i] and data['RSI'][i] < 70:
            buy_signals.append(1)  # Buy signal
            sell_signals.append(0)
        elif avg_sentiment['compound'] < threshold and data['EMA'][i] < data['SMA'][i] and data['RSI'][i] > 30:
            buy_signals.append(0)
            sell_signals.append(1)  # Sell signal
        else:
            buy_signals.append(0)
            sell_signals.append(0)
    return buy_signals, sell_signals

# Generate buy/sell signals
data['Buy_Signal'], data['Sell_Signal'] = buy_sell_signals(data, avg_sentiment)

print("Data with Buy/Sell Signals:")
print(data.tail())

# Output the final signals
final_buy_signals = data[data['Buy_Signal'] == 1]
final_sell_signals = data[data['Sell_Signal'] == 1]

print("\nFinal Buy Signals:")
print(final_buy_signals)

print("\nFinal Sell Signals:")
print(final_sell_signals)