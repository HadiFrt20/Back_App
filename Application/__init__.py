from flask import Flask
from . import _Config
from CollectService.tasks import celery
from .views import App
from .models import db


Mouthful = Flask(__name__, instance_relative_config=True)
Mouthful.celery = celery
Mouthful.config.from_object(_Config.dbconf)
db.init_app(Mouthful)
Mouthful.register_blueprint(App)
