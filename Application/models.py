"""This script defines the models and tables needed to store tweets"""
from flask_sqlalchemy import SQLAlchemy
from CollectService import helpers
from Application import db, Mouthful
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import DateTime, exc
from sqlalchemy.orm import backref
from random import randint

Base = declarative_base()
# db = SQLAlchemy()

tweet_hashtag = db.Table('tweet_hashtag',
                         db.Column('tweet_id', db.BigInteger,
                                   db.ForeignKey('tweets.id')),
                         db.Column('hashtag_id', db.Integer,
                                   db.ForeignKey('hashtags.id')))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True)
    screen_name = db.Column(db.String(50))
    verified = db.Column(db.Boolean)
    score = db.Column(db.Float)
    seniority = db.Column(DateTime, default=datetime.datetime.utcnow)
    tweets = db.relationship("Tweet", backref='user', lazy='dynamic')

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
        with Mouthful.app_context():
            exists = db.session.query(Tweet.id).\
                filter(Tweet.id == id).scalar() is not None
            if exists:
                print('Tweet already exists')
        return exists


class Hashtag(db.Model):
    __tablename__ = 'hashtags'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.Text)


class Mention(db.Model):
    __tablename__ = 'mentions'
    mention_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.BigInteger, db.ForeignKey('users.id'))
    mentioned_id = db.Column(
        db.BigInteger, db.ForeignKey('users.id'))
    mentioned = db.relationship(
        'User', foreign_keys=[user_id],
        backref=db.backref('mentions', lazy='dynamic'))


def InsertMultipleEntries(tweets):
    succeeded = []
    AllEntries = helpers.Format(tweets)
    for entry in AllEntries:
        status = InsertdbEntry(entry)
        succeeded.append(status)
    return succeeded


def InsertdbEntry(tweet):
    succeeded = True
    this_hashtags = []
    this_mentions = []
    credscore = helpers.calcScore(tweet)
    this_Tweet = Tweet(id=tweet.tweet_id, text=tweet.text,
                       language=tweet.lang, longitude=tweet.lon,
                       latitude=tweet.lat, created_at=tweet.date,
                       retweets=tweet.retweets, favorites=tweet.favs,
                       keyword="test", polarity=1.22, subjectivity=0.33)
    this_User = User(id=tweet.user_id, screen_name=tweet.user,
                     verified=tweet.verified, score=credscore,
                     seniority=tweet.seniority)
    tweet_exists = this_Tweet.doesexist(tweet.tweet_id)
    if not tweet_exists:
        if tweet.hashtags is not None:
            for t in list(tweet.hashtags):
                idx = 0
                tag = Hashtag()
                tag.tag = list(tweet.hashtags)[idx]
                this_hashtags.append(tag)
                idx = idx + 1
            this_Tweet.hashtags.extend(this_hashtags)

        if tweet.mentions is not None:
            mnts_lst = list(tweet.mentions)
            print('mentions list size is : ', len(mnts_lst))
            for mnts in mnts_lst:
                idx = 0
                mention = Mention()
                mention.user_screen_name = tweet.user
                mention.mentioned_screen_name = randint(19271979, 829189383223)
                # mnts_lst[idx]
                this_mentions.append(mention)
                idx = idx + 1
        with Mouthful.app_context():
            try:
                db.session.add(this_Tweet)
                if this_hashtags is not None:
                    db.session.bulk_save_objects(this_hashtags)
                user_exists = this_User.doesexist(tweet.user_id)
                if user_exists is None:
                    print("User doesn't exist", user_exists, this_User)
                    this_User.tweets.append(this_Tweet)
                    db.session.add(this_User)
                else:
                    print("User already exists")
                    this_User = user_exists
                    this_User.tweets.append(this_Tweet)
                    db.session.merge(this_User)
                if len(this_mentions) > 0:
                    db.session.bulk_save_objects(this_mentions)
                db.session.commit()
            except exc.SQLAlchemyError as Err:
                succeeded = False
                print(Err)
            db.session.close()
    return succeeded
