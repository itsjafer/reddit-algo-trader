[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/itsjafer/reddit-trending-stocks-index)

# Reddit Stock Trader (WIP)

![screenshot1](https://i.imgur.com/gJ7TqcV.png)
![screenshot2](https://i.imgur.com/9EmrOJz.png)

This package contains two modules:
1. StockAnalysis - a module that looks through a subreddit for the most commonly mentioned stocks
2. AlpacaTrader - a high frequency trading module that uses the results from StockAnalysis to make trades

In particular, AlpacaTrader queries the top 10 most commonly mentioned stocks on reddit as often as possible, and rebalances its portfolio accordingly. Whenever a stock leaves the top 10, AlpacaTrader closes its position on that stock. Whenever a stock enters the top 10, AlpacaTrader opens a position for that stock.

Right now, this is a _very_ rudimentary package and is not intended for public use.

## Prerequisites
* [Alpaca](https://alpaca.markets) account with an API key pair
* Reddit account with an API key pair

## Changelog

* 0.1 - Initial commit; basic trading should theoretically work but hasn't been tested on a live market

## TODO

* Add sentiment analysis as part of a comprehensive score for stocks rather than simply occurrences
* Add filters for types of stock to avoid purchasing (i.e. specific countries/industries)
* Test on a live market scenario
* Add a non-daytrade strategy of buying and holding once a day
