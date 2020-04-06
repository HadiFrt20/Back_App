from tweepy import OAuthHandler, API, TweepError
from Application import Tweet
from Application import _Config
from celery import shared_task
from celery.utils.log import get_task_logger
import jsonpickle
from datetime import date, timedelta

logger = get_task_logger(__name__)

day_before = date.today() - timedelta(days=1)
max_t = -1
searchQuery = "logistics AND -filter:replies AND -filter:retweets"  # this is what we're searching for
maxTweets = 10000000 # Some arbitrary large number
tweetsPerQry = 100  # this is the max the API permits
fName = 'tweets.txt' # We'll store the tweets in a text file.
sinceId = None

def tweet_search(api):
  tweetCount = 0
  print("Downloading max {0} tweets, starting from {1}".format(maxTweets, max_t))
  with open(fName, 'w') as f:
      while tweetCount < maxTweets:
          try:
              if max_t <= 0:
                  if not sinceId:
                      new_tweets = api.search(q=searchQuery, count=tweetsPerQry,tweet_mode='extended', until=day_before)
                  else:
                      new_tweets = api.search(q=searchQuery, count=tweetsPerQry,tweet_mode='extended',
                                              since_id=sinceId, until=day_before)
              else:
                  if (not sinceId):
                      new_tweets = api.search(q=searchQuery, count=tweetsPerQry,tweet_mode='extended',
                                              max_id=str(max_t - 1), until=day_before)
                  else:
                      new_tweets = api.search(q=searchQuery, count=tweetsPerQry,tweet_mode='extended',
                                              max_id=str(max_t - 1),
                                              since_id=sinceId, until=day_before)
              if not new_tweets:
                  print("No more tweets found")
                  break
              for tweet in new_tweets:
                  t=Tweet.Tweet(tweet)
                  print(tweet._json)
                  print()
              tweetCount += len(new_tweets)
              print("Downloaded {0} tweets".format(tweetCount))
              global max_t 
              max_t = new_tweets[-1].id
          except TweepError as e:
              # Just exit if any error
              print("some error : " + str(e))
              break

  print ("Downloaded {0} tweets.".format(tweetCount))

@shared_task   
def SearchTweets():
  auth = OAuthHandler(_Config.consumer_key,_Config.consumer_secret)
  auth.set_access_token(_Config.access_token, _Config.access_secret)
  api = API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
  logger.info("I log!")
  tweet_search(api)