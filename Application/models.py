from Application import db
import datetime
from sqlalchemy import Column, Integer, DateTime, String, Text, Float

tweet_emoji = db.Table('tweet_emoji', db.Column('tweet_id',db.Integer, db.ForeignKey('tweets.id')),
                        db.Column('emoji_id',db.Integer, db.ForeignKey('emojis.id')))

tweet_hashtag = db.Table('tweet_hashtag', db.Column('tweet_id',db.Integer, db.ForeignKey('tweets.id')),
                        db.Column('hashtag_id',db.Integer, db.ForeignKey('hashtags.id')))

class User(db.Model):
  __tablename__='users'
  id = db.Column(db.Integer, primary_key=True)
  screen_name = db.Column(db.String(50))
  verified = db.Column(db.Boolean)
  followers = db.Column(db.Integer)
  statuses = db.Column(db.Integer)
  friends = db.Column(db.Integer)
  inlists = db.Column(db.Integer)
  seniority = db.Column(DateTime, default=datetime.datetime.utcnow)
  admin = db.Column(db.Boolean)
  tweets = db.relationship('Tweet', backref='author')


class Tweet(db.Model):
  __tablename__='tweets'
  id = db.Column(db.Integer, primary_key=True)
  text = db.Column(db.String(280))
  language = db.Column(db.String(4))
  longitude = db.Column(db.Float)
  latitude = db.Column(db.Float)
  created_at = db.Column(DateTime, default=datetime.datetime.utcnow)
  retweets = db.Column(db.Integer)
  favorites = db.Column(db.Integer)
  emojis = db.relationship('Emoji', secondary=tweet_emoji, backref=db.backref('tweets',lazy='dynamic'))
  hashtags = db.relationship('Hashtag', secondary=tweet_hashtag, backref=db.backref('tweets',lazy='dynamic'))
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  

class Hashtag(db.Model):
  __tablename__='hashtags'
  id = db.Column(db.Integer, primary_key=True)
  tag = db.Column(db.Text)
  
class Emoji(db.Model):
  __tablename__='emojis'
  id = db.Column(db.Integer, primary_key=True)
  emoji = db.Column(db.String(60))

class Mention(db.Model):
  __tablename__ = 'mentions'
  mention_id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  mentioned_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  mentioned = db.relationship('User', foreign_keys=[user_id], backref=db.backref('mentions',lazy='dynamic'))