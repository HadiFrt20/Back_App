from . import TweetSearch
from celery import shared_task, Celery, subtask
from celery.utils.log import get_task_logger
from celery.result import allow_join_result
from time import sleep
from . import _Config


logger = get_task_logger(__name__)


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


def genquery(idx):
    filters = " AND -filter:replies AND -filter:retweets"
    klist = list(_Config.keywords.keys())
    mlist = list(_Config.keywords.values())
    keyword_ = klist[idx]
    max_t = mlist[idx]
    q = keyword_ + filters
    return q, max_t


@shared_task(name='searchfortweets')
def search4tweets():
    alltweets = []
    maxt = -1
    cnt = _Config.keywords
    for idx in range(len(cnt)):
        query = genquery(idx)
        tweets, maxt = TweetSearch.SearchTweets(query, maxt)
        print(len(tweets))
        sleep(20)
        alltweets = alltweets + tweets
    print(len(alltweets))
    return alltweets


@shared_task(name='savetodb')
def savetweets(list):
    return "here"

# TODO try chord to forward results between tasks
@shared_task(name='gettweets')
def gettweets():
    search_task = subtask('searchfortweets').apply_async().id
    search_result = celery.AsyncResult(search_task)
    with allow_join_result():
        tweets = search_result.wait(timeout=None, interval=0.5)
    print(tweets)
    savetweets(tweets)
    return 0
