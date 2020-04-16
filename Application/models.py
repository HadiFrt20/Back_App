"""This script defines the models and tables needed to store tweets"""
from flask_sqlalchemy import SQLAlchemy
from CollectService import helpers
from Application import db, Mouthful
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import DateTime, exc, orm

Base = declarative_base()
# db = SQLAlchemy()

tweet_hashtag = db.Table('tweet_hashtag',
                         db.Column('tweet_id', db.BigInteger,
                                   db.ForeignKey('tweets.id')),
                         db.Column('hashtag_id', db.Integer,
                                   db.ForeignKey('hashtags.id')))


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
            print(user)
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
    hashtags = db.relationship(
        'Hashtag', secondary=tweet_hashtag,
        backref='tweet', lazy='dynamic')
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
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.Text, nullable=False)
    # TODO fix hashtags duplicates
    @classmethod
    def doesexist(cls, txt):
        tag = None
        exists = False
        try:
            exists = db.session.query(Hashtag).\
                     filter(Hashtag.tag == txt).one() is not None
        except orm.exc.MultipleResultsFound:
            exists = True
        except orm.exc.NoResultFound:
            exists = False

        if exists:
            print('Hashtag already exists')
            tag = db.session.query(Hashtag).\
                filter(Hashtag.tag == txt).first()
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
            this_hashtags = []
            tweets_hashtags = []
            if len(list(tweet.hashtags)) > 0:
                for t in list(tweet.hashtags):
                    tag = Hashtag()
                    exists = tag.doesexist(t['text'])
                    if exists is None:
                        new_tag = Hashtag(tag=t['text'])
                        this_hashtags.append(new_tag)
                        tweets_hashtags.append(new_tag)
                    else:
                        old_tag = exists
                        tweets_hashtags.append(old_tag)
            mnts_lst = list(tweet.mentions)
            try:
                db.session.add(this_Tweet)
                if len(this_hashtags) > 0:
                    for hashtag in this_hashtags:
                        db.session.merge(hashtag)
                if(len(tweets_hashtags) > 0):
                    this_Tweet.hashtags.extend(tweets_hashtags)
                user_exists = this_User.doesexist(tweet.user_id)
                if user_exists is None:
                    print("User doesn't exist")
                    this_User.tweets.append(this_Tweet)
                else:
                    print("User already exists")
                    this_User = user_exists
                    this_User.tweets.append(this_Tweet)
                if len(mnts_lst) > 0:
                    mentions = []
                    for mnts in mnts_lst:
                        mentioned = User()
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
                db.session.commit()
            except exc.SQLAlchemyError as Err:
                succeeded = False
                print(Err)
            db.session.close()
    return succeeded
