from emoji import UNICODE_EMOJI,demojize
import re

class Tweet:
  
  def get_tweet_id(self,status):
    return status.id
  
  def get_coordinates(self,status):
    coords = status._json["coordinates"]
    lon = None
    lat = None
    if coords is not None:
      lon = coords["coordinates"][0]
      lat = coords["coordinates"][1]
    return lon,lat;

  def get_text(self,status):
    text = ""
    if 'full_text' in status._json :
      text = status.full_text
    else:
      text = status.text
    exp_filter = "(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?|([@#][\w_-]+)"
    clean_text = re.sub(exp_filter, "", text)
    return clean_text

  def get_date(self,status):
    date = status.created_at
    return str(date)

  def get_country(self,status):
    if status._json['place'] is not None:
      country = status._json['place']['country']
    else:
      country = None
    return country

  def get_user(self,status):
    return status._json['user']['screen_name']
  
  def get_user_id(self,status):
    return status._json['user']['id']
  
  def get_lang(self,status):
    return str(status._json['lang'])

  def get_followers(self,status):
    return status._json['user']['followers_count']

  def get_listed(self,status):
    return status._json['user']['listed_count']

  def get_friends(self,status):
    return status._json['user']['friends_count']

  def get_statuses(self,status):
    return status._json['user']['statuses_count']

  def get_seniority(self,status):
    date = status._json['user']['created_at']
    return str(date)
  
  def is_verified(self,status):
    verified = status._json['user']['verified']
    return verified

  def get_rts(self,status):
    if status.retweeted:
      return status.retweet_count
    else:
      return 0

  def get_favs(self,status):
    if status.favorited:
      return status.favorite_count
    else:
      return 0

  def get_hashtags(self,status):
    if 'hashtags' in status._json:
      return status.entities['hashtags']
    else:
      return None

  def get_mentioned(self,status):
    if 'user_mentions' in status._json:
      return status.entities['user_mentions']
    else:
      return None

  def get_emojis(self,tweet_text):
    list = [demojize(c) for c in tweet_text if c in UNICODE_EMOJI]
    return list

  def __init__(self,status):
      self.tweet_id = self.get_tweet_id(status)
      self.country =self.get_country(status)
      self.user =self.get_user(status)
      self.user_id = self.get_user_id(status)
      self.verified = self.is_verified(status)
      self.lon =self.get_coordinates(status)[0]
      self.lat =self.get_coordinates(status)[1]
      self.text =self.get_text(status)
      self.mentions =self.get_mentioned(status)
      self.hashtags =self.get_hashtags(status)
      self.emojis =self.get_emojis(self.text)
      self.date =self.get_date(status)
      self.retweets =self.get_rts(status)
      self.favs =self.get_favs(status)
      self.followers = self.get_followers(status)
      self.friends = self.get_friends(status)
      self.inlists = self.get_listed(status)
      self.statuscnt = self.get_statuses(status)
      self.seniority = self.get_seniority(status)
      self.lang = self.get_lang(status)
     
    