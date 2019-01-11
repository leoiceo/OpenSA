#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

from __future__ import unicode_literals

import json
# import os
# from django.core.cache import cache
# from django.shortcuts import render
# from django.contrib.auth import login as auth_login, logout as auth_logout
# from django.core.files.storage import default_storage
# from django.shortcuts import reverse, redirect
# from django.utils.decorators import method_decorator
# from django.views.decorators.cache import never_cache
# from django.views.decorators.csrf import csrf_protect
# from django.views.decorators.debug import sensitive_post_parameters
# from django.views.generic.base import TemplateView
# from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.utils.translation import ugettext as _
from django.conf import settings
from users.models import *
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from pure_pagination import PageNotAnInteger, Paginator
from django.urls import reverse_lazy
from ..forms import UsersFormAdd, UsersForm

class UsersListAll(LoginRequiredMixin,ListView):
    '''
    用户列表列表
    '''
    model = UserProfile
    template_name = 'users/users-list.html'
    queryset = UserProfile.objects.all()
    ordering = ('id',)

    def get_context_data(self, **kwargs):
        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger as e:
            page = 1
        p = Paginator(self.queryset, getattr(settings, 'DISPLAY_PER_PAGE'), request=self.request)
        user_list = p.page(page)
        context = {
            "users_active": "active",
            "users_users_list": "active",
            "user_list": user_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = super().get_queryset()
        # user = UserProfile.objects.get(username=self.request.user)
        # project = [i.id for i in Project.objects.filter(Project_user=user.id)]
        # if user.is_superuser:
        if self.request.GET.get('name'):
            query = self.request.GET.get('name', None)
            self.queryset = self.queryset.filter(Q(username__icontains=query)
                                                 ).order_by('-id')
        else:
            self.queryset = self.queryset.all().order_by('id')
        # else:
        #     if self.request.GET.get('name'):
        #         query = self.request.GET.get('name', None)
        #         self.queryset = self.queryset.filter(project__in=project).filter(
        #             Q(username__contains=query) |
        #             Q(ip__contains=query) |
        #             Q(other_ip__contains=query)
        #         ).order_by('-id')
        #     else:
        #         self.queryset = self.queryset.filter(project__in=project).order_by('id')
        return self.queryset

class UsersAdd(LoginRequiredMixin,CreateView):
    """
    用户增加
    """
    model = UserProfile
    form_class = UsersFormAdd
    template_name = 'users/users-add-update.html'
    success_url = reverse_lazy('users:users_list')

    def get_context_data(self, **kwargs):

        context = {
            "users_active": "active",
            "users_users_list": "active",
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
        return super(UsersAdd, self).form_invalid(form)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        form.save()
        return super().form_valid(form)




class UsersUpdate(LoginRequiredMixin,UpdateView):
    '''
    用户更新信息
    '''
    model = UserProfile
    form_class = UsersForm
    template_name = 'users/users-add-update.html'
    success_url = reverse_lazy('users:users_list')


    def get_context_data(self, **kwargs):

        context = {
            "users_active": "active",
            "users_users_list": "active",
        }
        if '__next__' in self.request.POST:
            context['i__next__'] = self.request.POST['__next__']
        else:
            try:
                context['i__next__'] = self.request.META['HTTP_REFERER']
            except Exception as e:
                pass
        kwargs.update(context)
        return super(UsersUpdate, self).get_context_data(**kwargs)

    def form_invalid(self, form):
        return super(UsersUpdate, self).form_invalid(form)

    def get_success_url(self):
        self.url = self.request.POST['__next__']
        return self.url


class UsersAllDel(LoginRequiredMixin,View):
    """
    删除用户
    """
    model = UserProfile

    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid') :
                id = request.POST.get('nid', None)
                UserProfile.objects.get(id=id).delete()
            else:
                ids = request.POST.getlist('id', None)
                UserProfile.objects.filter(id__in=ids).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = _('Deletion error，{}'.format(e))
        finally:
            return HttpResponse(json.dumps(ret))

class UsersDetail(LoginRequiredMixin,DetailView):
    '''
    用户详细信息
    '''
    model = UserProfile
    template_name = 'users/users-detail.html'

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        detail = UserProfile.objects.get(id=pk)

        context = {
            "users_active": "active",
            "users_users_list": "active",
            "users": detail,
            "nid": pk,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)