#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

from __future__ import unicode_literals

import json
import time
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.utils.translation import ugettext as _
from django.conf import settings
from asset.models import Work_Env
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from pure_pagination import PageNotAnInteger, Paginator
from django.urls import reverse_lazy
from asset.forms import AssetFormAdd, AssetForm
from opensa.api import LoginPermissionRequired
from ..forms import WorkenvForm,WorkenvFormUpdate

class WorkEnvList(LoginPermissionRequired,ListView):
    '''
    项目列表
    '''
    template_name = 'asset/workenv-list.html'
    model = Work_Env
    context_object_name = "workenv_list"

    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_work_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = super().get_queryset()
        queryset = self.queryset.all().order_by('id')
        return queryset


class WorkEnvAdd(LoginPermissionRequired,CreateView):
    """
    项目增加
    """
    model = Work_Env
    form_class = WorkenvForm
    template_name = 'asset/workenv-add-update.html'
    success_url = reverse_lazy('asset:workenv_list')


    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_work_active": "active",
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
        return super(WorkEnvAdd, self).form_invalid(form)
#
class WorkEnvUpdate(LoginPermissionRequired,UpdateView):
    '''
    用户更新信息
    '''
    model = Work_Env
    form_class = WorkenvFormUpdate
    template_name = 'asset/workenv-add-update.html'
    success_url = reverse_lazy('asset:workenv_list')


    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_work_active": "active",
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
        return super(WorkEnvUpdate, self).form_invalid(form)

    def get_success_url(self):
        self.url = self.request.POST['__next__']
        return self.url

class WorkEnvDel(LoginPermissionRequired,View):
    """
    删除用户
    """
    model = Work_Env

    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid') :
                id = request.POST.get('nid', None)
                Work_Env.objects.get(id=id).delete()
            else:
                ids = request.POST.getlist('id', None)
                Work_Env.objects.filter(id__in=ids).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = _('Deletion error，{}'.format(e))
        finally:
            return HttpResponse(json.dumps(ret))

