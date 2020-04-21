import flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from Application import _Config


def make_celery():
    # celery = Celery('tasks', broker=_Config.broker,
    #                backend=_Config.backend)
    # celery.conf.update(task_serializer=_Config.task_serializer,
    #                    accept_content=_Config.accept_content,
    #                    result_serializer=_Config.result_serializer,
    #                    timezone=_Config.timezone,
    #                    beat_schedule=_Config.CELERYBEAT_SCHEDULE,
    #                    enable_utc=_Config.enable_utc)
    celery = Celery()
    celery.config_from_object(_Config.DEV)
    return celery


celery = make_celery()
db = SQLAlchemy()
