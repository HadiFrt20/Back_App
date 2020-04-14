from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
from Application import Tweet
from Application import _Config
from celery import shared_task
from celery.utils.log import get_task_logger
import json

logger = get_task_logger(__name__)
class stdOutListener(StreamListener):
    def __init__(self, output_file):
        super(stdOutListener,self).__init__()
        self.output_file = output_file
        self.tweets = []
        
    def on_status(self, status):
      if status._json['place']['country_code'] != 'IL' and status._json['place']['country_code'] != 'SY' and status._json['place']['country_code'] != 'JO':
        t = Tweet.Tweet(status)
        self.tweets.append(t)
        #print(t.__dict__)
        logger.info(t.text)

    
    def on_error(self, status_code):
        print(status_code)
        return False


@shared_task   
def StreamTweets():
  output = open('stream_output.json', 'w')
  Geobox_Lebanon =[35.104,33.067,36.623,34.691]
  Listener= stdOutListener(output_file=output)
  auth = OAuthHandler(_Config.consumer_key,_Config.consumer_secret)
  auth.set_access_token(_Config.access_token, _Config.access_secret)
  api = API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
  stream = Stream(api.auth, Listener,tweet_mode='extended')
  logger.info("I log!")
  stream.filter(locations=Geobox_Lebanon)