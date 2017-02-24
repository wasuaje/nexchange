from __future__ import absolute_import
from nexchange import settings
import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexchange.settings')

from django.conf import settings  # noqa

app = Celery('nexchange',
             broker=settings.REDIS_URL,
             include=['nexchange.tasks']
             )


# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
