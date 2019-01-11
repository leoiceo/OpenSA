#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo
from __future__ import unicode_literals
from django.shortcuts import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View, CreateView, UpdateView
from django.urls import reverse_lazy
from ..forms import CrontabScheduleForm, PeriodicTasksForm,IntervalScheduleForm,PeriodicTasksFormUpdate
from django_celery_beat.models import  CrontabSchedule, PeriodicTask, IntervalSchedule
from django.utils.translation import ugettext_lazy as _
import json, datetime, logging
from jobs.models import ScheduledTasks,ScriptsManage,TaskScheduling
from users.models import Project,UserProfile,KeyManage
from audit.models import TaskSchedule,JobsResults


class CrontabsListAll(LoginRequiredMixin, ListView):


    template_name = "jobs/crontab-list.html"
    model = CrontabSchedule
    context_object_name = "crontabs_list"
    queryset = CrontabSchedule.objects.all()
    ordering = ('-id',)

    def get_context_data(self, **kwargs):
        context = {
            "jobs_active": "active",
            "crontab_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class CrontabsAdd(LoginRequiredMixin, CreateView):

    model = CrontabSchedule
    form_class = CrontabScheduleForm
    template_name = 'jobs/crontab-add-update.html'
    success_url = reverse_lazy('jobs:crontabs_list')

    def get_context_data(self, **kwargs):
        context = {
            "jobs_active": "active",
            "crontab_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class CrontabsUpdate(LoginRequiredMixin, UpdateView):


    model = CrontabSchedule
    form_class = CrontabScheduleForm
    template_name = 'jobs/crontab-add-update.html'
    success_url = reverse_lazy('jobs:crontabs_list')

    def get_context_data(self, **kwargs):
        context = {
            "jobs_active": "active",
            "crontab_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class CrontabsAllDel(LoginRequiredMixin, View):

    model = CrontabSchedule

    @staticmethod
    def post(request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                ids = request.POST.get('nid', None)
                CrontabSchedule.objects.get(id=ids).delete()
            else:
                ids = request.POST.getlist('id', None)
                CrontabSchedule.objects.filter(id__in=ids).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = _('Deletion error，{}'.format(e))
        finally:
            return HttpResponse(json.dumps(ret))


class IntervalsListAll(LoginRequiredMixin, ListView):


    template_name = 'jobs/intervals-list.html'
    model = IntervalSchedule
    context_object_name = "intervals_list"
    queryset = IntervalSchedule.objects.all()
    ordering = ('-id',)

    def get_context_data(self, **kwargs):
        context = {
            "jobs_active": "active",
            "interval_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class IntervalsAdd(LoginRequiredMixin, CreateView):

    model = IntervalSchedule
    form_class = IntervalScheduleForm
    template_name = 'jobs/intervals-add-update.html'
    success_url = reverse_lazy('jobs:intervals_list')

    def get_context_data(self, **kwargs):
        context = {
            "jobs_active": "active",
            "interval_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class IntervalsUpdate(LoginRequiredMixin, UpdateView):


    model = IntervalSchedule
    form_class = IntervalScheduleForm
    template_name = 'jobs/intervals-add-update.html'
    success_url = reverse_lazy('jobs:intervals_list')


    def get_context_data(self, **kwargs):
        context = {
            "jobs_active": "active",
            "interval_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class IntervalsAllDel(LoginRequiredMixin, View):

    model = IntervalSchedule

    @staticmethod
    def post(request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                ids = request.POST.get('nid', None)
                IntervalSchedule.objects.get(id=ids).delete()
            else:
                ids = request.POST.getlist('id', None)
                IntervalSchedule.objects.filter(id__in=ids).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = _('Deletion error，{}'.format(e))
        finally:
            return HttpResponse(json.dumps(ret))

class PeriodicTasksListAll(LoginRequiredMixin, ListView):

    template_name = 'jobs/periodictask-list.html'
    model = PeriodicTask
    context_object_name = "periodicttasks_list"
    queryset = PeriodicTask.objects.all()
    ordering = ('-id',)

    def get_context_data(self, **kwargs):
        context = {
            "jobs_active": "active",
            "scheduled_tasks_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class PeriodicTasksAdd(LoginRequiredMixin, CreateView):

    model = PeriodicTask
    form_class = PeriodicTasksForm
    template_name = 'jobs/periodicttasks-add-update.html'
    success_url = reverse_lazy('jobs:periodictasks_list')

    def get_context_data(self, **kwargs):
        context = {
            "jobs_active": "active",
            "scheduled_tasks_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super(PeriodicTasksAdd, self).get_form_kwargs()
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = ''
        kwargs['project'] = project
        return kwargs

    def form_valid(self, form):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = ''
        jobs = form.save(commit=False)
        ip = form.cleaned_data['asser']
        key = form.cleaned_data['key']
        scripts = form.cleaned_data['scripts']
        scheduling = form.cleaned_data['scheduling']
        ips = ["{}".format(i.id) for i in ip]
        operator = UserProfile.objects.get(email=self.request.user)
        key_id = KeyManage.objects.get(name=key)
        if scripts:
            jobs.task = 'jobs.tasks.crontab_scripts'
            jobs.save()
            project_id = Project.objects.get(name=project)
            scripts_id = ScriptsManage.objects.get(id=scripts.id)
            crontab = ScheduledTasks.objects.create(project=project_id,scritps=scripts_id,create_user=operator,scheduled=jobs,key=key_id)
            crontab.asset.add(*ip)
            jr_obj = JobsResults.objects.create(type=4, operator=operator.username, key=key_id,project=project_id,
                                                job_name='Scripts Name{}'.format(scripts_id.name))

            kwarg = json.dumps({"ip": ips, "job": "{}".format(jr_obj.id),"script":"{}".format(scripts.id)})
            jobs.kwargs = kwarg
        else:
            jobs.task = 'jobs.tasks.crontab_task'
            jobs.save()
            project_id = Project.objects.get(name=project)
            task = TaskScheduling.objects.get(id=scheduling.id)
            crontab = ScheduledTasks.objects.create(project=project_id, scheduling=task, create_user=operator,
                                                    scheduled=jobs, key=key_id)
            crontab.asset.add(*ip)
            jr_obj = JobsResults.objects.create(type=4, operator=operator.username, key=key_id, project=project_id,
                                                job_name='Task Name{}'.format(task.name))
            kwarg = json.dumps({"ip": ips, "job": "{}".format(jr_obj.id), "task": "{}".format(scheduling.id)})
            jobs.kwargs = kwarg
        jobs.save()
        return super().form_valid(form)

class PeriodicTasksUpdate(LoginRequiredMixin, UpdateView):

    model = PeriodicTask
    form_class = PeriodicTasksFormUpdate
    template_name = 'jobs/periodicttasks-add-update.html'
    success_url = reverse_lazy('jobs:periodictasks_list')

    def get_context_data(self, **kwargs):
        context = {
            "jobs_active": "active",
            "scheduled_tasks_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super(PeriodicTasksUpdate, self).get_form_kwargs()
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = ''
        kwargs['project'] = project
        return kwargs

    def tasks(self):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        task_id = PeriodicTask.objects.get(id=pk)
        tasks_list =[i.id for i in task_id.scheduled_task.all()]
        return ScheduledTasks.objects.get(id=tasks_list[0])

    def get_initial(self):
        initial = super(PeriodicTasksUpdate, self).get_initial()
        tasks = self.tasks()
        initial['scripts'] = tasks.scritps
        initial['scheduling'] = tasks.scheduling
        initial['key'] = tasks.key
        initial['asser'] = tasks.asset.all()
        return initial


    def form_valid(self, form):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = ''
        project_id = Project.objects.get(name=project)
        jobs = form.save(commit=False)
        scripts = form.cleaned_data['scripts']
        key = form.cleaned_data['key']
        ip = form.cleaned_data['asser']
        scheduling = form.cleaned_data['scheduling']
        ips = ["{}".format(i.id) for i in ip]
        user_id = UserProfile.objects.get(username=self.request.user.username)
        key_id = KeyManage.objects.get(name=key)
        per = PeriodicTask.objects.get(id=jobs.id)
        if scripts:
            jobs.task = 'jobs.tasks.crontab_scripts'
            jobs.save()
            scripts_id = ScriptsManage.objects.get(id=scripts.id)
            tasks = self.tasks()
            tasks.project = project_id
            tasks.scheduling = None
            tasks.scritps = scripts_id
            tasks.create_user = user_id
            tasks.scheduled = jobs
            tasks.key = key_id
            tasks.save()
            tasks.asset.clear()
            tasks.asset.add(*ip)
            jr_obj = JobsResults.objects.create(type=4, operator=user_id, key=key_id, project=project_id,
                                                job_name='Scripts Name{}'.format(scripts_id.name))
            kwarg = json.dumps({"ip": ips, "job": "{}".format(jr_obj.id),"script":"{}".format(scripts.id)})
            jobs.kwargs = kwarg
        else:
            jobs.task = 'jobs.tasks.crontab_task'
            jobs.save()
            task = TaskScheduling.objects.get(id=scheduling.id)
            tasks = self.tasks()
            tasks.project = project_id
            tasks.scritps = None
            tasks.scheduling = task
            tasks.create_user = user_id
            tasks.scheduled = jobs
            tasks.key = key_id
            tasks.save()
            tasks.asset.clear()
            tasks.asset.add(*ip)
            jr_obj = JobsResults.objects.create(type=4, operator=user_id, key=key_id, project=project_id,
                                                job_name='Task Name{}'.format(task.name))
            kwarg = json.dumps({"ip": ips, "job": '{}'.format(jr_obj.id), "task": "{}".format(task.id)})
            jobs.kwargs = kwarg
        jobs.save()
        return super().form_valid(form)

class PeriodicTaskAllDel(LoginRequiredMixin, View):

    model = PeriodicTask

    @staticmethod
    def post(request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                ids = request.POST.get('nid', None)
                PeriodicTask.objects.get(id=ids).delete()
            else:
                ids = request.POST.getlist('id', None)
                PeriodicTask.objects.filter(id__in=ids).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = _('Deletion error，{}'.format(e))
        finally:
            return HttpResponse(json.dumps(ret))

