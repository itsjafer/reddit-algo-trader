[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/itsjafer/reddit-trending-stocks-index)

# Reddit Stock Trader

![screenshot1](https://i.imgur.com/jcUoc4w.png)
![screenshot2](https://i.imgur.com/9EmrOJz.png)

This package contains two modules:
1. StockAnalysis - a module that looks through a subreddit for the most commonly mentioned stocks
2. AlpacaTrader - a high frequency trading module that uses the results from StockAnalysis to make trades

In particular, AlpacaTrader queries the top 10 most commonly mentioned stocks on reddit as often as possible, and rebalances its portfolio accordingly. Whenever a stock leaves the top 10, AlpacaTrader closes its position on that stock. Whenever a stock enters the top 10, AlpacaTrader opens a position for that stock.

## Live Demo

I've been paper testing this using the Alpaca API. If you'd like to take a look at the performance of the algorithm, [check out the front-end on my website](https://itsjafer.com/#/trader)!

## Prerequisites
* [Alpaca](https://alpaca.markets) account with an API key pair
* Reddit account with an API key pair

## Changelog

* 0.1 - Initial commit; basic trading should theoretically work but hasn't been tested on a live market
* 0.2 - Fixed trading logic; currently runs on a live paper market as expected.
* 1.0 - Added a second algorithm based on sentiment, created a front-end to track the algorithms

## TODO

* Add filters for types of stock to avoid purchasing (i.e. specific countries/industries)
* Test on a live market scenario
* Add a non-daytrade strategy of buying and holding once a day

## Development

* I coded this entire project on my iPad using gitpod.io!
* You can get the project running by opening it in a gitpod IDE by clicking here: [![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/itsjafer/reddit-trending-stocks-index)
* Run `make setup` followed by `make run_trader` or `make run_analysis` depending on which module you'd like to run. Remember to fill in credentials details for the corresponding module
