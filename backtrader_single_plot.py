import backtrader as bt
import yfinance as yf


class CombinedStrategy(bt.Strategy):
    def __init__(self):
        # SMACrossover
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=10)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=30)

        # EMACrossover
        self.ema_short = bt.indicators.ExponentialMovingAverage(self.data.close, period=12)
        self.ema_long = bt.indicators.ExponentialMovingAverage(self.data.close, period=26)

        # RSI
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data.close, period=14)

        # Bollinger Bands
        self.bbands = bt.indicators.BollingerBands(self.data.close, period=20, devfactor=2.0)

        # MACD
        self.macd = bt.indicators.MACD(self.data.close)

        # Stochastic
        self.stochastic = bt.indicators.Stochastic(self.data, period=14, period_dfast=3, period_dslow=3)

        # ATR
        self.atr = bt.indicators.AverageTrueRange(self.data, period=14)

        # Parabolic SAR
        self.parabolic_sar = bt.indicators.ParabolicSAR(self.data)

    def next(self):
        # SMACrossover signals
        if self.sma_short > self.sma_long:
            self.buy()
        elif self.sma_short < self.sma_long:
            self.sell()

        # EMACrossover signals
        if self.ema_short > self.ema_long:
            self.buy()
        elif self.ema_short < self.ema_long:
            self.sell()

        # RSI signals
        if self.rsi < 30:
            self.buy()
        elif self.rsi > 70:
            self.sell()

        # Bollinger Bands signals
        if self.data.close < self.bbands.lines.bot:
            self.buy()
        elif self.data.close > self.bbands.lines.top:
            self.sell()

        # MACD signals
        if self.macd.macd > self.macd.signal:
            self.buy()
        elif self.macd.macd < self.macd.signal:
            self.sell()

        # Stochastic signals
        if self.stochastic.percK < 20:
            self.buy()
        elif self.stochastic.percK > 80:
            self.sell()

        # ATR signals
        if self.data.close > self.data.close[-1] + self.atr:
            self.buy()
        elif self.data.close < self.data.close[-1] - self.atr:
            self.sell()

        # Parabolic SAR signals
        if self.data.close > self.parabolic_sar:
            self.buy()
        elif self.data.close < self.parabolic_sar:
            self.sell()


# Fetch stock data
ticker = 'NVDA'
data = yf.download(ticker, period='2y',interval='1d')
datafeed = bt.feeds.PandasData(dataname=data)

# Initialize Cerebro engine
cerebro = bt.Cerebro()
cerebro.addstrategy(CombinedStrategy)
cerebro.adddata(datafeed)

# Run strategy
cerebro.run()
cerebro.plot()
