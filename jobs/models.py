# !/usr/bin/env python
# ~*~ coding: utf-8 ~*~
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_celery_beat.models import  CrontabSchedule, PeriodicTask, IntervalSchedule
from django_celery_results.models import TaskResult
from django.core.exceptions import MultipleObjectsReturned, ValidationError
# Create your models here.
import uuid

class ScriptsManage(models.Model):
    SCRIPT_TYPE=(
        (0,"shell"),
        (1,"python"),
        (2,"bat"),
    )
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=64,unique=True,verbose_name=_("Script Name"))
    type = models.IntegerField(choices=SCRIPT_TYPE,verbose_name=_("Script Type"))
    args = models.CharField(max_length=255,null=True,blank=True,verbose_name=_("Script Args"))
    content = models.TextField(verbose_name=_("Script Content"))
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Script Comment'))
    create_date = models.DateTimeField(auto_now_add=True,null=True,blank=True,verbose_name=_("Create By"))
    create_user = models.ForeignKey(to="users.UserProfile", blank=True, null=True, on_delete=models.SET_NULL,verbose_name=_("Create User"))
    project = models.ForeignKey(to="users.Project",blank=True,null=True,on_delete=models.SET_NULL,verbose_name=_("Project Name"))
    update = models.ManyToManyField(to="UpdateConfigLog",blank=True,verbose_name=_("Update Log"))

    class Meta:
        db_table = "scriptsmanage"
        verbose_name = _("Scripts Manage")
        verbose_name_plural = _("Scripts Manage")

    def __str__(self):
        return self.name

class UpdateConfigLog(models.Model):
    id = models.UUIDField(default=uuid.uuid4,primary_key=True)
    type = models.CharField(max_length=32, null=True, blank=True, verbose_name=_("Config Type"))
    content = models.TextField(verbose_name=_("Config Histroy Content"))
    update_date = models.DateTimeField(auto_now_add=True,null=True, blank=True, verbose_name=_("Update By"))
    update_user = models.ForeignKey(to="users.UserProfile", blank=True, null=True, on_delete=models.SET_NULL,
                                    verbose_name=_("Update User"))
    class Meta:
        db_table = "updateconfiglog"
        verbose_name = _("Update Config Log")
        verbose_name_plural = _("Update Config Log")

    def __str__(self):
        return self.id

class ScheduledTasks(models.Model):
    project = models.ForeignKey(to="users.Project", blank=True, null=True,
                                on_delete=models.SET_NULL, verbose_name=_("User Project"))
    scritps = models.ForeignKey(to="ScriptsManage", blank=True, null=True,
                                on_delete=models.SET_NULL, verbose_name=_("Scritps Name"))
    scheduling = models.ForeignKey(to="TaskScheduling", blank=True, null=True,
                                on_delete=models.SET_NULL, verbose_name=_("Task Scheduling Name"))
    create_date = models.DateTimeField(blank=True, auto_now_add=True, verbose_name=_("Create By"))
    create_user = models.ForeignKey(to="users.UserProfile", blank=True, null=True,
                                on_delete=models.SET_NULL, verbose_name=_("Create User"))
    scheduled = models.ForeignKey(to="django_celery_beat.PeriodicTask", blank=True, null=True, related_name='scheduled_task',
                                on_delete=models.SET_NULL, verbose_name=_("Scheduled Name"))
    key = models.ForeignKey(to="users.KeyManage", blank=True, null=True,
                                on_delete=models.SET_NULL, verbose_name=_("Scheduled Name"))
    asset = models.ManyToManyField(to="asset.Asset", blank=True, related_name='asset_task', verbose_name=_("Asset"))


    class Meta:
        db_table = "scheduledtasks"
        verbose_name = _("Scheduled Tasks")
        verbose_name_plural = verbose_name





class TaskScheduling(models.Model):
    '''
    任务编排
    '''
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=128,blank=True,null=True,verbose_name=_("Task Name"))
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Orchestration Comment'))
    create_date = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_("Create By"))
    create_user = models.ForeignKey(to="users.UserProfile", blank=True, null=True, on_delete=models.SET_NULL,
                                    verbose_name=_("Create User"))
    project = models.ForeignKey(to="users.Project", blank=True, null=True, on_delete=models.SET_NULL,
                                verbose_name=_("Project Name"))
    task_scripts = models.ManyToManyField(to="TaskSchedulScripts",blank=True,verbose_name="Task Schedul Scripts")

    class Meta:
        db_table = "taskscheduling"
        verbose_name = _("Task Scheduling")
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name



class TaskSchedulScripts(models.Model):
    '''
    任务编排脚本
    '''

    TASKSCHEDULING_STATUS = (
        (0, "失败退出"),
        (1, "失败继续执行"),
        # (2, "执行后暂停"),
    )
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    level = models.IntegerField(blank=True,null=True,verbose_name="Execution order")
    status = models.IntegerField(choices=TASKSCHEDULING_STATUS,default=0,verbose_name="Execution Status")
    delaytime = models.IntegerField(blank=True,null=True,verbose_name="Delay Time Execution")
    scripts = models.ForeignKey(to="ScriptsManage", blank=True, null=True,
                                on_delete=models.SET_NULL, verbose_name=_("Scritps Name"))

    class Meta:
        db_table = "taskschedulscripts"
        verbose_name = _("Task Schedul Scripts")
        verbose_name_plural = verbose_name



