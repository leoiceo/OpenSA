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
from asset.models import Idc
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from pure_pagination import PageNotAnInteger, Paginator
from django.urls import reverse_lazy
from asset.forms import AssetFormAdd, AssetForm
from opensa.api import LoginPermissionRequired
from ..forms import IdcForm,IdcFormUpdate

class IdcList(LoginPermissionRequired,ListView):
    '''
    项目列表
    '''
    template_name = 'asset/idc-list.html'
    model = Idc
    context_object_name = "idc_list"

    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_idc_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = super().get_queryset()
        queryset = self.queryset.all().order_by('id')
        return queryset


class IdcAdd(LoginPermissionRequired,CreateView):
    """
    项目增加
    """
    model = Idc
    form_class = IdcForm
    template_name = 'asset/idc-add-update.html'
    success_url = reverse_lazy('asset:idc_list')


    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_idc_active": "active",
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
        return super(IdcAdd, self).form_invalid(form)

class IdcUpdate(LoginPermissionRequired,UpdateView):
    '''
    用户更新信息
    '''
    model = Idc
    form_class = IdcFormUpdate
    template_name = 'asset/idc-add-update.html'
    success_url = reverse_lazy('asset:idc_list')


    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_idc_active": "active",
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
        return super(IdcUpdate, self).form_invalid(form)

    def get_success_url(self):
        self.url = self.request.POST['__next__']
        return self.url

class IdcDel(LoginPermissionRequired,View):
    """
    删除用户
    """
    model = Idc

    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid') :
                id = request.POST.get('nid', None)
                Idc.objects.get(id=id).delete()
            else:
                ids = request.POST.getlist('id', None)
                Idc.objects.filter(id__in=ids).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = _('Deletion error，{}'.format(e))
        finally:
            return HttpResponse(json.dumps(ret))

