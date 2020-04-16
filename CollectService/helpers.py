from . import Tweet


def Format(nested_list):
    New_Tweets = []
    for Itr in nested_list:
        for tweetdict in Itr:
            NewTweet = Tweet.Tweet(tweetdict, 'PostProcessing')
            New_Tweets.append(NewTweet)
    return New_Tweets


def calcScore(TweetObject):
    # tweet.favs, statuscnt, followers, friends, inlists, seniority
    return 0
