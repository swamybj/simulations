import backtrader as bt
import yfinance as yf

# Fetch stock data
ticker = 'AAPL'
data = yf.download(ticker, period='2y', interval='1d')
datafeed = bt.feeds.PandasData(dataname=data)

# Define various strategies

class SMACrossover(bt.Strategy):
    def __init__(self):
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=50)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=200)

    def next(self):
        if self.sma_short > self.sma_long:
            self.buy()
        elif self.sma_short < self.sma_long:
            self.sell()

class EMACrossover(bt.Strategy):
    def __init__(self):
        self.ema_short = bt.indicators.ExponentialMovingAverage(self.data.close, period=12)
        self.ema_long = bt.indicators.ExponentialMovingAverage(self.data.close, period=26)

    def next(self):
        if self.ema_short > self.ema_long:
            self.buy()
        elif self.ema_short < self.ema_long:
            self.sell()

class RSIStrategy(bt.Strategy):
    def __init__(self):
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data.close, period=200)

    def next(self):
        if self.rsi < 30:
            self.buy()
        elif self.rsi > 70:
            self.sell()

class BollingerBandsStrategy(bt.Strategy):
    def __init__(self):
        self.bbands = bt.indicators.BollingerBands(self.data.close, period=200, devfactor=2.0)

    def next(self):
        if self.data.close < self.bbands.lines.bot:
            self.buy()
        elif self.data.close > self.bbands.lines.top:
            self.sell()

class MACDStrategy(bt.Strategy):
    def __init__(self):
        self.macd = bt.indicators.MACD(self.data.close)
        self.signal = bt.indicators.MACDSignal(self.data.close)

    def next(self):
        if self.macd.macd > self.macd.signal:
            self.buy()
        elif self.macd.macd < self.macd.signal:
            self.sell()

class StochasticStrategy(bt.Strategy):
    def __init__(self):
        self.stochastic = bt.indicators.Stochastic(self.data, period=14, period_dfast=3, period_dslow=3)

    def next(self):
        if self.stochastic.percK < 20:
            self.buy()
        elif self.stochastic.percK > 80:
            self.sell()

class ATRStrategy(bt.Strategy):
    def __init__(self):
        self.atr = bt.indicators.AverageTrueRange(self.data, period=14)

    def next(self):
        if self.data.close > self.data.close[-1] + self.atr:
            self.buy()
        elif self.data.close < self.data.close[-1] - self.atr:
            self.sell()

class ParabolicSARStrategy(bt.Strategy):
    def __init__(self):
        self.parabolic_sar = bt.indicators.ParabolicSAR(self.data)

    def next(self):
        if self.data.close > self.parabolic_sar:
            self.buy()
        elif self.data.close < self.parabolic_sar:
            self.sell()

# List of strategies
strategies = [
    SMACrossover,
    EMACrossover,
    RSIStrategy,
    BollingerBandsStrategy,
    MACDStrategy,
    StochasticStrategy,
    ATRStrategy,
    ParabolicSARStrategy
]

# Run each strategy
for strategy in strategies:
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)
    cerebro.adddata(datafeed)
    print(f"Running {strategy.__name__}...")
    cerebro.run()
    cerebro.plot()
