#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by leoiceo
from __future__ import absolute_import, unicode_literals
import subprocess,re
from django.http import JsonResponse
from django.views.generic import ListView, View, CreateView, UpdateView,TemplateView
from opensa.api import LoginPermissionRequired
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import HttpResponse
from audit.models import JobsResults,TaskSchedule
from django.db.models import Q
from opensa import settings
import json, datetime, logging
from asset.models import Asset
from users.models import Project,UserProfile,KeyManage
from pure_pagination import PageNotAnInteger, Paginator
from jobs.tasks import ExecutionCmd
import sys
import imp
imp.reload(sys)


class CmdListAll(LoginPermissionRequired,ListView):

    model = Asset
    template_name = "jobs/cmd.html"

    def get_project(self):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        return project

    def get_context_data(self, **kwargs):

        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger as e:
            page = 1
        p = Paginator(self.queryset, getattr(settings, 'DISPLAY_PER_PAGE'), request=self.request)
        asset_list = p.page(page)
        pro = Project.objects.get(name=self.get_project())
        key = pro.key.all()
        context = {
            "jobs_active": "active",
            "batch_tasks_active": "active",
            "batch_cmd_active": "active",
            "asset_list": asset_list,
            "key_list":key
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = super().get_queryset()
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        product = self.request.GET.get('id')
        asset = self.request.GET.get('asset')
        if project:
            if self.request.GET.get('name'):
                query = self.request.GET.get('name', None)
                self.queryset = self.queryset.filter(project__name=project).filter(
                    Q(hostname__icontains=query) |
                    Q(ip__icontains=query) |
                    Q(other_ip__icontains=query)
                ).order_by('-id')
            else:
                if product:
                    self.queryset = self.queryset.filter(project__name=project,product__id=product)
                elif asset:
                    self.queryset = self.queryset.filter(project__name=project, id=asset.strip('-'))
                else:
                    self.queryset = self.queryset.filter(project__name=project).order_by('id')
        else:
            self.queryset = self.queryset.filter(project__name=project).order_by('id')
        return self.queryset

    def post(self, request, *args, **kwargs):
        ret = {'status': True, 'error': None, 'id': None}
        operator = UserProfile.objects.get(email=self.request.user).username
        pro = Project.objects.get(name=self.get_project())
        try:
            cmd = self.request.POST.get('cmd', '')
            key = self.request.POST.get('key', '')
            asset = self.request.POST.getlist('asset[]', '')
            key_obj = KeyManage.objects.get(id=key.strip('-'))
            jr_obj = JobsResults.objects.create(type=0, operator=operator, key=key_obj,
                                                job_name='{}'.format(cmd),project=pro)
            ret['id'] = '{}'.format(jr_obj.id)
            from celery import group
            group(ExecutionCmd.s(jr_obj.id, i, cmd) for i in asset)()
        except Exception as e:
            ret['status'] = False
            ret['error'] = "{}".format(e)
        finally:
            return HttpResponse(json.dumps(ret))



class BatchCommandExecute(LoginPermissionRequired,View):

    model = Asset

    def post(self, request):
        cmd = request.POST.get('cmd', '')
        commandall = subprocess.getoutput(
            "PATH=$PATH:./:/usr/lib:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin;for dir in $(echo $PATH |sed 's/:/ /g');do ls $dir;done").strip().split(
            '\n')
        commandmatch = []
        for command in commandall:
            match = re.search('^{0}.*'.format(cmd), command)
            if match:
                commandmatch.append(match.group())
            else:
                continue
        return JsonResponse({'status': True, 'message': list(set(commandmatch))})

class BatchExecutionResult(LoginPermissionRequired, TemplateView):

    model = Asset
    template_name = "jobs/execution-result.html"

    def get_context_data(self, **kwargs):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        context = {
            "jobs_active": "active",
            "batch_tasks_active": "active",
            "batch_cmd_active": "active",
            "project": project,
            "get_id": self.request.GET.get('id', '')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def post(self, request):
        flag = True
        job_list,result_list = [], []
        id = request.POST.get('id')
        jobsresults = JobsResults.objects.get(id=id.strip('-'))
        job = jobsresults.task_schedule.all()
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        for i, element in enumerate(job):
            job_dict, result_dict = {},{}
            job_dict["DT_RowId"] = "{}".format(element.id)
            job_dict['serial number'] = i+1
            job_dict['project'] = project
            job_dict['ip'] = element.asset.ip
            job_dict['cmd'] = jobsresults.job_name
            job_dict['status'] = element.status
            try:
                jsons = json.loads(element.result)
                plan = jsons['current']
                job_dict['plan'] = '<div class="progress-bar progress-bar-striped active update-progressbar" ' \
                                   'role="progressbar" aria-valuenow="45" aria-valuemin="0" aria-valuemax="100" style="width: {0}">{0}</div>'.format(plan)
            except Exception as e:
                if element.status == "SUCCESS" or element.status == "FAILURE":
                    job_dict['plan'] = '<div class="progress-bar progress-bar-striped active update-progressbar" ' \
                                   'role="progressbar" aria-valuenow="45" aria-valuemin="0" aria-valuemax="100" style="width: 100%">100%</div>'
                else:
                    job_dict['plan'] = '<div class="progress-bar progress-bar-striped active update-progressbar" ' \
                                       'role="progressbar" aria-valuenow="45" aria-valuemin="0" aria-valuemax="100" style="width: 1%">1%</div>'

            job_dict['time'] = '{}s'.format(element.total_time)
            job_dict['operator'] = jobsresults.operator

            result_dict['ip'] = element.asset.ip

            try:
                jsons = json.loads(element.result)
                plan = jsons['current']
                result_dict['result'] = ''
                result_dict['log'] = ''
            except Exception as e:
                result = element.result.encode('utf-8').decode('unicode_escape').strip('"')
                result_dict['result'] = '{}'.format(result)
                result_dict['log'] = '{}'.format(element.log)
            if element.status == "PROGRESS":
                flag = False
            result_list.append(result_dict)
            job_list.append(job_dict)
        info = {'flag':flag, 'data':job_list,'res':result_list}
        return HttpResponse(json.dumps(info), content_type='application/json')


class BatchExecutionResultFlush(LoginPermissionRequired, View):

    model = Asset

    def post(self, request):
        flag = True
        job_list,result_list = [], []
        id = request.POST.get('id')
        task_id = request.POST.get('task_id')
        jobsresults = JobsResults.objects.get(id=id.strip('-'))
        job = jobsresults.task_schedule.all()
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        for i, element in enumerate(job):
            job_dict = {}
            job_dict['serial number'] = i+1
            job_dict['project'] = project
            job_dict['ip'] = element.asset.ip
            job_dict['cmd'] = jobsresults.job_name
            job_dict['status'] = element.status
            try:
                jsons = json.loads(element.result)
                plan = jsons['current']
                job_dict['plan'] = '<div class="progress-bar progress-bar-striped active update-progressbar" ' \
                                   'role="progressbar" aria-valuenow="45" aria-valuemin="0" aria-valuemax="100" style="width: {0}">{0}</div>'.format(plan)
            except Exception as e:
                if element.status == "SUCCESS" or element.status == "FAILURE":
                    job_dict['plan'] = '<div class="progress-bar progress-bar-striped active update-progressbar" ' \
                                   'role="progressbar" aria-valuenow="45" aria-valuemin="0" aria-valuemax="100" style="width: 100%">100%</div>'
                else:
                    job_dict['plan'] = '<div class="progress-bar progress-bar-striped active update-progressbar" ' \
                                       'role="progressbar" aria-valuenow="45" aria-valuemin="0" aria-valuemax="100" style="width: 1%">1%</div>'

            job_dict['time'] = '{}s'.format(element.total_time)
            job_dict['operator'] = jobsresults.operator
            if element.status == "PROGRESS":
                flag = False
            job_list.append(job_dict)
        for i in job.filter(id=task_id.strip('-')):
            result_dict = {}
            result_dict['ip'] = i.asset.ip
            try:
                jsons = json.loads(i.result)
                plan = jsons['current']
                result_dict['result'] = ''
                result_dict['log'] = ''
            except Exception as e:
                result = i.result.encode('utf-8').decode('unicode_escape').strip('"')
                result_dict['result'] = '{}'.format(result)
                result_dict['log'] = '{}'.format(i.log)
            result_list.append(result_dict)

        info = {'flag':flag, 'data':job_list,'res':result_list}

        return HttpResponse(json.dumps(info), content_type='application/json')



