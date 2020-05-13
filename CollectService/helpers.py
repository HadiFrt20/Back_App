from . import Tweet, TweetSearch, textprocessing
from datetime import datetime
import hashlib
from math import log
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


def Format(nested_list):
    New_Tweets = []
    for Itr in nested_list:
        for tweetdict in Itr:
            NewTweet = Tweet.Tweet(tweetdict, 'PostProcessing')
            NewTweet.mentions = UsrfromId(NewTweet.mentions)
            NewTweet.keywords = textprocessing.MatchKeywords(NewTweet.text)
            NewTweet.polarity = textprocessing.GetSentiment(NewTweet.text)[0]
            NewTweet.subjectivity = textprocessing.\
                GetSentiment(NewTweet.text)[1]
            NewTweet.CredScore = calcScore(NewTweet)
            New_Tweets.append(NewTweet)
    return New_Tweets


def UsrfromId(lst):
    new_lst = []
    if len(lst) > 0:
        for mentioned_user in lst:
            if mentioned_user is None:
                pass
            else:
                new_lst.append(TweetSearch.GetUserfromId(mentioned_user['id']))
    return new_lst


def genUniqueId(string):
    id = int(hashlib.md5(string.encode('utf-8')).hexdigest(), 16)
    trunc_id = int(str(id)[:15])
    return trunc_id


# Formula for CalcScore
def calcScore(TweetObject):
    activity = 0
    rejectnulldate = "0000-00-00 00:00:00"
    creation_date_string = TweetObject.seniority
    if creation_date_string != rejectnulldate:
        creation_date = datetime.strptime(creation_date_string,
                                          '%Y-%m-%d %H:%M:%S')
        seniority = (datetime.now() - creation_date).days
        activity = log(int(TweetObject.statuscnt)/(seniority))

    friends = int(TweetObject.friends)
    followers = int(TweetObject.followers)
    lists = int(TweetObject.inlists)
    if friends > 0 and followers > 0:
        reach = log(followers/friends)
    else:
        reach = -4
    if followers > 0 and lists > 0:
        influence = log(lists) + log(followers)
    else:
        influence = - 4
    score = 0.3 * activity + 0.3 * reach + 0.4 * influence
    return score


#Replace location with lon, lat
def validcountry(TwitteLocation):
    geolocator = Nominatim(user_agent="InsightApp")
    location = None
    try:
        location = geolocator.geocode(TwitteLocation)
    except GeocoderTimedOut as e:
        print("Error: geocode failed on input %s with message %s"%(TwitteLocation, e))
    
    if location is not None:
        return location.longitude, location.latitude
    else:
        return None, None