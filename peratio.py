import yfinance as yf
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np


# Function to fetch stock data
def fetch_financial_data(ticker, start, end):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start, end=end)

    # Fetch additional financial data
    forward_pe = stock.info.get('forwardPE')
    revenue = stock.info.get('totalRevenue')
    peg_ratio = stock.info.get('pegRatio')

    # Create a DataFrame for simplicity
    financial_data = pd.DataFrame({
        'Date': df.index,
        'Forward_PE': forward_pe,
        'PEG_Ratio': peg_ratio,
        'Revenue': revenue,
        'Stock_Price': df['Close']
    })

    # Repeat the values to match the length of the historical data
    financial_data['Forward_PE'] = forward_pe
    financial_data['PEG_Ratio'] = peg_ratio
    financial_data['Revenue'] = revenue

    return financial_data


# Parameters
ticker = 'AAPL'  # Change to 'NVDA' for NVIDIA stock
start_date = '2020-01-01'
end_date = '2023-01-01'

# Fetch financial data
financial_data = fetch_financial_data(ticker, start_date, end_date)

# Drop rows with any missing values
financial_data.dropna(inplace=True)

# Features and target variable
X = financial_data[['Forward_PE', 'PEG_Ratio', 'Revenue']]
y = financial_data['Stock_Price']

# Splitting the dataset into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Training the Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Predicting stock prices
y_pred = model.predict(X_test)

# Calculating the mean squared error
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')

# Displaying predicted and actual prices
predictions = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
print(predictions)

# Predicting future stock price
future_forward_pe = 30  # Example forward P/E ratio
future_peg_ratio = 1.5  # Example PEG ratio
future_revenue = 100e9  # Example revenue

future_data = np.array([[future_forward_pe, future_peg_ratio, future_revenue]])
predicted_price = model.predict(future_data)

print(f'Predicted Stock Price: {predicted_price[0]:.2f}')
