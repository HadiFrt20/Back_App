from . import helpers
from Application.models import db, User, Tweet, Hashtag, Keyword
# from extensions import db
from sqlalchemy import exc
from Application import Mouthful

app = Mouthful


def InsertMultipleEntries(tweets):
    succeeded = []
    AllEntries = helpers.Format(tweets)
    for entry in AllEntries:
        status = InsertdbEntry(entry)
        succeeded.append(status)
    db.session.remove()
    return succeeded


def InsertdbEntry(tweet):
    succeeded = True
    credscore = helpers.calcScore(tweet)
    this_Tweet = Tweet(id=tweet.tweet_id, text=tweet.text,
                       language=tweet.lang, longitude=tweet.lon,
                       latitude=tweet.lat, created_at=tweet.date,
                       retweets=tweet.retweets, favorites=tweet.favs,
                       polarity=tweet.polarity,
                       subjectivity=tweet.subjectivity)
    user_lon, user_lat = helpers.validcountry(tweet.user_location)
    this_User = User(id=tweet.user_id, screen_name=tweet.user,
                     verified=tweet.verified, score=credscore,
                     longitude=user_lon, latitude=user_lat,
                     seniority=tweet.seniority)
    with app.app_context():
        tweet_exists = this_Tweet.doesexist(tweet.tweet_id)
        if not tweet_exists:
            with db.session.no_autoflush:
                tweets_hashtags = []
                tweets_keywords = []
                if len(list(tweet.hashtags)) > 0:
                    for t in list(tweet.hashtags):
                        gen_id = helpers.genUniqueId(t['text'])
                        tag = Hashtag(id=gen_id, tag=t['text'])
                        tweets_hashtags.append(tag)
                if len(list(tweet.keywords)) > 0:
                    for k in list(tweet.keywords):
                        gen_id = helpers.genUniqueId(k)
                        keyword = Keyword(id=gen_id, keyword=k)
                        tweets_keywords.append(keyword)
                mnts_lst = list(tweet.mentions)
                try:
                    if(len(tweets_hashtags) > 0):
                        this_Tweet.hashtags.append(tweets_hashtags)
                    if(len(tweets_keywords) > 0):
                        this_Tweet.keywords.append(tweets_keywords)
                    db.session.add(this_Tweet)
                    user_exists = this_User.doesexist(tweet.user_id)
                    if user_exists is None:
                        this_User.tweets.append(this_Tweet)
                    else:
                        this_User = user_exists
                        this_User.tweets.append(this_Tweet)
                    if len(mnts_lst) > 0:
                        mentions = []
                        for mnts in mnts_lst:
                            mentioned = User()
                            if mnts is not None:
                                exists = this_User.doesexist(mnts._json['id'])
                                if exists is None:
                                    mentioned = User(id=mnts._json['id'],
                                                        screen_name=mnts._json['screen_name'],
                                                        verified=mnts._json['verified'],
                                                        score=credscore,
                                                        location=mnts._json['location'],
                                                        seniority=mnts._json['created_at'])
                                else:
                                    mentioned = exists
                                mentions.append(mentioned)
                            this_User.mentions.extend(mentions)
                    if user_exists is None:
                        db.session.add(this_User)
                    else:
                        print("User already exists")
                        # db.session.add(this_User)
                except exc.SQLAlchemyError as Err:
                    succeeded = False
                    print(Err)
            try:
                db.session.commit()
                db.session.close()
            except exc.SQLAlchemyError as Err:
                print(Err)
    return succeeded
