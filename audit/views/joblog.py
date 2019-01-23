#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by leoiceo
from __future__ import absolute_import, unicode_literals
import subprocess,re
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, View, CreateView, UpdateView,TemplateView
from opensa.api import LoginPermissionRequired
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import HttpResponse
from audit.models import JobsResults,TaskSchedule
from django.db.models import Q
from opensa import settings
import json, datetime, logging
from asset.models import Asset
from jobs.models import ScheduledTasks,ScriptsManage
from users.models import Project,UserProfile,KeyManage
from pure_pagination import PageNotAnInteger, Paginator
from django_celery_results.models import TaskResult
from jobs.tasks import ExecutionCmd
import sys
import imp
imp.reload(sys)


class CrontadbList(LoginPermissionRequired,ListView):
    '''
    用户列表列表
    '''
    model = JobsResults
    template_name = "audit/jobs_logs_crontab.html"

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
        loginlog_list = p.page(page)
        context = {
            "audit_active": "active",
            "jobs_logs": "active",
            "loginlog_list": loginlog_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = JobsResults.objects.filter(type=4,project__name=self.get_project()).exclude(task_schedule__id=None)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        operator = UserProfile.objects.get(email=self.request.user)
        if self.request.GET.get('name') and operator.is_superuser:
            query = self.request.GET.get('name', None)
            self.queryset = self.queryset.filter(operator=query).order_by('-start_time')
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(start_time__gte=date_from).filter(start_time__lte=end).order_by(
                    '-start_time')
        else:
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(start_time__gte=date_from).filter(start_time__lte=end).order_by(
                    '-start_time')
            else:
                self.queryset = self.queryset.order_by('-start_time')

        return self.queryset


class CrontabResult(LoginPermissionRequired, TemplateView):

    model = JobsResults
    template_name = "audit/jobs_crontab_result.html"

    def get_project(self):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        return project

    def get_context_data(self, **kwargs):
        context = {
            "audit_active": "active",
            "jobs_logs": "active",
            "project": self.get_project(),
            "get_id": self.request.GET.get('id', '')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def post(self, request):
        flag = True
        job_list,result_list = [], []
        id = request.POST.get('id')
        task_id = request.POST.get('task_id')
        jobsresults = JobsResults.objects.get(id=id.strip('-'))
        job = jobsresults.task_schedule.all()
        if task_id:
            jobs = job.filter(id=task_id.strip('-'))
        else:
            jobs = job.order_by('-start_time')
        for i, element in enumerate(jobs):
            job_dict, result_dict = {},{}
            job_dict["DT_RowId"] = "{}".format(element.id)
            job_dict['project'] = self.get_project()
            job_dict['ip'] = element.asset.ip
            job_dict['cmd'] = jobsresults.job_name
            job_dict['status'] = element.status
            job_dict['start_time'] = '{}s'.format(element.start_time)
            job_dict['total_time'] = '{}s'.format(element.total_time)
            job_dict['operator'] = jobsresults.operator
            result_dict['ip'] = element.asset.ip
            result = element.result.encode('utf-8').decode('unicode_escape').strip('"')
            result_dict['result'] = '{}'.format(result)
            result_dict['log'] = '{}'.format(element.log)
            if element.status == "PROGRESS":
                flag = False
            result_list.append(result_dict)
            job_list.append(job_dict)
        info = {'flag':flag, 'data':job_list,'res':result_list}
        return HttpResponse(json.dumps(info), content_type='application/json')




class ExecutionList(LoginPermissionRequired,ListView):

    model = JobsResults
    template_name = "audit/jobs_logs_command.html"

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
        loginlog_list = p.page(page)
        context = {
            "audit_active": "active",
            "jobs_logs": "active",
            "loginlog_list": loginlog_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = JobsResults.objects.filter(type=0,project__name=self.get_project()).exclude(task_schedule__id=None)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        operator = UserProfile.objects.get(email=self.request.user)
        if self.request.GET.get('name') and operator.is_superuser:
            query = self.request.GET.get('name', None)
            self.queryset = self.queryset.filter(operator=query).order_by('-start_time')
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(start_time__gte=date_from).filter(start_time__lte=end).order_by(
                    '-start_time')
        else:
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(start_time__gte=date_from).filter(start_time__lte=end).order_by(
                    '-start_time')
            else:
                self.queryset = self.queryset.order_by('-start_time')

        return self.queryset


class ExecutionResult(LoginPermissionRequired, TemplateView):

    model = JobsResults
    template_name = "audit/jobs_command_result.html"


    def get_project(self):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        return project

    def get_context_data(self, **kwargs):
        context = {
            "audit_active": "active",
            "jobs_logs": "active",
            "project": self.get_project(),
            "get_id": self.request.GET.get('id', '')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def post(self, request):
        flag = True
        job_list,result_list = [], []
        id = request.POST.get('id')
        task_id = request.POST.get('task_id')
        jobsresults = JobsResults.objects.get(id=id.strip('-'))
        job = jobsresults.task_schedule.all()
        if task_id:
            jobs = job.filter(id=task_id.strip('-'))
        else:
            jobs = job.order_by('-start_time')
        for i, element in enumerate(jobs):
            job_dict, result_dict = {},{}
            job_dict["DT_RowId"] = "{}".format(element.id)
            job_dict['project'] = self.get_project()
            job_dict['ip'] = element.asset.ip
            job_dict['cmd'] = jobsresults.job_name
            job_dict['status'] = element.status
            job_dict['start_time'] = '{}s'.format(element.start_time)
            job_dict['total_time'] = '{}s'.format(element.total_time)
            job_dict['operator'] = jobsresults.operator
            result_dict['ip'] = element.asset.ip
            result = element.result.encode('utf-8').decode('unicode_escape').strip('"')
            result_dict['result'] = '{}'.format(result)
            result_dict['log'] = '{}'.format(element.log)
            if element.status == "PROGRESS":
                flag = False
            result_list.append(result_dict)
            job_list.append(job_dict)
        info = {'flag':flag, 'data':job_list,'res':result_list}
        return HttpResponse(json.dumps(info), content_type='application/json')



class ScriptsList(LoginPermissionRequired,ListView):

    model = JobsResults
    template_name = "audit/jobs_logs_scripts.html"

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
        loginlog_list = p.page(page)
        context = {
            "audit_active": "active",
            "jobs_logs": "active",
            "loginlog_list": loginlog_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = JobsResults.objects.filter(type=1,project__name=self.get_project()).exclude(task_schedule__id=None)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        operator = UserProfile.objects.get(email=self.request.user)
        if self.request.GET.get('name') and operator.is_superuser:
            query = self.request.GET.get('name', None)
            self.queryset = self.queryset.filter(operator=query).order_by('-start_time')
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(start_time__gte=date_from).filter(start_time__lte=end).order_by(
                    '-start_time')
        else:
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(start_time__gte=date_from).filter(start_time__lte=end).order_by(
                    '-start_time')
            else:
                self.queryset = self.queryset.order_by('-start_time')

        return self.queryset

class ScriptsResult(LoginPermissionRequired, TemplateView):

    model = JobsResults
    template_name = "audit/jobs_scripts_result.html"

    def get_project(self):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        return project

    def get_context_data(self, **kwargs):
        context = {
            "audit_active": "active",
            "jobs_logs": "active",
            "project": self.get_project(),
            "get_id": self.request.GET.get('id', '')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def post(self, request):
        flag = True
        job_list,result_list = [], []
        id = request.POST.get('id')
        task_id = request.POST.get('task_id')
        jobsresults = JobsResults.objects.get(id=id.strip('-'))
        job = jobsresults.task_schedule.all()
        if task_id:
            jobs = job.filter(id=task_id.strip('-'))
        else:
            jobs = job.order_by('-start_time')
        for i, element in enumerate(jobs):
            job_dict, result_dict = {},{}
            job_dict["DT_RowId"] = "{}".format(element.id)
            job_dict['project'] = self.get_project()
            job_dict['ip'] = element.asset.ip
            job_dict['cmd'] = jobsresults.job_name
            job_dict['status'] = element.status
            job_dict['start_time'] = '{}s'.format(element.start_time)
            job_dict['total_time'] = '{}s'.format(element.total_time)
            job_dict['operator'] = jobsresults.operator
            result_dict['ip'] = element.asset.ip
            result = element.result.encode('utf-8').decode('unicode_escape').strip('"').replace("\\n","\r\n")
            result_dict['result'] = '{}'.format(result)
            result_dict['log'] = '{}'.format(element.log)
            if element.status == "PROGRESS":
                flag = False
            result_list.append(result_dict)
            job_list.append(job_dict)
        info = {'flag':flag, 'data':job_list,'res':result_list}
        return HttpResponse(json.dumps(info), content_type='application/json')


class SchedulingList(LoginPermissionRequired,ListView):

    model = JobsResults
    template_name = "audit/jobs_logs_scheduling.html"

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
        loginlog_list = p.page(page)
        context = {
            "audit_active": "active",
            "jobs_logs": "active",
            "loginlog_list": loginlog_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = JobsResults.objects.filter(type=3,project__name=self.get_project()).exclude(task_schedule__id=None)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        operator = UserProfile.objects.get(email=self.request.user)
        if self.request.GET.get('name') and operator.is_superuser:
            query = self.request.GET.get('name', None)
            self.queryset = self.queryset.filter(operator=query).order_by('-start_time')
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(start_time__gte=date_from).filter(start_time__lte=end).order_by(
                    '-start_time')
        else:
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(start_time__gte=date_from).filter(start_time__lte=end).order_by(
                    '-start_time')
            else:
                self.queryset = self.queryset.order_by('-start_time')

        return self.queryset

class SchedulingResult(LoginPermissionRequired, TemplateView):

    model = JobsResults
    template_name = "audit/jobs_scheduling_result.html"

    def get_project(self):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        return project

    def get_context_data(self, **kwargs):
        context = {
            "audit_active": "active",
            "jobs_logs": "active",
            "project": self.get_project(),
            "get_id": self.request.GET.get('id', '')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def post(self, request):
        flag = True
        job_list,result_list = [], []
        id = request.POST.get('id')
        task_id = request.POST.get('task_id')
        jobsresults = JobsResults.objects.get(id=id.strip('-'))
        job = jobsresults.task_schedule.all()
        if task_id:
            jobs = job.filter(id=task_id.strip('-'))
        else:
            jobs = job.order_by('-start_time')
        for i, element in enumerate(jobs):
            job_dict, result_dict = {},{}
            job_dict["DT_RowId"] = "{}".format(element.id)
            job_dict['project'] = self.get_project()
            job_dict['ip'] = element.asset.ip
            job_dict['cmd'] = jobsresults.job_name
            job_dict['status'] = element.status
            job_dict['start_time'] = '{}s'.format(element.start_time)
            job_dict['total_time'] = '{}s'.format(element.total_time)
            job_dict['operator'] = jobsresults.operator
            result_dict['ip'] = element.asset.ip
            result = element.result.encode('utf-8').decode('unicode_escape').strip('"').replace("\\n","\r\n")
            result_dict['result'] = '{}'.format(result)
            result_dict['log'] = '{}'.format(element.log)
            if element.status == "PROGRESS":
                flag = False
            result_list.append(result_dict)
            job_list.append(job_dict)
        info = {'flag':flag, 'data':job_list,'res':result_list}
        return HttpResponse(json.dumps(info), content_type='application/json')


class BatchFilesList(LoginPermissionRequired,ListView):

    model = JobsResults
    template_name = "audit/jobs_logs_files.html"

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
        loginlog_list = p.page(page)
        context = {
            "audit_active": "active",
            "jobs_logs": "active",
            "loginlog_list": loginlog_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = JobsResults.objects.filter(type=2,project__name=self.get_project()).exclude(task_schedule__id=None)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        operator = UserProfile.objects.get(email=self.request.user)
        if self.request.GET.get('name') and operator.is_superuser:
            query = self.request.GET.get('name', None)
            self.queryset = self.queryset.filter(operator=query).order_by('-start_time')
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(start_time__gte=date_from).filter(start_time__lte=end).order_by(
                    '-start_time')
        else:
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(start_time__gte=date_from).filter(start_time__lte=end).order_by(
                    '-start_time')
            else:
                self.queryset = self.queryset.order_by('-start_time')

        return self.queryset

class BatchFilesResult(LoginPermissionRequired, TemplateView):

    model = JobsResults
    template_name = "audit/jobs_files_result.html"

    def get_project(self):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        return project

    def get_context_data(self, **kwargs):
        context = {
            "audit_active": "active",
            "jobs_logs": "active",
            "project": self.get_project(),
            "get_id": self.request.GET.get('id', '')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def post(self, request):
        flag = True
        job_list,result_list = [], []
        id = request.POST.get('id')
        task_id = request.POST.get('task_id')
        jobsresults = JobsResults.objects.get(id=id.strip('-'))
        job = jobsresults.task_schedule.all()
        if task_id:
            jobs = job.filter(id=task_id.strip('-'))
        else:
            jobs = job.order_by('-start_time')
        for i, element in enumerate(jobs):
            job_dict, result_dict = {},{}
            job_dict["DT_RowId"] = "{}".format(element.id)
            job_dict['project'] = self.get_project()
            job_dict['ip'] = element.asset.ip
            job_dict['cmd'] = jobsresults.remote_path
            job_dict['status'] = element.status
            job_dict['start_time'] = '{}s'.format(element.start_time)
            job_dict['total_time'] = '{}s'.format(element.total_time)
            job_dict['operator'] = jobsresults.operator
            result_dict['ip'] = element.asset.ip
            result = element.result.encode('utf-8').decode('unicode_escape').strip('"').replace("\\n","\r\n")
            result_dict['result'] = '{}'.format(result)
            result_dict['log'] = '{}'.format(element.log)
            if element.status == "PROGRESS":
                flag = False
            result_list.append(result_dict)
            job_list.append(job_dict)
        info = {'flag':flag, 'data':job_list,'res':result_list}
        return HttpResponse(json.dumps(info), content_type='application/json')