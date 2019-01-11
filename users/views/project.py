#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

from __future__ import unicode_literals
import os
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
from django.conf import settings
from users.models import *
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from pure_pagination import PageNotAnInteger, Paginator
from django.urls import reverse_lazy
from ..forms import ProjectFormAdd, ProjectForm
from opensa.api import LoginPermissionRequired

class ProjectListAll(LoginPermissionRequired,ListView):
    '''
    项目列表
    '''
    template_name = 'users/project-list.html'
    model = Project
    context_object_name = "project_list"

    def get_context_data(self, **kwargs):

        context = {
            "users_active": "active",
            "users_project_list": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = super().get_queryset()
        queryset = self.queryset.all().order_by('id')
        return queryset

class ProjectAdd(LoginPermissionRequired,CreateView):
    """
    项目增加
    """
    model = Project
    form_class = ProjectFormAdd
    template_name = 'users/project-add-update.html'
    success_url = reverse_lazy('users:project_list')


    def get_context_data(self, **kwargs):

        context = {
            "users_active": "active",
            "users_project_list": "active",
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

    def form_invalid(self, form):
        return super(ProjectAdd, self).form_invalid(form)
#
#
#
class ProjectUpdate(LoginPermissionRequired,UpdateView):
    '''
    用户更新信息
    '''
    model = Project
    form_class = ProjectForm
    template_name = 'users/project-add-update.html'
    success_url = reverse_lazy('users:users_list')


    def get_context_data(self, **kwargs):

        context = {
            "users_active": "active",
            "users_project_list": "active",
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


    def form_invalid(self, form):
        return super(ProjectUpdate, self).form_invalid(form)

    def get_success_url(self):
        self.url = self.request.POST['__next__']
        return self.url
#
#
class ProjectDel(LoginPermissionRequired,View):
    """
    删除用户
    """
    model = Project

    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid') :
                id = request.POST.get('nid', None)
                Project.objects.get(id=id).delete()
            else:
                ids = request.POST.getlist('id', None)
                Project.objects.filter(id__in=ids).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = _('Deletion error，{}'.format(e))
        finally:
            return HttpResponse(json.dumps(ret))
