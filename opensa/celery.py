from __future__ import absolute_import, unicode_literals
import os,sys,time
from datetime import datetime
import django
from celery import Celery,platforms
from opensa import settings
from celery.signals import task_prerun, task_postrun #task_failure, after_task_publish, before_task_publish,task_success
from kombu import Exchange, Queue

app = Celery('opensa')
app.config_from_object('django.conf:settings', namespace='CELERY')
#app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
platforms.C_FORCE_ROOT = True
app.conf.timezone = 'Asia/Shanghai'

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTTING_KEY = 'default'

# /usr/local/python37/bin/python3.7 /usr/bin/celery --app=opensa.celery:app worker --loglevel=INFO -Q batch_jobs_collect -c 20
# /usr/local/python37/bin/python3.7 /usr/bin/celery -B -A opensa worker --loglevel=INFO
# 指定队列一次只能同时执行20个


# CELERY_QUEUES = (
#     Queue('default', exchange=Exchange('default',type="direct"), routing_key='default'),
#     Queue('batch_jobs_collect', exchange=Exchange('batch_jobs_collect',type="direct"), routing_key='jobs.tasks.batch_scripts_func'),
# )
#
# CELERY_ROUTES = {
#     'jobs.tasks.batch_scripts_func': {'queue': 'batch_jobs_collect', 'routing_key': 'batch_jobs_key'},
#     'default': {'queue': 'default', 'routing_key': 'default'},
#
# }
# app.conf.update(CELERY_QUEUES=CELERY_QUEUES,CELERY_ROUTES=CELERY_ROUTES)

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