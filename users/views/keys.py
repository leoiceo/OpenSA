#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo

from __future__ import unicode_literals

import json
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.utils.translation import ugettext as _
from django.conf import settings
from users.models import KeyManage,Project
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from pure_pagination import PageNotAnInteger, Paginator
from django.urls import reverse_lazy
from ..forms import KeyManageForm
from opensa.api import LoginPermissionRequired

class KeyListAll(LoginPermissionRequired,ListView):
    '''
    密钥列表
    '''
    model = KeyManage
    template_name = 'users/keys-list.html'
    queryset = KeyManage.objects.all()
    ordering = ('id',)

    def get_context_data(self, **kwargs):
        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger as e:
            page = 1
        p = Paginator(self.queryset, getattr(settings, 'DISPLAY_PER_PAGE'), request=self.request)
        key_list = p.page(page)

        context = {
            "users_active": "active",
            "users_key_list": "active",
            "key_list": key_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = super().get_queryset()

        if self.request.GET.get('name'):
            query = self.request.GET.get('name', None)
            self.queryset = self.queryset.filter(Q(name__icontains=query)
                                                 ).order_by('-id')
        else:
            self.queryset = self.queryset.all().order_by('id')

        return self.queryset


class KeyAdd(LoginPermissionRequired,CreateView):
    '''
    添加密钥
    '''
    model = KeyManage
    form_class = KeyManageForm
    template_name = 'users/keys-add-update.html'
    success_url = reverse_lazy('users:key_list')

    def get_context_data(self, **kwargs):

        context = {
            "users_active": "active",
            "users_key_list": "active",
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
        return super(KeyAdd, self).form_invalid(form)

    def form_valid(self, form):
        key = form.save(commit=False)
        key.save()
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        pro = Project.objects.get(name=project)
        pro.key.add(key)
        return super().form_valid(form)


class KeyUpdate(LoginPermissionRequired,UpdateView):
    '''
    更新密钥
    '''
    model = KeyManage
    form_class = KeyManageForm
    template_name = 'users/keys-add-update.html'
    success_url = reverse_lazy('users:key_list')

    def get_context_data(self, **kwargs):

        context = {
            "users_active": "active",
            "users_key_list": "active",
        }
        if '__next__' in self.request.POST:
            context['i__next__'] = self.request.POST['__next__']
        else:
            try:
                context['i__next__'] = self.request.META['HTTP_REFERER']
            except Exception as e:
                pass
        kwargs.update(context)
        return super(KeyUpdate, self).get_context_data(**kwargs)

    def form_invalid(self, form):
        return super(KeyUpdate, self).form_invalid(form)

    def get_success_url(self):
        self.url = self.request.POST['__next__']
        return self.url


class KeyAllDel(LoginPermissionRequired,DeleteView):
    """
    删除密钥
    """
    model = KeyManage

    def post(self, request, *args, **kwargs):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                id = request.POST.get('nid', None)
                KeyManage.objects.get(id=id).delete()
            else:
                ids = request.POST.getlist('id', None)
                KeyManage.objects.filter(id__in=ids).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = _('Deletion error，{}'.format(e))
        finally:
            return HttpResponse(json.dumps(ret))