import yfinance as yf
import numpy as np
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
import matplotlib.pyplot as plt
from io import BytesIO
from kivy.graphics.texture import Texture

# Function to calculate MACD
def calculate_macd(price_data, short_window=12, long_window=26, signal_window=9):
    # Calculate short-term EMA
    short_ema = price_data.ewm(span=short_window, adjust=False).mean()

    # Calculate long-term EMA
    long_ema = price_data.ewm(span=long_window, adjust=False).mean()

    # Calculate MACD line
    macd_line = short_ema - long_ema

    # Calculate signal line
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()

    # Calculate MACD histogram
    macd_histogram = macd_line - signal_line

    return macd_line, signal_line, macd_histogram


# Function to calculate EMA
def calculate_ema(price_data, window_size):
    ema_data = price_data.ewm(span=window_size, adjust=False).mean()
    return ema_data


def calculate_bollinger_bands(price_data, window_size=20, num_std=2):
    # Calculate rolling mean and standard deviation
    rolling_mean = price_data.rolling(window=window_size).mean()
    rolling_std = price_data.rolling(window=window_size).std()

    # Calculate upper and lower bands
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)

    return upper_band, lower_band


# Function to calculate Stochastic Oscillator
def calculate_stochastic_oscillator(price_data, window_size=14):
    try:
        # Calculate highest high and lowest low over the window
        high_max = price_data.rolling(window=window_size).max()
        low_min = price_data.rolling(window=window_size).min()

        # Calculate %K
        percent_k = ((price_data - low_min) / (high_max - low_min)) * 100

        # Calculate %D (3-period moving average of %K)
        percent_d = percent_k.rolling(window=3).mean()

        return percent_k, percent_d
    except Exception as e:
        print("Error calculating Stochastic Oscillator:", e)
        return None, None


# Function to calculate mean reversion
def calculate_mean_reversion(price_data, window_size=20):
    # Calculate rolling mean over the window
    rolling_mean = price_data.rolling(window=window_size).mean()

    # Calculate mean reversion signal
    mean_reversion_signal = (price_data - rolling_mean) / rolling_mean

    return mean_reversion_signal


# Function to calculate Fibonacci levels
def calculate_fibonacci_levels(price_data):
    # Get the highest high and lowest low prices
    high_max = price_data.max()
    low_min = price_data.min()

    # Calculate the range
    price_range = high_max - low_min

    # Fibonacci levels
    fibonacci_levels = {
        0.236: low_min + 0.236 * price_range,
        0.382: low_min + 0.382 * price_range,
        0.5: low_min + 0.5 * price_range,
        0.618: low_min + 0.618 * price_range,
        1.0: high_max
    }

    return fibonacci_levels

# Main App Class
class TradingApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical')

        # Add UI components for input (ticker, parameters)
        self.ticker_input = TextInput(hint_text='Enter Ticker Symbol')
        self.short_window_input = TextInput(hint_text='Short Window')
        self.long_window_input = TextInput(hint_text='Long Window')
        self.signal_window_input = TextInput(hint_text='Signal Window')
        self.fetch_button = Button(text='Fetch Data', on_press=self.fetch_data)
        self.root.add_widget(self.ticker_input)
        self.root.add_widget(self.short_window_input)
        self.root.add_widget(self.long_window_input)
        self.root.add_widget(self.signal_window_input)
        self.root.add_widget(self.fetch_button)

        return self.root

    # Function to fetch data and calculate signals
    def fetch_data(self, instance):

        ticker = self.ticker_input.text
        short_window_text = self.short_window_input.text

        # Perform input validation for short_window
        if not short_window_text:
            print("Short window input is empty. Using default value.")
            short_window = 12  # Default value
        else:
            try:
                short_window = int(short_window_text)
            except ValueError:
                print("Invalid input for short window. Using default value.")
                short_window = 12  # Default value

        # Continue with your data fetching and processing
        try:
            price_data = yf.download(ticker, start='2023-01-01', end='2024-01-01')['Adj Close']
            if isinstance(price_data, tuple):
                raise ValueError("Error fetching price data. Received tuple instead of expected pandas DataFrame.")

            # Calculate strategies using short_window
            macd_line, signal_line, macd_histogram = calculate_macd(price_data, short_window)
            if isinstance(macd_line, tuple) or isinstance(signal_line, tuple) or isinstance(macd_histogram, tuple):
                raise ValueError("Error calculating MACD. Received tuple instead of expected pandas Series.")

            ema_data = calculate_ema(price_data, short_window)
            if isinstance(ema_data, tuple):
                raise ValueError("Error calculating EMA. Received tuple instead of expected pandas Series.")

            upper_band, lower_band = calculate_bollinger_bands(price_data, window_size=short_window)
            if isinstance(upper_band, tuple) or isinstance(lower_band, tuple):
                raise ValueError("Error calculating Bollinger Bands. Received tuple instead of expected pandas Series.")

            stochastic_oscillator = calculate_stochastic_oscillator(price_data, window_size=short_window)[0]
            if isinstance(stochastic_oscillator, tuple):
                raise ValueError(
                    "Error calculating Stochastic Oscillator. Received tuple instead of expected pandas Series.")

            mean_reversion_signal = calculate_mean_reversion(price_data, window_size=short_window)
            if isinstance(mean_reversion_signal, tuple):
                raise ValueError("Error calculating mean reversion. Received tuple instead of expected pandas Series.")

            fibonacci_levels = calculate_fibonacci_levels(price_data)

            # Plot data and strategies
            plt.figure(figsize=(10, 6))

            # Plot price data
            plt.plot(price_data.index, price_data.values, label='Price')

            # Plot MACD and signal line
            plt.plot(macd_line.index, macd_line.values, label='MACD', color='blue')
            plt.plot(signal_line.index, signal_line.values, label='Signal Line', color='red')

            # Plot Bollinger Bands
            plt.plot(upper_band.index, upper_band.values, label='Upper Bollinger Band', color='green')
            plt.plot(lower_band.index, lower_band.values, label='Lower Bollinger Band', color='green')

            # Plot Stochastic Oscillator
            plt.plot(stochastic_oscillator.index, stochastic_oscillator.values, label='%K', color='purple')

            # Plot Mean Reversion Signal
            plt.plot(mean_reversion_signal.index, mean_reversion_signal.values, label='Mean Reversion Signal',
                     color='orange')

            # Customize the plot
            plt.title('Stock Price and Strategies')
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.legend()

            # Save plot to a BytesIO buffer
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)

            # Clear the current plot to avoid overlap
            plt.close()

            # Display the plot within the Kivy app using an image widget
            texture = Texture.create(size=(buf.width, buf.height), colorfmt='rgba')
            texture.blit_buffer(buf.getvalue(), colorfmt='rgba', bufferfmt='ubyte')
            self.image = Image(texture=texture)
            self.root.add_widget(self.image)
            # Display the plot within the Kivy app using an image widget
            self.image = Image(texture=buf.read())
            self.root.add_widget(self.image)

        except Exception as e:
            print("Error:", e)


if __name__ == '__main__':
    TradingApp().run()
