import praw
import collections
import string
import requests
import os
import time
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path  # Python 3.6+ only
from pmaw import PushshiftAPI
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from reddit_lingo import reddit_lingo, blacklist

class StockAnalysis:

    def __init__(self, limit, sentiment):
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)
        self.UPVOTES = 1
        self.BLACKLIST = blacklist
        self.UPVOTE_RATIO = 0.70 
        self.reddit = praw.Reddit(
            user_agent = "Comment Extraction",
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            username=os.getenv("USERNAME"),
            password=os.getenv("PASSWORD")
        )
        self.limit = limit
        self.sentiment = sentiment
        self.vader = SentimentIntensityAnalyzer()
        self.vader.lexicon.update(reddit_lingo)
        
    def getAllTickers(self):
        URL = "https://dumbstockapi.com/stock"
        param = dict(
            format="tickers-only",
            exchanges="NYSE,NASDAQ,AMEX"
        )

        response = requests.get(url=URL, params=param)
        data = response.json()
        return set(data)

    def getTickersFromSubreddit(self, sub):
        subreddit = self.reddit.subreddit(sub)
        sortedByHot = subreddit.hot(limit=self.limit)
        allTickers = self.getAllTickers()
        numPosts = 0 
        if self.sentiment:
            tickers = collections.defaultdict(set)
        else:
            tickers = collections.defaultdict(int)
        for submission in sortedByHot:
            if submission.upvote_ratio < self.UPVOTE_RATIO or submission.ups < self.UPVOTES:
                continue 
        
            authors = set()
            submission.comment_sort = "new"
            comments = submission.comments
            if self.sentiment:
                submission.comments.replace_more(limit=None)
            numPosts += 1
            for comment in comments:
                try:
                    commentAuthor = comment.author.name
                    if comment.score < self.UPVOTES or commentAuthor in authors:
                        continue
                except: # if the author wasn't found, or no score available 
                    continue

                numPosts += 1
                for word in comment.body.split(" "):
                    word = word.replace("$", "")
                    word = word.translate(str.maketrans('', '', string.punctuation))
                    if (not word.isupper()) or len(word) > 5 or word in self.BLACKLIST or word not in allTickers:
                        continue
                    authors.add(commentAuthor)
                    if (self.sentiment):
                        tickers[word].add(self.getSentimentScore(comment.body))
                    else:
                        tickers[word] += 1

        return tickers, numPosts

    def getSentimentScore(self, comment):
        score = self.vader.polarity_scores(comment)
        return score['pos'] - score['neg']

if __name__ == "__main__":

    sentiment = True
    stockAnalysis = StockAnalysis(1000, sentiment)
    
    subreddits = [
        # "wallstreetbets",
        "robinhood+pennystocks",
        # "stocks"
    ]

    for subreddit in subreddits:
        startTime = time.time()
        scraped_tickers, numPosts = stockAnalysis.getTickersFromSubreddit(subreddit)
        if (sentiment):
            for ticker in scraped_tickers:
                if len(scraped_tickers[ticker]) <= 5:
                    scraped_tickers[ticker] = 0
                    continue
                scraped_tickers[ticker] = sum(scraped_tickers[ticker])/len(scraped_tickers[ticker])    
        
        top_tickers = dict(sorted(scraped_tickers.items(), key=lambda x: x[1], reverse = True))
        print(f"This took {(time.time() - startTime)/60} minutes")
        print(f"Scraped {numPosts} posts in {subreddit}")
        print("Ticker: score")
        ticker_list = list(top_tickers)[0:10]
        for ticker in ticker_list:
            print(f"{ticker}: {top_tickers[ticker]}")