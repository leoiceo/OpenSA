#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo
from __future__ import unicode_literals
import json,uuid
from django.http import HttpResponseRedirect, HttpResponse
from asset.models import Asset
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.utils.translation import ugettext as _
from django.conf import settings
from jobs.tasks import batch_task_func
from users.models import KeyManage
from django.utils.translation import ugettext_lazy as _
from jobs.models import TaskScheduling,ScriptsManage,TaskSchedulScripts
from audit.models import JobsResults,TaskSchedule
from django.urls import reverse_lazy
from jobs.models import ScriptsManage,UpdateConfigLog
from opensa.api import LoginPermissionRequired
from ..forms import ScritsManageForm
from users.models import UserProfile,Project

class BatchTask(LoginPermissionRequired,CreateView):
    """
    批量执行脚本
    """

    model = TaskScheduling
    form_class = ScritsManageForm
    template_name = 'jobs/batch_task.html'

    def get_context_data(self, **kwargs):
        try:
            project = self.request.session["project"]
            tasks_list = TaskScheduling.objects.filter(project__name=project)
            key_list = Project.objects.get(name=project).key.all()
            asset_list = Asset.objects.filter(project__name=project, status=1)
            context = {
                "jobs_active": "active",
                "batch_tasks_active": "active",
                "batch_task_active": "active",
                "tasks_list": tasks_list,
                "key_list": key_list,
                "asset_list": asset_list,
            }
        except Exception as e:
            context = {}

        kwargs.update(context)
        return super().get_context_data(**kwargs)

class BatchTaskProcess(LoginPermissionRequired,CreateView):

    model = TaskScheduling
    form_class = ScritsManageForm
    template_name = 'jobs/batch_task_process.html'

    def get_context_data(self, **kwargs):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None

        task_id = self.request.POST.get("task_id")
        timeout = self.request.POST.get("timeout")
        key_id = self.request.POST.get("key_id")
        asset_info = self.request.POST.get("asset_info")

        operator = UserProfile.objects.get(email=self.request.user).username
        project_id = Project.objects.get(name=project)
        key_obj = KeyManage.objects.get(id=key_id.strip('-'))
        task_obj = TaskScheduling.objects.get(id=task_id.strip('-'))
        args_list = []
        asset_list = asset_info.split(',')
        while '' in asset_list:
            asset_list.remove('')

        asset_count = len(asset_list)


        jr_obj = JobsResults.objects.create(type=3, operator=operator,key=key_obj,
                                            project=project_id,job_name=task_obj.name)
        from celery import group
        #yet = group(batch_scripts_func.s(jr_obj.id,script_id,timeout,input_args,i) for i in asset_list)(queue="batch_jobs_collect")
        yet = group(batch_task_func.s(jr_obj.id,task_id,timeout,i) for i in asset_list)()

        jobs_obj = JobsResults.objects.get(id=jr_obj.id)

        context = {
            "jobs_active": "active",
            "batch_tasks_active": "active",
            "batch_task_active": "active",
            "keymanage_obj": key_obj,
            "task_obj": task_obj,
            "args_list": args_list,
            "asset_count": asset_count,
            "jobs_obj": jobs_obj,
            "timeout": timeout,
            "yet": yet,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class BatchTaskApi(LoginPermissionRequired,ListView):

    def post(self, request, *args, **kwargs):
        jobid = request.POST.get("jobid")
        tsid = request.POST.get("tsid")

        try:
            if tsid is not None:
                ts_obj = TaskSchedule.objects.get(id=tsid.strip('-'))

                result_list = eval(ts_obj.result)
                result = '\\n'.join(eval(result_list))
                info = {
                    "status":True,
                    "data": {
                        "result": result.strip('"').replace("\n","\r\n").replace("\\n","\r\n"),
                    }
                }
                #print(info)
            else:
                jb_obj = JobsResults.objects.get(id=jobid.strip('-'))
                taskschedule_list = []
                success_count = 0
                total_time = 0
                jbts_obj = jb_obj.task_schedule.all()
                jobs_count = jbts_obj.count()

                for i in jbts_obj:
                    ts_dict = {}
                    ts_dict["DT_RowId"] = "{}".format(i.id)
                    ts_dict["id"] = "{}".format(i.id)
                    ts_dict["hostname"] = "{}".format(i.asset.hostname)
                    ts_dict["ip"] = i.asset.ip
                    ts_dict["status"] = i.status
                    ts_dict["total_time"] = i.total_time
                    taskschedule_list.append(ts_dict)

                    if i.status == "SUCCESS" or i.status == "FAILURE":
                        success_count += 1

                    if i.total_time:
                        total_time += i.total_time

                process = "{}".format(success_count / jobs_count * 100)

                info = {
                    "default":False,
                    "status":True,
                    "data": taskschedule_list,
                    "process": process,
                    "jobs_count": jobs_count,
                    "success_count": success_count,
                    "total_time": "{:.3f}".format(total_time)
                }

                if jbts_obj[0].status != "PROGRESS":
                    info["default"] = "{}".format(jbts_obj[0].id)

        except Exception as e:

            info = {"status": False, "error": "{}".format(e)}


        return HttpResponse(json.dumps(info), content_type='application/json')





