from . import Tweet, TweetSearch


def Format(nested_list):
    New_Tweets = []
    for Itr in nested_list:
        for tweetdict in Itr:
            NewTweet = Tweet.Tweet(tweetdict, 'PostProcessing')
            new_mentions = UsrfromId(NewTweet.mentions)
            NewTweet.mentions = new_mentions
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
    # TODO get text sentiment and send subjectivity and polairty to models
    # TODO set keywords and send


# Formula for CalcScore
def calcScore(TweetObject):
    # tweet.favs, statuscnt, followers, friends, inlists, seniority
    return 0
