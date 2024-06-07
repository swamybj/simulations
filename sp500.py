import requests
import pandas as pd

# URL of the Slickcharts page containing S&P 500 tickers
url = 'https://www.slickcharts.com/sp500'
url = 'https://www.slickcharts.com/nasdaq100/gainers'

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

# Print the tickers
print(tickers)
