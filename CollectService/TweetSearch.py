from tweepy import OAuthHandler, API, TweepError
from Application import Tweet
from Application import _Config
from datetime import date, timedelta
from time import sleep
from random import choice
import json

day_before = date.today() - timedelta(days=1)
keywords = {}
maxTweets = 100
tweetsPerQry = 10
sinceId = None
maxId = -1
Alltweets = []


def ConfigQuery(idx):
    global keywords, maxTweets, tweetsPerQry, sinceId, maxId
    if(idx == 0):
        with open("CollectService/QuerySettings.json", "r") as json_file:
            data = json.load(json_file)
            keywords = data["keywords"]
            maxTweets = data["maxTweets"]
            tweetsPerQry = data["tweetsPerQry"]
    k = choice(list(keywords.keys()))
    sinceId = keywords[k]["sinceId"]
    maxId = keywords[k]["maxId"]
    filters = " AND -filter:replies AND -filter:retweets"
    query = k + filters
    return query, k


def updatekeywords(key):
    keywords[key]["sinceId"] = sinceId
    keywords[key]["maxId"] = maxId


def updatequerysettings():
    with open("CollectService/QuerySettings.json", "r+") as json_file:
        data = json.load(json_file)
        # Insert new data
        data["keywords"] = keywords
        json_file.seek(0)
        json.dump(data, json_file)
        json_file.truncate()


def tweet_search(api, searchQuery):
    tweetCount = 0
    tweets = []
    global maxId, sinceId
    print("Downloading max {0} tweets, starting from {1}".format(
        maxTweets, maxId))
    while tweetCount < maxTweets:
        try:
            if maxId <= 0:
                if not sinceId:
                    new_tweets = api.search(
                        q=searchQuery, count=tweetsPerQry, lang='en',
                        tweet_mode='extended', until=day_before)
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            tweet_mode='extended', lang='en',
                                            since_id=sinceId, until=day_before)
            else:
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            tweet_mode='extended', lang='en',
                                            max_id=str(maxId - 1),
                                            until=day_before)
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            tweet_mode='extended', lang='en',
                                            max_id=str(maxId - 1),
                                            until=day_before)
            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:
                t = Tweet.Tweet(tweet)
                tweets.append(t.__dict__)
            tweetCount += len(new_tweets)
            maxId = new_tweets[-1].id
            sinceId = new_tweets[0].id
        except TweepError as e:
            # Just exit if any error
            print("some error : " + str(e))
            break
        sleep(5)
    print("Downloaded {0} tweets.".format(tweetCount))
    return tweets


def SearchTweets():
    global Alltweets
    auth = OAuthHandler(_Config.consumer_key, _Config.consumer_secret)
    auth.set_access_token(_Config.access_token, _Config.access_secret)
    api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    for i in range(2):
        squery, k = ConfigQuery(i)
        print("Nb {0} Generated query is {1}".format(i, squery))
        tweets = tweet_search(api, squery)
        Alltweets.append(tweets)
        updatekeywords(k)
        sleep(10)
    updatequerysettings()
    return Alltweets
