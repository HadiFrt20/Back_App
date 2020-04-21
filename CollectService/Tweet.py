from emoji import UNICODE_EMOJI, demojize
import re
from datetime import datetime
import pandas as pd


class Tweet:

    def get_tweet_id(self, status):
        return status.id

    def get_coordinates(self, status):
        coords = status._json["coordinates"]
        lon = None
        lat = None
        if coords is not None:
            lon = coords["coordinates"][0]
            lat = coords["coordinates"][1]
        return lon, lat

    def get_text(self, status):
        text = ""
        if 'full_text' in status._json:
            text = status.full_text
        else:
            text = status.text
        exp_filter = r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?|([@#][\w_-]+)"
        clean_text = re.sub(exp_filter, "", text)
        readable_text = self.replace_emojis(clean_text)
        return readable_text

    def get_date(self, status):
        date = status.created_at
        return str(date)

    def get_country(self, status):
        if status._json['place'] is not None:
            country = status._json['place']['country']
        else:
            country = None
        return country

    def get_user(self, status):
        return status._json['user']['screen_name']

    def get_user_id(self, status):
        return status._json['user']['id']

    def get_user_location(self, status):
        return status._json['user']['location']

    def get_lang(self, status):
        return str(status._json['lang'])

    def get_followers(self, status):
        return status._json['user']['followers_count']

    def get_listed(self, status):
        return status._json['user']['listed_count']

    def get_friends(self, status):
        return status._json['user']['friends_count']

    def get_statuses(self, status):
        return status._json['user']['statuses_count']

    def get_seniority(self, status):
        date = status._json['user']['created_at']
        ts = pd.Timestamp(date).tz_convert("UTC")
        new_date = ts.strftime("%Y-%m-%d %H:%M:%S")
        return str(new_date)

    def is_verified(self, status):
        verified = status._json['user']['verified']
        return verified

    def get_rts(self, status):
        return status.retweet_count

    def get_favs(self, status):
        return status.favorite_count

    def get_hashtags(self, status):
        return status.entities['hashtags']

    def get_mentioned(self, status):
        return status.entities['user_mentions']

    def replace_emojis(self, tweet_text):
        readable_tweet = tweet_text
        lst = [c for c in tweet_text if c in UNICODE_EMOJI]
        if(len(lst) > 0):
            emoji_dict = {}
            for emoji in lst:
                emoji_dict[emoji] = demojize(emoji)
            for e, t in emoji_dict.items():
                readable_tweet = tweet_text.replace(e.lower(), t)
        return readable_tweet

    def __init__(self, status, key):
        if key == 'SearchAPI':
            self.tweet_id = self.get_tweet_id(status)
            self.country = self.get_country(status)
            self.user = self.get_user(status)
            self.user_id = self.get_user_id(status)
            self.verified = self.is_verified(status)
            self.user_location = self.get_user_location(status)
            self.lon = self.get_coordinates(status)[0]
            self.lat = self.get_coordinates(status)[1]
            self.text = self.get_text(status)
            self.mentions = self.get_mentioned(status)
            self.hashtags = self.get_hashtags(status)
            self.date = self.get_date(status)
            self.retweets = self.get_rts(status)
            self.favs = self.get_favs(status)
            self.followers = self.get_followers(status)
            self.friends = self.get_friends(status)
            self.inlists = self.get_listed(status)
            self.statuscnt = self.get_statuses(status)
            self.seniority = self.get_seniority(status)
            self.lang = self.get_lang(status)

        else:
            if key == 'PostProcessing':
                self.tweet_id = status["tweet_id"]
                self.country = status["country"]
                self.user = status["user"]
                self.CredScore = 0
                self.user_id = status["user_id"]
                self.user_location = status["user_location"]
                self.verified = bool(status["verified"])
                self.lon = status["lon"]
                self.lat = status["lat"]
                self.text = str(status["text"])
                self.keywords = []
                self.polarity = 0
                self.subjectivity = 0
                self.mentions = status["mentions"]
                self.hashtags = status["hashtags"]
                self.date = status["date"]
                self.retweets = status["retweets"]
                self.favs = status["favs"]
                self.followers = status["followers"]
                self.friends = status["friends"]
                self.inlists = status["inlists"]
                self.statuscnt = status["statuscnt"]
                self.seniority = status["seniority"]
                self.lang = status["lang"]
