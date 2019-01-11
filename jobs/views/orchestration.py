#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo
from __future__ import unicode_literals
import json,uuid
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.conf import settings
from django.shortcuts import render,reverse
from django.db.models import Q
from pure_pagination import PageNotAnInteger, Paginator
from jobs.models import TaskScheduling,ScriptsManage,TaskSchedulScripts
from opensa.api import LoginPermissionRequired
from ..forms import ScritsManageForm
from users.models import UserProfile,Project


class OrchestrationListAll(LoginPermissionRequired,ListView):

    model = TaskScheduling
    template_name = 'jobs/orchestration-list.html'
    queryset = TaskScheduling.objects.all()
    ordering = ('id',)

    def get_context_data(self, **kwargs):
        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger as e:
            page = 1
        p = Paginator(self.queryset, getattr(settings, 'DISPLAY_PER_PAGE'), request=self.request)
        scripts_list = p.page(page)

        context = {
            "jobs_active": "active",
            "tasks_scheduling_active": "active",
            "scripts_list": scripts_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        self.queryset = super().get_queryset()

        if self.request.GET.get('name'):
            query = self.request.GET.get('name', None)
            self.queryset = self.queryset.filter(Q(name__icontains=query)|
                                                 Q(create_user__username__icontains=query)
                                                 ).order_by('create_date')
        else:
            self.queryset = self.queryset.filter(project__name=project).order_by('create_date')

        return self.queryset



class OrchestrationAdd(LoginPermissionRequired,ListView):

    model = TaskScheduling
    template_name = 'jobs/orchestration-add.html'


    def get_project(self):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        return project

    def get_context_data(self, **kwargs):
        error = self.request.GET.get('error')
        scripts_in = [i.id for i in ScriptsManage.objects.filter(project__name=self.get_project()) if i.args == '{}']
        scripts = ScriptsManage.objects.filter(id__in=scripts_in)
        context = {
            "jobs_active": "active",
            "tasks_scheduling_active": "active",
            "scripts" : scripts,
            "error": error,
        }
        if '__next__' in self.request.POST:
            context['i__next__'] = self.request.POST['__next__']
        else:
            try:
                context['i__next__'] = self.request.META['HTTP_REFERER']
            except Exception as e:
                pass
        kwargs.update(context)

        return super().get_context_data(**kwargs)

    def post(self,request):
        user = UserProfile.objects.get(email=self.request.user)
        try:
            scritps = request.POST.getlist('scritps', None)
            level = request.POST.getlist('level', None)
            time = request.POST.getlist('time', None)
            stat = request.POST.getlist('status', None)
            name = request.POST.get('name')
            comment = request.POST.get('comment')
            project_id = Project.objects.get(name=self.get_project())
            scriptwork = TaskScheduling.objects.create(name=name,project=project_id,create_user=user,comment=comment)
            for status in range(len(scritps)):
                scriptsmanage = ScriptsManage.objects.get(id=scritps[status])
                scriptstatus = TaskSchedulScripts.objects.create(scripts=scriptsmanage,status=stat[status],level=level[status],delaytime=time[status])
                scriptwork.task_scripts.add(scriptstatus)
            return HttpResponseRedirect(reverse('jobs:orchestration_list'))
        except Exception as e:
            print(e)
            return HttpResponseRedirect('/jobs/orchestration_add/?error={}'.format(e))


class OrchestrationAllDel(LoginPermissionRequired,View):

    model = TaskScheduling
    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            if  request.POST.get('nid') :
                id = request.POST.get('nid', None)
                del_scritps = TaskScheduling.objects.get(id=id)
                scriptstatus_id = del_scritps.task_scripts.all()
                for id in scriptstatus_id:
                    TaskSchedulScripts.objects.get(id=id.id).delete()
                del_scritps.task_scripts.clear()
                del_scritps.delete()

            else:
                ids = request.POST.getlist('id', None)
                for i in ids:
                    del_scritps = TaskScheduling.objects.get(id=i)
                    scriptstatus_id = del_scritps.task_scripts.all()
                    for id in scriptstatus_id:
                        TaskSchedulScripts.objects.get(id=id.id).delete()
                    del_scritps.task_scripts.clear()
                    del_scritps.delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))


class OrchestrationUpdate(LoginPermissionRequired,UpdateView):

    model = TaskScheduling
    form_class = ScritsManageForm
    template_name = 'jobs/orchestration-edit.html'


    def get_project(self):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        return project

    def get_context_data(self, **kwargs):
        error = self.request.GET.get('error')
        scritps, status, level, time = [], [], [],[]
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        scriptwork = TaskScheduling.objects.get(id=pk)
        scriptstatus_id = scriptwork.task_scripts.all().order_by('level')
        scripts_in = [i.id for i in ScriptsManage.objects.filter(project__name=self.get_project()) if i.args == '{}']
        scritps_all = ScriptsManage.objects.filter(id__in=scripts_in)
        for id in scriptstatus_id:
            scriptstatus = TaskSchedulScripts.objects.get(id = id.id)
            scritps_name = ScriptsManage.objects.get(id = scriptstatus.scripts.id)
            scritps.append(str(scritps_name.id))
            status.append(scriptstatus.status)
            level.append(scriptstatus.level)
            time.append(scriptstatus.delaytime)
        context = {
            "comment" : scriptwork.comment,
            "jobs_active": "active",
            "tasks_scheduling_active": "active",
            "scriptmanage": scritps,
            "name": scriptwork.name,
            "scripts" : scritps_all,
            "status" : status,
            "level" : level,
            "time" : time,
            "error": error,
            "pk" : pk,

        }
        if '__next__' in self.request.POST:
            context['i__next__'] = self.request.POST['__next__']
        else:
            try:
                context['i__next__'] = self.request.META['HTTP_REFERER']
            except Exception as e:
                pass
        kwargs.update(context)

        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        try:
            pk = self.kwargs.get(self.pk_url_kwarg, None)
            scritps = request.POST.getlist('scritps', None)
            level = request.POST.getlist('level', None)
            time = request.POST.getlist('time', None)
            stat = request.POST.getlist('status', None)
            name = request.POST.get('name')
            comment = request.POST.get('comment')
            scriptwork = TaskScheduling.objects.get(id = pk)
            scriptwork.name = name
            scriptwork.comment = comment
            scriptwork.save()
            scriptstatus_id = scriptwork.task_scripts.all().order_by('level')
            for id in scriptstatus_id:
                TaskSchedulScripts.objects.get(id=id.id).delete()
            scriptwork.task_scripts.clear()
            for status in range(len(level)):
                scriptsmanage = ScriptsManage.objects.get(id=scritps[status])
                scriptstatus = TaskSchedulScripts.objects.create(scripts=scriptsmanage,status=stat[status],level=level[status],delaytime=time[status])
                scriptwork.task_scripts.add(scriptstatus)
            return HttpResponseRedirect(reverse('jobs:orchestration_list'))
        except Exception as e:
            return HttpResponseRedirect('/jobs/orchestration_update/?error={}'.format(e))








