"""This script defines the models and tables needed to store tweets"""
from flask_sqlalchemy import SQLAlchemy
from CollectService import helpers
from Application import db, Mouthful
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
import datetime
from sqlalchemy import DateTime, exc, orm

Base = declarative_base()
# db = SQLAlchemy()


def find_or_create(foundtags):
    for foundtag in foundtags:
        try:
            hashtag = foundtag.doesexist(foundtag.id)
            if hashtag is None:
                print("Writing new hashtag record")
                hashtag = Hashtag(id=foundtag.id, tag=foundtag.tag)
            else:
                print("Appended old record")
        except exc.SQLAlchemyError as err:
            print(err)
    return Tweet_Hashtag(hashtag)


class Tweet_Hashtag(db.Model):
    __tablename__ = 'tweet_hashtag'
    tweet_fk = db.Column('tweet_id', db.BigInteger,
                         db.ForeignKey('tweets.id'), primary_key=True)
    hashtag_fk = db.Column('hashtag_id', db.BigInteger,
                           db.ForeignKey('hashtags.id'), primary_key=True)
    hashtag = db.relationship("Hashtag", back_populates="tweets")
    tweet = db.relationship("Tweet", backref="t_h")

    def __init__(self, proxied=None):
        if type(proxied) is Tweet:
            self.tweet = proxied
        elif type(proxied) is Hashtag:
            self.hashtag = proxied


mention = db.Table('mention',
                   db.Column('user_fk', db.BigInteger,
                             db.ForeignKey('users.id')),
                   db.Column('mentioned_fk', db.BigInteger,
                             db.ForeignKey('users.id')))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True)
    screen_name = db.Column(db.String(50))
    location = db.Column(db.String(150))
    verified = db.Column(db.Boolean)
    score = db.Column(db.Float)
    seniority = db.Column(DateTime, default=datetime.datetime.utcnow)
    tweets = db.relationship("Tweet", backref='user', lazy='dynamic')
    mentions = db.relationship("User", secondary=mention,
                               primaryjoin=id == mention.c.user_fk,
                               secondaryjoin=id == mention.c.mentioned_fk,
                               backref="left mentions")

    @classmethod
    def doesexist(cls, id):
        user = None
        exists = db.session.query(User.id).filter_by(
            id=id).scalar() is not None
        if exists:
            user = db.session.query(User).join(User.tweets).\
                filter(User.id == id).first()
        return user


class Tweet(db.Model):
    __tablename__ = 'tweets'
    id = db.Column(db.BigInteger, primary_key=True)
    text = db.Column(db.String(280))
    language = db.Column(db.String(4))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    country = db.Column(db.Text)
    created_at = db.Column(DateTime, default=datetime.datetime.utcnow)
    retweets = db.Column(db.Integer)
    favorites = db.Column(db.Integer)
    keyword = db.Column(db.Text)
    polarity = db.Column(db.Float)
    subjectivity = db.Column(db.Float)
    hashtags = association_proxy("t_h", "hashtag", creator=find_or_create)
    user_fk = db.Column(db.BigInteger, db.ForeignKey('users.id'))

    @classmethod
    def doesexist(cls, id):
        exists = db.session.query(Tweet.id).\
            filter(Tweet.id == id).scalar() is not None
        if exists:
            print('Tweet already exists')
        return exists


class Hashtag(db.Model):
    __tablename__ = 'hashtags'
    id = db.Column(db.BigInteger, primary_key=True)
    tag = db.Column(db.VARCHAR(280), nullable=False)
    tweets = db.relationship("Tweet_Hashtag", back_populates="hashtag")
    # TODO fix hashtags duplicates
    @classmethod
    def doesexist(cls, id):
        tag = None
        exists = False
        try:
            exists = db.session.query(Hashtag).\
                filter(Hashtag.id == id).one() is not None
        except orm.exc.MultipleResultsFound:
            exists = True
        except orm.exc.NoResultFound:
            exists = False

        if exists:
            tag = db.session.query(Hashtag).\
                filter(Hashtag.id == id).first()
        return tag


def InsertMultipleEntries(tweets):
    succeeded = []
    AllEntries = helpers.Format(tweets)
    for entry in AllEntries:
        status = InsertdbEntry(entry)
        succeeded.append(status)
    return succeeded


def InsertdbEntry(tweet):
    succeeded = True
    credscore = helpers.calcScore(tweet)
    this_Tweet = Tweet(id=tweet.tweet_id, text=tweet.text,
                       language=tweet.lang, longitude=tweet.lon,
                       latitude=tweet.lat, created_at=tweet.date,
                       retweets=tweet.retweets, favorites=tweet.favs,
                       keyword="test", polarity=1.22, subjectivity=0.33)
    this_User = User(id=tweet.user_id, screen_name=tweet.user,
                     verified=tweet.verified, score=credscore,
                     location=tweet.user_location, seniority=tweet.seniority)
    with Mouthful.app_context():
        tweet_exists = this_Tweet.doesexist(tweet.tweet_id)
        if not tweet_exists:
            with db.session.no_autoflush:
                tweets_hashtags = []
                # associations = []
                if len(list(tweet.hashtags)) > 0:
                    for t in list(tweet.hashtags):
                        gen_id = helpers.genUniqueId(t['text'])
                        tag = Hashtag(id=gen_id, tag=t['text'])
                        # exists = tag.doesexist(gen_id)
                        # if exists is None:
                        #     new_tag = Hashtag(id=gen_id, tag=t['text'])
                        #     # asso = Tweet_Hashtag()
                        #     # asso.hashtag = new_tag
                        tweets_hashtags.append(tag)
                        # else:
                        #     old_tag = exists
                        #     asso = Tweet_Hashtag(this_Tweet, old_tag)
                        #     associations.append(asso)
                mnts_lst = list(tweet.mentions)
                try:
                    # if len(this_hashtags) > 0:
                    #     for newtag in this_hashtags:
                    #         db.session.merge(newtag)
                    #         db.session.flush()
                    if(len(tweets_hashtags) > 0):
                        this_Tweet.hashtags.append(tweets_hashtags)

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
                        db.session.merge(this_User)
                except exc.SQLAlchemyError as Err:
                    succeeded = False
                    print(Err)
            try:
                db.session.commit()
                db.session.close()
            except exc.SQLAlchemyError as Err:
                print(Err)
    return succeeded
