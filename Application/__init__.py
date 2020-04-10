from flask import Flask 
from celery import Celery
from Application import _Config
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def make_celery(app):
    celery = Celery(app.import_name, backend=_Config.backend,
                    broker=_Config.broker)
    celery.conf.update(task_serializer=_Config.task_serializer,
                       accept_content=_Config.accept_content,
                       result_serializer=_Config.result_serializer,
                       timezone=_Config.timezone,
                       beat_schedule=_Config.CELERYBEAT_SCHEDULE,
                       enable_utc=_Config.enable_utc)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

    return celery


def create_app():
    Mouthful = Flask(__name__, instance_relative_config=True)

    from .views import App
    Mouthful.register_blueprint(App)
    return Mouthful
