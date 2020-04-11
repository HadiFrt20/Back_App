from tweepy import OAuthHandler, API, TweepError
from Application import Tweet
from celery import shared_task
from Application import _Config
from celery.utils.log import get_task_logger
from datetime import date, timedelta
import random
import json

logger = get_task_logger(__name__)

day_before = date.today() - timedelta(days=1)
max_t = -1
# this is what we're searching for
searchQuery = "logistics AND -filter:replies AND -filter:retweets"
maxTweets = 1000  # Some arbitrary large number
tweetsPerQry = 100  # this is the max the API permits
fName = 'tweets.txt'  # We'll store the tweets in a text file.
sinceId = None


def gen_tquery():
    q = " "
    filters = " AND -filter:replies AND -filter:retweets"
    with open(_Config.scglossary) as json_file:
        glossary = json.load(json_file)
        cats = list(glossary.keys())
        cat = random.choice(cats)
        terms = glossary[cat]
        nb = random.randrange(len(terms))
        if nb <= 0:
            nb = 1
        chosen_terms = random.sample(terms, nb)
        q = " OR ".join(chosen_terms)
    if q == " ":
        return None
    else:
        return q+filters, cat


def tweet_search(api):
    tweetCount = 0
    global max_t
    print("Downloading max {0} tweets, starting from {1}".format(
        maxTweets, max_t))
    while tweetCount < maxTweets:
        try:
            if max_t <= 0:
                if not sinceId:
                    new_tweets = api.search(
                        q=searchQuery, count=tweetsPerQry,
                        tweet_mode='extended', until=day_before)
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            tweet_mode='extended',
                                            since_id=sinceId, until=day_before)
            else:
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            tweet_mode='extended',
                                            max_id=str(max_t - 1),
                                            until=day_before)
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            tweet_mode='extended',
                                            max_id=str(max_t - 1),
                                            since_id=sinceId, until=day_before)
            if not new_tweets:
                # print("No more tweets found")
                break
            for tweet in new_tweets:
                t = Tweet.Tweet(tweet)
                # print(tweet._json)
                print(t.__dict__)
            tweetCount += len(new_tweets)
            # print("Downloaded {0} tweets".format(tweetCount))
            max_t = new_tweets[-1].id
        except TweepError as e:
            # Just exit if any error
            print("some error : " + str(e))
            break

    print("Downloaded {0} tweets.".format(tweetCount))


# @periodic_task(run_every=crontab(minute=0, hour='16'))
@shared_task
def SearchTweets():
    auth = OAuthHandler(_Config.consumer_key, _Config.consumer_secret)
    auth.set_access_token(_Config.access_token, _Config.access_secret)
    api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    logger.info("I log!")
    tweet_search(api)
