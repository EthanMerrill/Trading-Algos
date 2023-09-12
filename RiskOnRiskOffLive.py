!pip install alpaca_trade_api
!pip install alpaca-py

import pandas_datareader.data as web
import pandas as pd
import alpaca_trade_api as alpaca

APCA_API_BASE_URL="https://paper-api.alpaca.markets"
ALPCA_PAPER_KEY = "PKIDK8BXVS07HWAKUYCS"
ALPCA_PAPER_SECRET = "zmSekWcDtkbnMVeadoHmuqCgw5edeNLgKxjIIcW6"

# Importing the API and instantiating the REST client according to our keys
from alpaca.trading.client import TradingClient
from pandas_datareader.av import AlphaVantage
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data import StockHistoricalDataClient
client = StockHistoricalDataClient(ALPCA_PAPER_KEY, ALPCA_PAPER_SECRET)


trading_client = TradingClient(AlphaVantage, ALPCA_PAPER_SECRET, paper=True)

def Orderer (symbol, quantity, buy):
  print(f'order recieved to {buy if "buy" else "sell"} {quantity} of {symbol}')
  # preparing orders
  market_order_data = MarketOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side= OrderSide.BUY if buy else OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                    )
  # Market order
  market_order = trading_client.submit_order(
                order_data=market_order_data
               )


## determines how many shares of each item in the portfolio need to be purchased given their current prices
def ShareAllocator(totalCash, portfolio_object):
  for ticker in portfolio_object:
        print(ticker, portfolio_object[ticker])
        quote = client.get_stock_latest_quote(StockLatestQuoteRequest(symbol_or_symbols=[ticker]))
        quote_price = quote[ticker].ask_price
        share_count = totalCash*portfolio_object[ticker]/quote_price
        portfolio_object[ticker] = {"%":portfolio_object[ticker], "shares":round(share_count)}

  return portfolio_object

def SellEverything(portfolio):
      # Print the quantity of shares for each position.
    for position in portfolio:

      print("Selling {} shares of {}".format(position.qty, position.symbol))
      Orderer(position.symbol, position.qty, False)

def AssetAllocator(desired_portfolio, current_positions, cash):
  #if ANY of the desired positions are already held in the account, abort
  for ticker in current_positions:
    print(ticker.symbol)
    if ticker.symbol in desired_portfolio:
      print(f'ticker {ticker.symbol} already owned! Ending')
      return
    ## Sell Everything in portfolio currently
  SellEverything(portfolio)
  # determine how many shares to purchase
  desired_portfolio = ShareAllocator(int(cash), desired_portfolio)
  for ticker in desired_portfolio:
    Orderer(ticker, conserv_portfolio[ticker]["shares"], True)

# Get historical returns for selected assets
BILDF = web.DataReader('BIL', 'stooq')
BNDDF = web.DataReader('BND', 'stooq')
QQQDF = web.DataReader('QQQ', 'stooq')
UPRODF = web.DataReader('UPRO', 'stooq')
EIFDF = web.DataReader('EIF', 'stooq')

# Calculate returns in the past 60 days for BIL
cumBIL = BILDF["Open"].iloc[0]-BILDF["Open"].iloc[60];
cumBND = BNDDF["Open"].iloc[0]-BNDDF["Open"].iloc[60];

# create the trading client
trading_client = TradingClient(ALPCA_PAPER_KEY, ALPCA_PAPER_SECRET, paper=True)
# Get a list of all of our positions.
portfolio = trading_client.get_all_positions()
account = trading_client.get_account()
print(f'60dyBND{cumBND} 60dyBIL: {cumBIL}')

if cumBND>cumBIL:
    print('Buy Signal')
    ## Buy the Aggressive stocks
    agro_portfolio = {
        "QQQ":45,
        "UPRO":45
    }
    AssetAllocator(agro_portfolio, trading_client.get_all_positions(), account.cash)

else:
    print("Sell Signal")

    ## Buy the conservative stock
    conserv_portfolio = {
        "IEF":.98
    }
    AssetAllocator(conserv_portfolio, trading_client.get_all_positions(), account.cash)


trading_client.get_all_positions()[0].symbol

