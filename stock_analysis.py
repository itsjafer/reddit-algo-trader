import praw
import yfinance as yf
import collections

UPVOTE_RATIO = 0.70
UPVOTES = 5

def main():

    reddit = praw.Reddit(
        user_agent = "Comment Extraction",
        client_id="",
        client_secret="",
        username="",
        password=""
    )

    subreddit = reddit.subreddit("robinhoodpennystocks")
    sortedByHot = subreddit.hot()

    numPosts, tickers = 0, collections.defaultdict(int)
    for submission in sortedByHot:
        if submission.upvote_ratio < UPVOTE_RATIO or submission.ups < UPVOTES:
            continue 

        authors = set()
        comments = submission.comments
        numPosts += 1

        submission.comments.replace_more(limit=0)
        for comment in comments:
            if comment.score < UPVOTES:
                continue 

            try:
                commentAuthor = comment.author.name
            except:
                pass

            if commentAuthor in authors:
                continue

            for word in comment.body.split(" "):
                word = word.replace("$", "")
                if not word.isupper() or len(word) > 5:
                    continue
                ticker = yf.Ticker(word)
                try:
                    ticker.info
                except:
                    print(f"Ticker {ticker} does not exist")
                    continue

                authors.add(commentAuthor)
                print(word)
                tickers[word] += 1

                




        



if __name__ == "__main__":
    main()