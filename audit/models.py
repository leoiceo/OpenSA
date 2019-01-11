#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
from django.utils.translation import ugettext_lazy as _
from django.db import models
import uuid,json
from django_celery_results.models import TaskResult
# Create your models here.

LOGINTYPE = (
    (0, 'GET'),
    (1, 'POST'),
)

class RequestRecord(models.Model):
    username = models.ForeignKey(to="users.UserProfile", verbose_name=_("UserName"), blank=True, null=True,
                                 on_delete=models.SET_NULL)
    ipaddr = models.GenericIPAddressField(verbose_name=_("Client Address"))
    datetime = models.DateTimeField(auto_now_add=True, verbose_name=_("Request Date Time"))
    type = models.IntegerField(choices=LOGINTYPE, verbose_name=_("Request Type"))
    get_full_path = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("Request Full Path"))
    post_body = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("Request Post Body"))

    class Meta:
        db_table = "requestrecord"
        verbose_name = _('Request Record')
        verbose_name_plural = _('Request Record')

    def __str__(self):
        return self.username

JOBS_TYPE=(
    (0,_("Batch Cmd")),
    (1,_("Batch Scripts")),
    (2,_("File Distribution")),
    (3,_("Batch Task")),
    (4,_("Crontab Task")),
)
class JobsResults(models.Model):
    """
    异步任务状态信息
    job name：任务名称、脚本名、命令名,文件远程路径
    """
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    type = models.IntegerField(choices=JOBS_TYPE, blank=True, null=True, verbose_name=_("Jobs Type"))
    start_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Start Time"))
    job_name = models.CharField(max_length=128,blank=True, null=True, verbose_name=_("Job Name"))
    remote_path = models.CharField(max_length=128, blank=True, null=True, verbose_name=_("Remote Path"))
    operator = models.CharField(max_length=64,null=True, blank=True, verbose_name=_('Operator'))
    key = models.ForeignKey(to="users.KeyManage",blank=True,null=True, verbose_name=_('Jobs Exec Key'),on_delete=models.SET_NULL)
    task_schedule = models.ManyToManyField(to='TaskSchedule',blank=True, verbose_name=_("Jobs Schedule"))
    project = models.ForeignKey(to="users.Project", null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Jobs Project"))

    class Meta:
        db_table = "jobsresults"
        verbose_name = _("Jobs Results")
        verbose_name_plural = _("Jobs Results")

    def __str__(self):
        return self.id

class TaskSchedule(models.Model):
    """
    type: 任务清单
    """
    # version = models.IntegerField(blank=True, null=True,verbose_name=_("Version"))
    # appname = models.IntegerField(blank=True, null=True,verbose_name=_("App Name"))
    # port = models.IntegerField(blank=True, null=True,verbose_name=_("App Port"))

    id = models.UUIDField(default=uuid.uuid4,primary_key=True)
    task_id = models.UUIDField(max_length=255, blank=True, null=True, verbose_name=_('Task ID'), unique=True)
    log = models.CharField(max_length=128,blank=True,null=True,verbose_name=_("Log Info"))
    #result = models.TextField(blank=True,null=True,verbose_name=_("Task Result"))
    start_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Start Time"))
    total_time = models.FloatField(blank=True, null=True,verbose_name=_("Total Time"))
    asset = models.ForeignKey(to="asset.Asset", blank=True, null=True, on_delete=models.SET_NULL,
                                verbose_name=_("Tasks Asset"))

    @property
    def status(self):
        status = TaskResult.objects.get(task_id=self.task_id).status
        return status

    @property
    def result(self):
        result = TaskResult.objects.get(task_id=self.task_id).result
        return result

    @property
    def plan(self):
        try:
            current = TaskResult.objects.get(task_id=self.task_id).result
            jsons = json.loads(current)
            plan = jsons['current']
        except Exception as e:
            plan = ''
        return plan

    @property
    def operator(self):
        current = TaskSchedule.objects.get(task_id=self.task_id).jobsresults_set.all()
        return current


    class Meta:
        db_table = "taskschedule"
        verbose_name = _("Task Schedule Table")
        verbose_name_plural = _("Task Schedule Table")

    def __str__(self):
        return self.id

class PasswordChangeLog(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.CharField(max_length=128, verbose_name=_('User'))
    change_by = models.CharField(max_length=128, verbose_name=_("Change by"))
    remote_addr = models.CharField(max_length=15, verbose_name=_("Remote addr"), blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "passwordchangelog"
        verbose_name = _("Password Change Log")
        verbose_name_plural = _("Password Change Log")

    def __str__(self):
        return "{} change {}'s password".format(self.change_by, self.user)
