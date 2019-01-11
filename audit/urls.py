#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo
from __future__ import absolute_import
from django.urls import path
from audit.views import loginfo, joblog

app_name = 'audit'

urlpatterns = [
    # Asset View
    path('login-log/', loginfo.LoginLogList.as_view(), name='login-log-list'),
    path('request-log/', loginfo.RequestLogList.as_view(), name='request-log-list'),
    path('crontab-log/', joblog.CrontadbList.as_view(), name='jobs_logs_crontab'),
    path('crontab-result/', joblog.CrontabResult.as_view(), name='jobs_crontab_result'),
    path('password-change-log/', loginfo.PasswordChangeList.as_view(), name='password_change_log'),
    path('command-log/', joblog.ExecutionList.as_view(), name='jobs_logs_command'),
    path('command-result/', joblog.ExecutionResult.as_view(), name='jobs_command_result'),

    path('scripts-log/', joblog.ScriptsList.as_view(), name='jobs_logs_scripts'),
    path('scripts-result/', joblog.ScriptsResult.as_view(), name='jobs_scripts_result'),

    path('scheduling-log/', joblog.SchedulingList.as_view(), name='jobs_logs_scheduling'),
    path('scheduling-result/', joblog.SchedulingResult.as_view(), name='jobs_scheduling_result'),
    ]
