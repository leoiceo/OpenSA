#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo
from __future__ import unicode_literals
import json,uuid,datetime
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.utils.translation import ugettext as _
from django.conf import settings
from users.models import KeyManage
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from pure_pagination import PageNotAnInteger, Paginator
from users.models import UserProfile
from audit.models import RequestRecord,PasswordChangeLog
from opensa.api import LoginPermissionRequired

class LoginLogList(LoginPermissionRequired, ListView):
    model = RequestRecord
    template_name = 'audit/login-log.html'
    queryset = RequestRecord.objects.all()
    ordering = ('id',)

    def get_context_data(self, **kwargs):
        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger as e:
            page = 1
        p = Paginator(self.queryset, getattr(settings, 'DISPLAY_PER_PAGE'), request=self.request)
        loginlog_list = p.page(page)

        context = {
            "audit_active": "active",
            "audit_login_active": "active",
            "loginlog_list": loginlog_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = RequestRecord.objects.filter(get_full_path__in=['/users/login/','/users/logout/'])
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        operator = UserProfile.objects.get(email=self.request.user)
        if self.request.GET.get('name') and operator.is_superuser:
            query = self.request.GET.get('name', None)
            self.queryset = self.queryset.filter(username__username=query).order_by('-datetime')
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(datetime__gte=date_from).filter(datetime__lte=end).order_by(
                    '-datetime')
        else:
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(datetime__gte=date_from).filter(datetime__lte=end).order_by(
                    '-datetime')
            else:
                self.queryset = self.queryset.order_by('-datetime')

        return self.queryset

class PasswordChangeList(LoginPermissionRequired, ListView):
    model = PasswordChangeLog
    template_name = 'audit/password-change-log.html'
    queryset = PasswordChangeLog.objects.all()
    ordering = ('id',)

    def get_context_data(self, **kwargs):
        import datetime
        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger as e:
            page = 1
        p = Paginator(self.queryset, getattr(settings, 'DISPLAY_PER_PAGE'), request=self.request)
        requestlog_list = p.page(page)

        context = {
            "audit_active": "active",
            "password_change_log": "active",
            "loginlog_list": requestlog_list,
            'date_from': (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y-%m-%d'),
            'date_to': (datetime.datetime.now() + datetime.timedelta(days=+1)).strftime('%Y-%m-%d')

        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = PasswordChangeLog.objects.all()
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        operator = UserProfile.objects.get(email=self.request.user)
        if self.request.GET.get('name') and operator.is_superuser:
            query = self.request.GET.get('name', None)
            self.queryset = self.queryset.filter(user=query).order_by('-datetime')
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(datetime__gte=date_from).filter(datetime__lte=end).order_by(
                    '-datetime')
        else:
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(datetime__gte=date_from).filter(datetime__lte=end).order_by(
                    '-datetime')
            else:
                self.queryset = self.queryset.order_by('-datetime')

        return self.queryset

class RequestLogList(LoginPermissionRequired, ListView):
    model = RequestRecord
    template_name = 'audit/request-log.html'
    queryset = RequestRecord.objects.all()
    ordering = ('id',)

    def get_context_data(self, **kwargs):
        import datetime
        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger as e:
            page = 1
        p = Paginator(self.queryset, getattr(settings, 'DISPLAY_PER_PAGE'), request=self.request)
        requestlog_list = p.page(page)

        context = {
            "audit_active": "active",
            "audit_request_active": "active",
            "loginlog_list": requestlog_list,
            'date_from': (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y-%m-%d'),
            'date_to': (datetime.datetime.now() + datetime.timedelta(days=+1)).strftime('%Y-%m-%d')

        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = RequestRecord.objects.exclude(get_full_path__in=['/users/login/','/users/logout/'])
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        operator = UserProfile.objects.get(email=self.request.user)
        if self.request.GET.get('name') and operator.is_superuser:
            query = self.request.GET.get('name', None)
            self.queryset = self.queryset.filter(operator=query).order_by('-datetime')
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(datetime__gte=date_from).filter(datetime__lte=end).order_by(
                    '-datetime')
        else:
            if date_from and date_to:
                end = datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1)
                self.queryset = self.queryset.filter(datetime__gte=date_from).filter(datetime__lte=end).order_by(
                    '-datetime')
            else:
                self.queryset = self.queryset.order_by('-datetime')

        return self.queryset

