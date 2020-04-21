from . import TweetSearch
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'extensions')))
from extensions import celery
from celery import shared_task, Celery, subtask, chain, signature
from . import queries


Alltweets = []


@shared_task(name='searchfortweets')
def search4tweets():
    global Alltweets
    Alltweets = TweetSearch.SearchTweets()
    return Alltweets


@shared_task(name='savetodb')
def savetweets(tweets):
    print("Done looking for tweets")
    ret = -1
    statuses = queries.InsertMultipleEntries(tweets)
    if len(statuses) == 0:
        print('Data not inserted')
        ret = -1
    else:
        if True in statuses:
            if False in statuses:
                print('Some operations failed')
                ret = 0
            else:
                print('All operation terminated successfully')
                ret = 1
    return ret


@shared_task(name='gettweets')
def gettweets():
    save = search4tweets.apply_async((), link=savetweets.signature()).id
    save_result = celery.AsyncResult(save)
    print(save_result)
    # savetweets(tweets)
    return 0
