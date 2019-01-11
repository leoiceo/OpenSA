#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo

from __future__ import unicode_literals
import datetime
from django.core.cache import cache
from django.shortcuts import render
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,View
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import reverse, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.conf import settings
from users.models import UserProfile
from audit.models import RequestRecord
from users import forms
from django.contrib.auth import authenticate,login,logout



class UserLoginView(FormView):
    template_name = 'users/login.html'
    model = UserProfile

    def get_context_data(self, **kwargs):
        context = {}
        kwargs.update(context)

    def post(self, request, *args, **kwargs):

        if 'HTTP_X_FORWARDED_FOR' in self.request.META:
            ipaddr = self.request.META['HTTP_X_FORWARDED_FOR']
        else:
            ipaddr = self.request.META['REMOTE_ADDR']
        username = self.request.POST.get("username")
        password = self.request.POST.get("password")
        check_code = request.POST.get('checkcode')
        user = authenticate(username=username, password=password)
        session_code = request.session["CheckCode"]

        if check_code.strip().lower() != session_code.lower():
            login_err = _('Did you slip the wrong hand? try again')
        else:
            if user is not None:  # pass authencation
                if user.is_active == False:
                    login_err = _('Warning, {} has been disabled'.format(user.username))
                    return render(request, 'users/login.html', {'login_err': login_err})
                login(self.request, user)
                userprofile = UserProfile.objects.get(username=user.username)
                h = RequestRecord(ipaddr=ipaddr, type=1, get_full_path=self.request.get_full_path())
                h.username = userprofile
                h.save()
                login_limit_info = UserProfile.objects.filter(email=username)
                login_limit_info.update(limit=0,login_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                return HttpResponseRedirect('/')
            else:
                try:
                    limit_num = 5
                    curr_login_limit = UserProfile.objects.get(email=username).login_limit
                    new_login_limit = int(curr_login_limit) + 1
                    login_limit_info = UserProfile.objects.filter(email=username)
                    if new_login_limit == 5:
                        login_limit_info.update(limit=new_login_limit, is_active=0)
                        login_err = _("Warning: {} has been disabled, please contact the administrator".format(username))
                    else:
                        login_limit_info.update(limit=new_login_limit)
                        login_err = _("Warning: {} remaining attempts are {}".format(username, limit_num - new_login_limit))
                except Exception as e:
                    login_err = _('Verification failed? Think again ^.^')

        return render(request, 'users/login.html', {'login_err': login_err})



class UserLogoutView(TemplateView):
    template_name = 'users/login.html'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        response = super().get(request, *args, **kwargs)
        return response

    def get_context_data(self, **kwargs):
        context = {
            'messages': 'Logout success',
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)