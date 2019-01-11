#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

from __future__ import unicode_literals

import json
import time
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.utils.translation import ugettext as _
from asset.models import ServerUse
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
from opensa.api import LoginPermissionRequired
from ..forms import UseForm,UseFormUpdate

class UseList(LoginPermissionRequired,ListView):

    template_name = 'asset/use-list.html'
    model = ServerUse
    context_object_name = "use_list"

    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_use_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = super().get_queryset()
        queryset = self.queryset.all().order_by('id')
        return queryset


class UseAdd(LoginPermissionRequired,CreateView):

    model = ServerUse
    form_class = UseForm
    template_name = 'asset/product-add-update.html'
    success_url = reverse_lazy('asset:use_list')


    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_use_active": "active",
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
        return super(UseAdd, self).form_invalid(form)
#
class UseUpdate(LoginPermissionRequired,UpdateView):

    model = ServerUse
    form_class = UseFormUpdate
    template_name = 'asset/product-add-update.html'
    success_url = reverse_lazy('asset:use_list')


    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_use_active": "active",
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
        return super(UseUpdate, self).form_invalid(form)

    def get_success_url(self):
        self.url = self.request.POST['__next__']
        return self.url

class UseDel(LoginPermissionRequired,View):

    model = ServerUse

    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid') :
                id = request.POST.get('nid', None)
                ServerUse.objects.get(id=id).delete()
            else:
                ids = request.POST.getlist('id', None)
                ServerUse.objects.filter(id__in=ids).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = _('Deletion error，{}'.format(e))
        finally:
            return HttpResponse(json.dumps(ret))

