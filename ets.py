import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from pmdarima import auto_arima
from statsmodels.tsa.stattools import adfuller

# Function to fetch stock data
def fetch_stock_data(ticker, start, end):
    stock_data = yf.download(ticker, start=start, end=end)
    return stock_data['Close']

# Function to check stationarity and difference if necessary
def make_stationary(data):
    p_value_threshold = 0.05

    def adf_test(timeseries):
        adf_test_result = adfuller(timeseries, autolag='AIC')
        return adf_test_result[1]  # p-value

    p_value = adf_test(data)
    if p_value > p_value_threshold:
        data = data.diff().dropna()
        print("Data differenced to make it stationary.")
    else:
        print("Data is already stationary.")
    return data

# Function to forecast using ARIMA
def forecast_arima(train_data, periods):
    model = auto_arima(train_data, seasonal=False, trace=True, suppress_warnings=True, error_action='ignore')
    forecast, conf_int = model.predict(n_periods=periods, return_conf_int=True)
    return forecast, conf_int

# Function to forecast using ETS
def forecast_ets(train_data, periods):
    ets_model = ExponentialSmoothing(train_data, trend='add', seasonal=None).fit()
    forecast = ets_model.forecast(steps=periods)
    return forecast

# Parameters
ticker = 'AAPL'  # Change to 'NVDA' for NVIDIA stock
start_date = '2020-01-01'
end_date = '2024-06-01'
forecast_periods = 50

# Fetch stock data
stock_data = fetch_stock_data(ticker, start_date, end_date)

# Preprocessing: Remove any missing values
stock_data.dropna(inplace=True)
print("Initial data length:", len(stock_data))

# Ensure the data is stationary
train_data = make_stationary(stock_data[:-forecast_periods])
test_data = stock_data[-forecast_periods:]

# Check for any remaining NaN values after differencing
if train_data.isna().sum() > 0:
    print("NaN values found in train data after making it stationary. Please check the data preprocessing steps.")
else:
    print("No NaN values in train data. Proceeding with forecasting.")

# Forecast using ARIMA
try:
    arima_forecast, arima_conf_int = forecast_arima(train_data, forecast_periods)
    arima_forecast_series = pd.Series(arima_forecast, index=test_data.index)
except Exception as e:
    print(f"ARIMA model fitting failed: {e}")
    arima_forecast_series = pd.Series([np.nan] * forecast_periods, index=test_data.index)

# Forecast using ETS
try:
    ets_forecast = forecast_ets(train_data, forecast_periods)
    ets_forecast_series = pd.Series(ets_forecast, index=test_data.index)
except Exception as e:
    print(f"ETS model fitting failed: {e}")
    ets_forecast_series = pd.Series([np.nan] * forecast_periods, index=test_data.index)

# Print the predicted prices
print(f"\nARIMA Model Predictions for {ticker}:\n")
for date, price in arima_forecast_series.items():
    print(f"Date: {date.date()}, Predicted Price: {price:.2f}")

print(f"\nETS Model Predictions for {ticker}:\n")
for date, price in ets_forecast_series.items():
    print(f"Date: {date.date()}, Predicted Price: {price:.2f}")

# Plot the results
plt.figure(figsize=(14, 7))

# Plot actual data
plt.plot(stock_data, label='Actual Data')
plt.plot(test_data, label='Test Data')

# Plot ARIMA forecast
plt.plot(arima_forecast_series, label='ARIMA Forecast', color='orange')
if not arima_forecast_series.isna().all():
    plt.fill_between(test_data.index, arima_conf_int[:, 0], arima_conf_int[:, 1], color='orange', alpha=0.1)

# Plot ETS forecast
plt.plot(ets_forecast_series, label='ETS Forecast', color='green')

# Customize plot
plt.title(f'{ticker} Stock Price Forecast')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()
