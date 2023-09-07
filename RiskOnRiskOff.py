import pandas_datareader.data as web
import pandas as pd
from backtesting import Strategy, Backtest
from backtesting.lib import crossover

BILDF = web.DataReader('BIL', 'stooq')
BNDDF = web.DataReader('BND', 'stooq')
QQQDF = web.DataReader('QQQ', 'stooq')
UPRODF = web.DataReader('UPRO', 'stooq')
EIFDF = web.DataReader('EIF', 'stooq')


def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()

def CumRet(values, n):
    """
    Return the cumulative return of `values`, over the last 
    n days.
    """
    return pd.Series(values).rolling(n).apply(lambda x: x[-1]/x[0])


class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 10
    n2 = 20
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
    
    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()

class RiskOnRiskOff(Strategy):  
    # define the lookback period as a class variable
    lookback = 60

    def init(self, test):
        super().init()
        print(test)
        # compute the cumulative 60 day returns of bnd and bil
        self.bnd_cumret = self.I(CumRet, BNDDF.data.Close, self.lookback)
        self.bil_cumret = self.I(CumRet, BILDF.data.Close, self.lookback)
        print(self.bnd_cumret, self.bil_cumret)

    def next(self):
        if self.bnd_cumret > self.bil_cumret:
            self.position.close()
            self.buy()
        else:
            self.position.close()
            self.sell()





bt = Backtest(UPRODF, RiskOnRiskOff, cash=10000, commission=.002, test='test')
stats = bt.run()
print(stats)
bt.plot()
