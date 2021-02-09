# This file contains the logic for performing trades based on
# the info from our subreddits


# 1. We start by waiting for market open
# 2. We close all open orders
# 3. We rebalance our portfolio based on reddit
# 4. Rinse and repeat every minute or so 

import alpaca_trade_api as tradeapi
import stock_analysis
import threading
import time
import datetime
import collections
import os
from dotenv import load_dotenv
from pathlib import Path

class AlpacaTrader:
    def __init__(self, subreddit, limit):
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)
        self.limit = limit
        self.subreddit = subreddit
        self.init()

    def init(self):
        self.alpaca = tradeapi.REST(
            os.getenv("ACCESS_KEY_ID"),
            os.getenv("SECRET_ACCESS_KEY"),
            base_url="https://paper-api.alpaca.markets"
        )
        self.equity = None
        self.blacklist = set()
        self.qBuying = None
        self.positions = None 
        self.adjustedQBuying = None

    def run(self):
        # First, cancel any existing orders so they don't impact our buying power.
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
            self.alpaca.cancel_order(order.id)

        # Wait for market to open.
        print("Waiting for market to open...")
        tAMO = threading.Thread(target=self.awaitMarketOpen)
        tAMO.start()
        tAMO.join()
        print("Market opened.")

        # Rebalance the portfolio as much as we can
        # Rebalance the portfolio.
        tRebalance = threading.Thread(target=self.rebalance)
        tRebalance.start()
        tRebalance.join()

    def rebalance(self):
        tRerank = threading.Thread(target=self.rerank)
        tRerank.start()
        tRerank.join()

        # Clear existing orders again.
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
            self.alpaca.cancel_order(order.id)
        
        print("We are going to keep the following positions: " + str(self.positions))

        executed = []
        positions = self.alpaca.list_positions()

        self.blacklist.clear()
        for position in positions:
            # Remove positions that are no longer in the positions set
            if position.symbol not in self.positions:
                # Sell the position
                respSO = []
                tSO = threading.Thread(target=self.submitOrder, args=[int(position.qty), position.symbol, "sell", respSO])
                tSO.start()
                tSO.join()
            else:
                # print(f"We are keeping {position.symbol}")
                if (int(position.qty) == int(self.qBuying[position.symbol])):
                    # print(f"We already have the correct amount of shares for {position.symbol}. Skipping.")
                    pass
                else:
                    # Need to adjust position amount
                    diff = int(self.qBuying[position.symbol]) - int(float(position.qty))
                    print(f"Adjusting position amount for {position.symbol} from {position.qty} to {self.qBuying[position.symbol]}.")
                    if (diff > 0):
                        side = "buy"
                    else:
                        side = "sell"
                    respSO = []
                    tSO = threading.Thread(target=self.submitOrder, args=[abs(diff), position.symbol, side, respSO])
                    tSO.start()
                    tSO.join()
                executed.append(position.symbol)
                self.blacklist.add(position.symbol)
            
        # submit the orders to be executed
        respSendBO = []
        tSendBO = threading.Thread(target=self.sendBatchOrder, args=[self.qBuying, self.positions, "buy", respSendBO])
        tSendBO.start()
        tSendBO.join()
        respSendBO[0][0] += executed

        # find out which orders didn't get completed
        respGetTP = collections.defaultdict(int)
        if (len(respSendBO[0][1]) > 0):
            print("Some orders were not completed successfully. Retrying.")
            tGetTP = threading.Thread(target=self.getTotalPrice, args=[respSendBO[0][0], respGetTP])
            tGetTP.start()
            tGetTP.join()
        
        # resubmit orders that were not completed
        for stock in respSendBO[0][1]:
            qty = self.qBuying[stock]
            respResendBO = []
            tResendBO = threading.Thread(target=self.submitOrder, args=[qty, stock, "buy", respResendBO])
            tResendBO.start()
            tResendBO.join()

        self.qBuying.clear()
            
    def rerank(self):
        tRank = threading.Thread(target=self.rank)
        tRank.start()
        tRank.join()

        # figure out how many shares to buy of each stock
        self.equity = int(float(self.alpaca.get_account().equity))
        self.equityPerStock = int(self.equity // len(self.positions))

        respGetTP = collections.defaultdict(int)
        tGetTP = threading.Thread(target=self.getTotalPrice, args=[self.positions, respGetTP])
        tGetTP.start()
        tGetTP.join()

        self.qBuying = respGetTP

    def getTotalPrice(self, positions, resp):
        for stock in positions:
            bars = self.alpaca.get_barset(stock, "minute", 1)
            resp[stock] = int(self.equityPerStock // bars[stock][0].c)

    def rank(self):
        tGetPC = threading.Thread(target=self.getTickers)
        tGetPC.start()
        tGetPC.join()

    def getTickers(self):
        # the core ranking mechanism, reddit popularity
        stockAnalysis = stock_analysis.StockAnalysis(self.limit)
        scraped_tickers, numPosts = stockAnalysis.getTickersFromSubreddit(self.subreddit)
        top_tickers = dict(sorted(scraped_tickers.items(), key=lambda x: x[1], reverse = True))
        ticker_set = set(list(top_tickers)[0:10])
        self.positions = ticker_set

    def sendBatchOrder(self, qty, stocks, side, resp):
        executed = []
        incomplete = []
        for stock in stocks:
            if(self.blacklist.isdisjoint({stock})):
                respSO = []
                tSubmitOrder = threading.Thread(target=self.submitOrder, args=[qty[stock], stock, side, respSO])
                tSubmitOrder.start()
                tSubmitOrder.join()
                if(not respSO[0]):
                    # Stock order did not go through, add it to incomplete.
                    incomplete.append(stock)
                else:
                    executed.append(stock)
                respSO.clear()
        resp.append([executed, incomplete])

    # Submit an order if quantity is above 0.
    def submitOrder(self, qty, stock, side, resp):
        if(qty > 0):
            try:
                self.alpaca.submit_order(stock, qty, side, "market", "day")
                print("Market order of | " + str(qty) + " " + stock + " " + side + " | completed.")
                resp.append(True)
            except:
                print("Market Order of | " + str(qty) + " " + stock + " " + side + " | did not go through.")
                resp.append(False)
        else:
            print("Market Order of | " + str(qty) + " " + stock + " " + side + " | not completed.")
            resp.append(True) 

    def awaitMarketOpen(self):
        isOpen = self.alpaca.get_clock().is_open
        while(not isOpen):
            clock = self.alpaca.get_clock()
            openingTime = clock.next_open.replace(tzinfo=datetime.timezone.utc).timestamp()
            currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
            timeToOpen = int((openingTime - currTime) / 60)
            print(str(timeToOpen) + " minutes til market open.")
            time.sleep(60)
            isOpen = self.alpaca.get_clock().is_open

if __name__ == "__main__":
    startTime = time.time()
    alpacaTrader = AlpacaTrader("robinhoodpennystocks+pennystocks+wallstreetbets", 10000)
    alpacaTrader.run()
    print(f"This took {(time.time() - startTime)/60} minutes")
