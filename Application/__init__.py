from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from . import _Config
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'extensions')))


Mouthful = Flask(__name__, instance_relative_config=True)
Mouthful.config.from_object(_Config.DEV)
with Mouthful.app_context():
    from extensions import celery, db
    db.init_app(Mouthful)
    Mouthful.celery = celery
    sess = Session(Mouthful)
    from .views import App
    Mouthful.register_blueprint(App)
    from API.views import Api
    Mouthful.register_blueprint(Api)
