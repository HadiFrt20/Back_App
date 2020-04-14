from . import TweetSearch
from celery import shared_task, Celery, subtask, chain, signature
from celery.utils.log import get_task_logger
# from celery.result import allow_join_result
from . import _Config


logger = get_task_logger(__name__)
Alltweets = []


def make_celery():
    celery = Celery('tasks', broker=_Config.broker,
                    backend=_Config.backend)
    celery.conf.update(task_serializer=_Config.task_serializer,
                       accept_content=_Config.accept_content,
                       result_serializer=_Config.result_serializer,
                       timezone=_Config.timezone,
                       beat_schedule=_Config.CELERYBEAT_SCHEDULE,
                       enable_utc=_Config.enable_utc)
    return celery


celery = make_celery()


@shared_task(name='searchfortweets')
def search4tweets():
    global Alltweets
    Alltweets = TweetSearch.SearchTweets()
    return Alltweets


@shared_task(name='savetodb')
def savetweets(tweets):
    print("Done looking for tweets")
    print(len(tweets))
    print(tweets[0])
    return 1


@shared_task(name='gettweets')
def gettweets():
    save = search4tweets.apply_async((), link=savetweets.signature()).id
    save_result = celery.AsyncResult(save)
    print(save_result)
    # savetweets(tweets)
    return 0
