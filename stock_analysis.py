import praw
import collections
import string
import requests

class StockAnalysis:

    def __init__(self, limit):
        self.UPVOTES = 5
        self.BLACKLIST = {'I', 'ARE',  'ON', 'GO', 'NOW', 'CAN', 'UK', 'SO', 'OR', 'OUT', 'SEE', 'ONE', 'LOVE', 'U', 'STAY', 'HAS', 'BY', 'BIG', 'GOOD', 'RIDE', 'EOD', 'ELON', 'WSB', 'THE', 'A', 'ROPE', 'YOLO', 'TOS', 'CEO', 'DD', 'IT', 'OPEN', 'ATH', 'PM', 'IRS', 'FOR','DEC', 'BE', 'IMO', 'ALL', 'RH', 'EV', 'TOS', 'CFO', 'CTO', 'DD', 'BTFD', 'WSB', 'OK', 'PDT', 'RH', 'KYS', 'FD', 'TYS', 'US', 'USA', 'IT', 'ATH', 'RIP', 'BMW', 'GDP', 'OTM', 'ATM', 'ITM', 'IMO', 'LOL', 'AM', 'BE', 'PR', 'PRAY', 'PT', 'FBI', 'SEC', 'GOD', 'NOT', 'POS', 'FOMO', 'TL;DR', 'EDIT', 'STILL', 'WTF', 'RAW', 'PM', 'LMAO', 'LMFAO', 'ROFL', 'EZ', 'RED', 'BEZOS', 'TICK', 'IS', 'PM', 'LPT', 'GOAT', 'FL', 'CA', 'IL', 'MACD', 'HQ', 'OP', 'PS', 'AH', 'TL', 'JAN', 'FEB', 'JUL', 'AUG', 'SEP', 'SEPT', 'OCT', 'NOV', 'FDA', 'IV', 'ER', 'IPO', 'MILF', 'BUT', 'SSN', 'FIFA', 'USD', 'CPU', 'AT', 'GG', 'Mar' }
        self.UPVOTE_RATIO = 0.70 
        self.reddit = praw.Reddit(
            user_agent = "",
            client_id="",
            client_secret="",
            username="",
            password=""
        )
        self.limit = limit

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
        sortedByHot = subreddit.hot(limit=32)
        allTickers = self.getAllTickers()
        numPosts, tickers = 0, collections.defaultdict(int)
        for submission in sortedByHot:
            if submission.upvote_ratio < self.UPVOTE_RATIO or submission.ups < self.UPVOTES:
                continue 
        
            authors = set()
            submission.comment_sort = "new"
            comments = submission.comments
            numPosts += 1

            submission.comments.replace_more(self.limit)
            for comment in comments:
                try:
                    commentAuthor = comment.author.name
                    if comment.score < self.UPVOTES or commentAuthor in authors:
                        continue
                except: # if the author wasn't found, or no score available 
                    continue

                for word in comment.body.split(" "):
                    word = word.replace("$", "")
                    word = word.translate(str.maketrans('', '', string.punctuation))
                    if (not word.isupper()) or len(word) > 5 or word in self.BLACKLIST or word not in allTickers:
                        continue
                    authors.add(commentAuthor)
                    tickers[word] += 1

        return tickers, numPosts



if __name__ == "__main__":
    stockAnalysis = StockAnalysis(5)

    subreddits = [
        "wallstreetbets",
        "robinhoodpennystocks+pennystocks",
        "stocks+investing"
    ]

    for subreddit in subreddits:
        scraped_tickers, numPosts = stockAnalysis.getTickersFromSubreddit(subreddit)
        top_tickers = dict(sorted(scraped_tickers.items(), key=lambda x: x[1], reverse = True))
        print(f"Scraped {numPosts} posts in {subreddit}")
        print("Ticker: occurrences")
        ticker_list = list(top_tickers)[0:10]
        for ticker in ticker_list:
            print(f"{ticker}: {top_tickers[ticker]}")