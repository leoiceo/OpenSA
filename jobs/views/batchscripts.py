#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo
from __future__ import unicode_literals
from django.shortcuts import HttpResponse
from django.views.generic import ListView, View, CreateView, UpdateView
from django.urls import reverse_lazy
from ..forms import ScritsManageForm
import json, datetime, logging,time
from asset.models import Asset
from jobs.models import ScriptsManage
from audit.models import JobsResults,TaskSchedule
from users.models import Project,UserProfile,KeyManage
from opensa.api import LoginPermissionRequired,OpenSaEncoder
from jobs.tasks import batch_scripts_func
import logging
logger = logging.getLogger(__name__)

class BatchScripts(LoginPermissionRequired,CreateView):

    model = ScriptsManage
    form_class = ScritsManageForm
    template_name = 'jobs/batch_scripts.html'
    success_url = reverse_lazy('jobs:batch_scripts')

    def get_context_data(self, **kwargs):
        try:
            project = self.request.session["project"]
            script_list = ScriptsManage.objects.filter(project__name=project)
            key_list = Project.objects.get(name=project).key.all()
            asset_list = Asset.objects.filter(project__name=project, status=1)
            context = {
                "jobs_active": "active",
                "batch_tasks_active": "active",
                "batch_script_active": "active",
                "script_list": script_list,
                "key_list": key_list,
                "asset_list": asset_list,
            }
        except Exception as e:
            context = {}

        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        sid = request.POST.get("sid")
        try:
            args = ScriptsManage.objects.get(id=sid.strip('-')).args

            if args:
                args_dict = eval(args)
                info = {"status": 1, "args_dict": args_dict}
            else:
                info = {"status": 0, "msg": "args is empty"}
        except Exception as e:
            info = {"status": 0, "msg": "args is empty:{}".format(e)}

        return HttpResponse(json.dumps(info), content_type='application/json')


class BatchScriptsProcess(LoginPermissionRequired,CreateView):

    model = ScriptsManage
    form_class = ScritsManageForm
    template_name = 'jobs/batch_scripts_process.html'

    def get_context_data(self, **kwargs):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None

        script_id = self.request.POST.get("script_id")
        key_id = self.request.POST.get("key_id")
        asset_info = self.request.POST.get("asset_info")
        timeout = self.request.POST.get("timeout")
        input_args = self.request.POST.getlist("input[]")

        operator = UserProfile.objects.get(email=self.request.user).username
        project_id = Project.objects.get(name=project)
        key_obj = KeyManage.objects.get(id=key_id.strip('-'))
        script_obj = ScriptsManage.objects.get(id=script_id.strip('-'))
        args_name = script_obj.args
        args_list = []
        asset_list = asset_info.split(',')
        while '' in asset_list:
            asset_list.remove('')

        asset_count = len(asset_list)

        if len(input_args) > 0:
            num = 0
            for k,v in eval(args_name).items():
                args_dict = {}
                args_dict["{}".format(v)] = input_args[num]
                num += 1
                args_list.append(args_dict)
        else:
            args_list = None

        jr_obj = JobsResults.objects.create(type=1, operator=operator,key=key_obj,
                                            project=project_id,job_name=script_obj.name)
        from celery import group
        yet = group(batch_scripts_func.s(jr_obj.id,script_id,timeout,input_args,i) for i in asset_list)()

        jobs_obj = JobsResults.objects.get(id=jr_obj.id)

        context = {
            "jobs_active": "active",
            "batch_tasks_active": "active",
            "batch_script_active": "active",
            "keymanage_obj": key_obj,
            "scriptsmanage_obj": script_obj,
            "args_list": args_list,
            "asset_count": asset_count,
            "jobs_obj": jobs_obj,
            "timeout": timeout,
            "yet": yet,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class TaskScheduleApi(LoginPermissionRequired,ListView):

    def post(self, request, *args, **kwargs):
        jobid = request.POST.get("jobid")
        tsid = request.POST.get("tsid")

        try:
            if tsid is not None:
                ts_obj = TaskSchedule.objects.get(id=tsid.strip('-'))
                info = {
                    "status":True,
                    "data": {
                        "result": ts_obj.result.encode('utf-8').decode('unicode_escape').strip('"').replace("\\n","\r\n"),
                    }
                }
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
