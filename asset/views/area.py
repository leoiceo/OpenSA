#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

from __future__ import unicode_literals
import json
from django.http import HttpResponse
from django.views.generic import ListView, View, CreateView, UpdateView
from django.utils.translation import ugettext as _
from asset.models import Area
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
from opensa.api import LoginPermissionRequired
from ..forms import AreaForm, AreaFormUpdate

class AreaList(LoginPermissionRequired,ListView):
    template_name = 'asset/area-list.html'
    model = Area
    context_object_name = "area_list"

    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_area_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = super().get_queryset()
        queryset = self.queryset.all().order_by('id')
        return queryset


class AreaAdd(LoginPermissionRequired,CreateView):
    model = Area
    form_class = AreaForm
    template_name = 'asset/area-add-update.html'
    success_url = reverse_lazy('asset:area_list')


    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_area_active": "active",
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
        return super(AreaAdd, self).form_invalid(form)


class AreaUpdate(LoginPermissionRequired,UpdateView):
    model = Area
    form_class = AreaFormUpdate
    template_name = 'asset/area-add-update.html'
    success_url = reverse_lazy('asset:area_list')


    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_area_active": "active",
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
        return super(AreaUpdate, self).form_invalid(form)

    def get_success_url(self):
        self.url = self.request.POST['__next__']
        return self.url

class AreaDel(LoginPermissionRequired,View):
    model = Area

    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid') :
                id = request.POST.get('nid', None)
                Area.objects.get(id=id).delete()
            else:
                ids = request.POST.getlist('id', None)
                Area.objects.filter(id__in=ids).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = _('Deletion error，{}'.format(e))
        finally:
            return HttpResponse(json.dumps(ret))

