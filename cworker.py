from Application import create_app, make_celery

Mouthful = create_app()
celery = make_celery(Mouthful)
Mouthful.celery = celery
Mouthful.app_context().push()
