from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

####
# solved problem:
# https://stackoverflow.com/questions/45744992/celery-raises-valueerror-not-enough-values-to-unpack
# On Windows worker stars by: 'celery -A <module> worker -l info -P eventlet'
# rather than 'celery -A proj worker -l info'
# or (better)
# add a string to this file: 'os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1') # only use on Windows!'
####

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Collag.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1') # only use on Windows!

app = Celery('Collag')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

