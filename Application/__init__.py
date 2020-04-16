from flask import Flask
from . import _Config
from flask_sqlalchemy import SQLAlchemy
# from .models import db

# TODO implement login screen to launch and administer tasks

db = SQLAlchemy()

# def create_app():
Mouthful = Flask(__name__, instance_relative_config=True)
from CollectService.tasks import celery
Mouthful.celery = celery
Mouthful.config.from_object(_Config.dbconf)
db.init_app(Mouthful)
from .views import App
Mouthful.register_blueprint(App)
# return Mouthful
