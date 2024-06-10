import backtrader as bt
import yfinance as yf
import pandas as pd


# Define a custom data feed to include fundamental data
class FundamentalData(bt.feeds.PandasData):
    lines = ('earnings', 'revenue', 'pe',)
    params = (
        ('earnings', -1),
        ('revenue', -1),
        ('pe', -1),
    )


class CombinedStrategy(bt.Strategy):
    params = (
        ('sma_short_period', 10),
        ('sma_long_period', 30),
        ('ema_short_period', 12),
        ('ema_long_period', 26),
        ('rsi_period', 14),
        ('bollinger_period', 20),
        ('bollinger_devfactor', 2.0),
        ('stochastic_period', 14),
        ('stochastic_dfast', 3),
        ('stochastic_dslow', 3),
        ('atr_period', 14),
    )

    def __init__(self):
        # SMACrossover
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_short_period)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_long_period)

        # EMACrossover
        self.ema_short = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.ema_short_period)
        self.ema_long = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.ema_long_period)

        # RSI
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data.close, period=self.params.rsi_period)

        # Bollinger Bands
        self.bbands = bt.indicators.BollingerBands(self.data.close, period=self.params.bollinger_period,
                                                   devfactor=self.params.bollinger_devfactor)

        # MACD
        self.macd = bt.indicators.MACD(self.data.close)

        # Stochastic
        self.stochastic = bt.indicators.Stochastic(self.data, period=self.params.stochastic_period,
                                                   period_dfast=self.params.stochastic_dfast,
                                                   period_dslow=self.params.stochastic_dslow)

        # ATR
        self.atr = bt.indicators.AverageTrueRange(self.data, period=self.params.atr_period)

        # Parabolic SAR
        self.parabolic_sar = bt.indicators.ParabolicSAR(self.data)

    def next(self):
        # Technical Signals
        tech_buy_signals = [
            self.sma_short > self.sma_long,
            self.ema_short > self.ema_long,
            self.rsi < 30,
            self.data.close < self.bbands.lines.bot,
            self.macd.macd > self.macd.signal,
            self.stochastic.percK < 20,
            self.data.close > self.data.close[-1] + self.atr,
            self.data.close > self.parabolic_sar,
        ]

        tech_sell_signals = [
            self.sma_short < self.sma_long,
            self.ema_short < self.ema_long,
            self.rsi > 70,
            self.data.close > self.bbands.lines.top,
            self.macd.macd < self.macd.signal,
            self.stochastic.percK > 80,
            self.data.close < self.data.close[-1] - self.atr,
            self.data.close < self.parabolic_sar,
        ]

        # Debugging Statements to Check Fundamental Data Access
        try:
            earnings = self.data.earnings[0]
            revenue = self.data.revenue[0]
            pe_ratio = self.data.pe[0]
            print(f"Earnings: {earnings}, Revenue: {revenue}, P/E: {pe_ratio}")
        except IndexError:
            print("Fundamental data indexing issue.")
        except Exception as e:
            print(f"Unexpected error: {e}")

        fundamental_buy_signals = [
            earnings > self.data.earnings[-1],
            revenue > self.data.revenue[-1],
            pe_ratio < 20  # Example threshold for P/E ratio
        ]

        fundamental_sell_signals = [
            earnings < self.data.earnings[-1],
            revenue < self.data.revenue[-1],
            pe_ratio > 30  # Example threshold for P/E ratio
        ]

        # Combining Technical and Fundamental Signals
        if all(tech_buy_signals) and all(fundamental_buy_signals):
            self.buy()
        elif all(tech_sell_signals) and all(fundamental_sell_signals):
            self.sell()


# Function to fetch fundamental data (mock example)
def get_fundamental_data(ticker):
    # Replace with actual data fetching logic
    return {
        'Earnings': [2.5, 2.7, 2.9, 3.0],  # Mock earnings per quarter
        'Revenue': [10, 11, 12, 13],  # Mock revenue per quarter
        'P/E': [18, 19, 20, 15]  # Mock P/E ratio per quarter
    }


# Fetch stock data
ticker = 'TQQQ'
data = yf.download(ticker, period='2y')

# Convert stock data index to UTC if it isn't already
if data.index.tz is None:
    data.index = data.index.tz_localize('UTC')
else:
    data.index = data.index.tz_convert('UTC')

# Fetch and process fundamental data
fundamental_data = get_fundamental_data(ticker)

# Convert fundamental data to DataFrame and localize timezone
fundamental_df = pd.DataFrame({
    'earnings': fundamental_data['Earnings'],
    'revenue': fundamental_data['Revenue'],
    'pe': fundamental_data['P/E']
}, index=pd.date_range(start='2023-01-01', periods=4, freq='Q').tz_localize('UTC'))

# Merge the price data with fundamental data
# data = data.join(fundamental_df, how='outer').fillna(method='ffill')

# Create a data feed
datafeed = FundamentalData(dataname=data)

# Initialize Cerebro engine
cerebro = bt.Cerebro()
cerebro.addstrategy(CombinedStrategy)
cerebro.adddata(datafeed)

# Run strategy
cerebro.run()
cerebro.plot()
