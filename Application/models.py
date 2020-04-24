"""This script defines the models and tables needed to store tweets"""
from Application import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
import datetime
from sqlalchemy import DateTime, exc, orm

Base = declarative_base()


def find_or_create_hashtag(foundtags):
    for foundtag in foundtags:
        try:
            hashtag = foundtag.doesexist(foundtag.id)
            if hashtag is None:
                # print("Writing new hashtag record")
                hashtag = Hashtag(id=foundtag.id, tag=foundtag.tag)
            else:
                pass
                # print("Appended old record")
        except exc.SQLAlchemyError as err:
            print(err)
    return Tweet_Hashtag(hashtag)


def find_or_create_keyword(matchedkeywords):
    for key in matchedkeywords:
        try:
            keyword = key.doesexist(key.id)
            if keyword is None:
                # print("Writing new keyword record")
                keyword = Keyword(id=key.id, keyword=key.keyword)
            else:
                pass
                # print("Appended old keyword record")
        except exc.SQLAlchemyError as err:
            print(err)
    return Tweet_Keyword(keyword)


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


class Tweet_Keyword(db.Model):
    __tablename__ = 'tweet_keyword'
    tweet_fk = db.Column('tweet_id', db.BigInteger,
                         db.ForeignKey('tweets.id'), primary_key=True)
    keyword_fk = db.Column('keyword_id', db.BigInteger,
                           db.ForeignKey('keywords.id'), primary_key=True)
    keyword = db.relationship("Keyword", back_populates="tweets")
    tweet = db.relationship("Tweet", backref="t_k")

    def __init__(self, proxied=None):
        if type(proxied) is Tweet:
            self.tweet = proxied
        elif type(proxied) is Keyword:
            self.keyword = proxied


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
    polarity = db.Column(db.Float)
    subjectivity = db.Column(db.Float)
    hashtags = association_proxy("t_h", "hashtag",
                                 creator=find_or_create_hashtag)
    keywords = association_proxy("t_k", "keyword",
                                 creator=find_or_create_keyword)
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


class AccessToken(db.Model):
    __tablename__ = 'accesstokens'
    id = db.Column(db.BigInteger, primary_key=True)
    token = db.Column(db.String(50), unique=True)
    credit = db.Column(db.Integer)
    testers = db.relationship("Tester", backref='accesstokens', lazy='dynamic')
    @classmethod
    def doesexist(cls, txt):
        token = None
        exists = False
        try:
            exists = db.session.query(AccessToken).\
                filter(AccessToken.token == txt).one() is not None
        except orm.exc.MultipleResultsFound:
            exists = True
        except orm.exc.NoResultFound:
            exists = False

        if exists:
            token = db.session.query(AccessToken).\
                filter(AccessToken.token == txt).first()
        return token


class Tester(db.Model):
    __tablename__ = 'testers'
    id = db.Column(db.BigInteger, primary_key=True)
    public_id = db.Column(db.String(36), unique=True)
    email = db.Column(db.VARCHAR(320))
    password = db.Column(db.String(80))
    token_fk = db.Column(db.BigInteger, db.ForeignKey('accesstokens.id'))
    @classmethod
    def doesexist(cls, email):
        exists = False
        old_tester = db.session.query(Tester).\
            filter(Tester.email == email).scalar()
        if old_tester is not None:
            exists = True
        return exists, old_tester


class Keyword(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.BigInteger, primary_key=True)
    keyword = db.Column(db.VARCHAR(280), nullable=False)
    tweets = db.relationship("Tweet_Keyword", back_populates="keyword")
    @classmethod
    def doesexist(cls, id):
        key = None
        exists = False
        try:
            exists = db.session.query(Keyword).\
                filter(Keyword.id == id).one() is not None
        except orm.exc.MultipleResultsFound:
            exists = True
        except orm.exc.NoResultFound:
            exists = False

        if exists:
            key = db.session.query(Keyword).\
                filter(Keyword.id == id).first()
        return key
