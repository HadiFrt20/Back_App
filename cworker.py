from Application import Mouthful, make_celery, celery_app

celery = make_celery(Mouthful, celery_app)
Mouthful.celery = celery
Mouthful.app_context().push()
