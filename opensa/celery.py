from __future__ import absolute_import, unicode_literals
import os,sys
import django
from celery import Celery,platforms
from opensa import settings
from celery.signals import task_prerun, task_postrun
from kombu import Exchange, Queue

app = Celery('opensa')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
platforms.C_FORCE_ROOT = True
app.conf.timezone = 'Asia/Shanghai'

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTTING_KEY = 'default'


BaseDir = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-2])
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opensa.settings')
sys.path.append(BaseDir)
django.setup()

from audit.models import TaskSchedule
from django_celery_results.models import TaskResult

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@task_prerun.connect
def start_task_timer(task_id, task, **kw):
    TaskSchedule.objects.create(task_id=task_id)

@task_postrun.connect
def end_task_timer(task_id, task, **kw):
    ts_obj = TaskSchedule.objects.get(task_id=task_id)
    tr_obj = TaskResult.objects.get(task_id=task_id)
    end_time = (tr_obj.date_done - ts_obj.start_time).total_seconds()# / 1000000
    ts_obj.total_time = "{:.3f}".format(end_time)
    ts_obj.save()