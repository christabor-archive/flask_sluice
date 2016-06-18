"""Celery stuff."""

from celery import Celery


def make_celery(app):
    """Create and inject celery app with flask instance data.

    Taken from http://flask.pocoo.org/docs/0.10/patterns/celery/
    """
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
