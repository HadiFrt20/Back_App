from Application import Mouthful
from sqlalchemy.sql import func
from flask import jsonify
from Application.models import db, User, Tweet, Hashtag, Keyword, mention
from Application.models import Tweet_Hashtag, Tweet_Keyword, AccessToken
from Application.models import Tester


app = Mouthful

#Helpers
def replaceusermentions(allusers):
    idscreenname = {}
    for user in allusers:
        idscreenname[allusers[user]['id']] = allusers[user]['screen_name']
    for alt_user in allusers:
        if allusers[alt_user]['mentioned'] != 0 and allusers[alt_user]['mentioned'] is not None:
            mentioned_id = allusers[alt_user]['mentioned']
            allusers[alt_user]['mentioned'] = idscreenname[mentioned_id]
    return allusers


#Queries
def getusers():
    users = db.session.query(User.id, User.longitude, User.latitude,
                             User.screen_name, User.verified,
                             func.count(Tweet.id).label('tweets')).\
        join(Tweet, User.id == Tweet.user_fk).\
        group_by(User.id).all()
    db.session.close()
    db.session.remove()
    allusers = {}
    idx = 0
    for user in users:
        a_user = {}
        a_user['id'] = user.id
        a_user['longitude'] = user.longitude
        a_user['latitude'] = user.latitude
        a_user['screen_name'] = user.screen_name
        a_user['verified'] = user.verified
        a_user['tweets_count'] = user.tweets
        allusers[idx] = a_user
        idx = idx + 1
    return jsonify(allusers)

def getAllUsers():
    users = db.session.execute('SELECT *, ifnull(mention.mentioned_fk, 0) as ment, COUNT(mention.user_fk) as weight\
                                FROM users LEFT OUTER JOIN mention \
                                on users.id = mention.user_fk GROUP BY ifnull(mentioned_fk, 0), \
                                users.id ORDER BY score DESC')
    db.session.close()
    db.session.remove()
    allusers = {}
    idx = 0
    for user in users:
        a_user = {}
        a_user['id'] = user.id
        a_user['location'] = user.location
        a_user['screen_name'] = user.screen_name
        a_user['verified'] = user.verified
        a_user['score'] = user.score
        a_user['mentioned'] = user.ment
        a_user['weight'] = user.weight
        allusers[idx] = a_user
        idx = idx + 1
    return jsonify(replaceusermentions(allusers))

def gettweetsbyhashtag():
    hashtags_tweets = db.session.query(Hashtag,
                                       func.avg(Tweet.polarity).label(
                                           'polarity'),
                                       func.avg(Tweet.subjectivity).label(
                                           'subjectivity'),
                                       func.count(Tweet.id).label('tweets'))\
        .join(Tweet_Hashtag, Hashtag.id == Tweet_Hashtag.hashtag_fk)\
        .join(Tweet, Tweet.id == Tweet_Hashtag.tweet_fk)\
        .group_by(Hashtag.id).all()
    all_hk = {}
    idx = 0
    for hk in hashtags_tweets:
        h_k = {}
        h_k['tag'] = hk.Hashtag.tag
        h_k['tweets_count'] = hk.tweets
        h_k['avg_polarity'] = hk.polarity
        h_k['avg_subjectivity'] = hk.subjectivity
        all_hk[idx] = h_k
        idx = idx + 1
    return jsonify(all_hk)


def gethashtagkeys():
    hashtags_keys = db.session.query(Hashtag, Keyword)\
                              .join(Tweet_Hashtag, Hashtag.id
                                    == Tweet_Hashtag.hashtag_fk)\
                              .join(Tweet, Tweet.id
                                    == Tweet_Hashtag.tweet_fk)\
                              .join(Tweet_Keyword, Tweet_Keyword.tweet_fk
                                    == Tweet.id)\
                              .join(Keyword, Keyword.id
                                    == Tweet_Keyword.keyword_fk)\
                              .all()
    all_hk = {}
    idx = 0
    for hk in hashtags_keys:
        h_k = {}
        h_k['tag'] = hk.Hashtag.tag
        h_k['keyword'] = hk.Keyword.keyword
        all_hk[idx] = h_k
        idx = idx + 1
    return jsonify(all_hk)


def gettweetsbykeyword():
    try:
        keywords_tweets = db.session.query(Keyword,
                                        func.avg(Tweet.polarity).label(
                                            'polarity'),
                                        func.avg(Tweet.subjectivity).label(
                                            'subjectivity'),
                                        func.count(Tweet.id).label('tweets'))\
            .join(Tweet_Keyword, Keyword.id == Tweet_Keyword.keyword_fk)\
            .join(Tweet, Tweet.id == Tweet_Keyword.tweet_fk)\
            .group_by(Keyword.id).all()
    except:
        pass
    all_kt = {}
    idx = 0
    for kt in keywords_tweets:
        k_t = {}
        k_t['keyword'] = kt.Keyword.keyword
        k_t['tweets_count'] = kt.tweets
        k_t['avg_polarity'] = kt.polarity
        k_t['avg_subjectivity'] = kt.subjectivity
        all_kt[idx] = k_t
        idx = idx + 1
    return jsonify(all_kt)


def getsentimentbycatbyday():
    try:
        keywords_tweets = db.session.query(Keyword,
                                        func.date_format(Tweet.created_at, '%y-%m-%d')
                                        .label('date'),
                                        func.avg(Tweet.polarity).label(
                                            'polarity'),
                                        func.avg(Tweet.subjectivity).label(
                                            'subjectivity'),
                                        func.count(Tweet.id).label('tweets'))\
            .join(Tweet_Keyword, Keyword.id == Tweet_Keyword.keyword_fk)\
            .join(Tweet, Tweet.id == Tweet_Keyword.tweet_fk)\
            .group_by(Keyword.id, func.date_format(Tweet.created_at, '%y-%m-%d')
                                        .label('date')).all()
    except:
        pass
    all_kt = {}
    idx = 0
    for kt in keywords_tweets:
        k_t = {}
        k_t['date'] = kt.date
        k_t['keyword'] = kt.Keyword.keyword
        k_t['tweets_count'] = kt.tweets
        k_t['avg_polarity'] = kt.polarity
        k_t['avg_subjectivity'] = kt.subjectivity
        all_kt[idx] = k_t
        idx = idx + 1
    return jsonify(all_kt)


def getsentimentbyday():
    try:
        tweets = db.session.query(func.date_format(Tweet.created_at, '%y-%m-%d')
                                .label('date'),
                                func.avg(Tweet.polarity).label('polarity'),
                                func.avg(Tweet.subjectivity)
                                .label('subjectivity'))\
            .group_by(func.date_format(Tweet.created_at, '%y-%m-%d'), )\
            .all()
    except:
        pass
    all_tw = {}
    idx = 0
    for t in tweets:
        tw = {}
        tw['date'] = t.date
        tw['avg_polarity'] = t.polarity
        tw['avg_subjectivity'] = t.subjectivity
        all_tw[idx] = t
        idx = idx + 1
    return jsonify(all_tw)

def createtester(pid, email, hashed_pass, accesstoken):
    status = {"status" : "Access Token is not valid"}
    new_tester = Tester(public_id=pid, email=email, password=hashed_pass)
    token = AccessToken.doesexist(accesstoken)
    if token is None:
        status = {"status" : "Access Token is not valid", "code" : 205}
    else:
        if token.credit <= 0:
            status = {"status" : "Access Token expired", "code" : 205}
        else:
            token.credit = token.credit - 1
            tester_exists = Tester.doesexist(email)[0]
            if tester_exists is False:
                with app.app_context():
                    with db.session.no_autoflush:
                        try:
                            token.testers.append(new_tester)
                            db.session.commit()
                            db.session.close()
                            db.session.remove()
                            status = status = {"status" : "User successfully created", "code" : 201}
                        except:
                            pass
            else:
                status = status = {"status" : "User already exists", "code" : 204}
    return jsonify(status)


def getatester(auth_email):
    try:
        exists, tester = Tester.doesexist(auth_email)
        db.session.close()
        db.session.remove()
    except:
        pass
    if exists:
        return exists, tester
    else:
        return exists, None


def getatesterbyid(pid):
    try:
        current_tester = db.session.query(Tester).filter(
            Tester.public_id == pid).first()
    except:
        pass
    return current_tester
