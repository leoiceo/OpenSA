#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo
from __future__ import absolute_import

from django.urls import path
from jobs.views import scripts, crontab, batchscripts, batchcmd, batchfiles, orchestration, batchtask
app_name = 'jobs'

urlpatterns = [
    # Scripts View
    path('scripts-list/', scripts.ScriptsListAll.as_view(), name='scripts_list'),
    path('scripts-add/', scripts.ScriptsAdd.as_view(), name='scripts_add'),
    path('scripts-update/<uuid:pk>/', scripts.ScriptsUpdate.as_view(), name='scripts_update'),
    path('scripts-all-del/', scripts.ScriptsAllDel.as_view(), name='scripts_all_del'),
    path('scripts-diff-list/<uuid:pk>/', scripts.ScriptsDiffList.as_view(), name='scripts_diff_list'),
    path('scripts-diff/', scripts.ScriptsDiff.as_view(), name='scripts_diff'),

    path('batch-files-list/', batchfiles.BatchFiles.as_view(), name='batch_files'),
    path('batch-files-list/<str:pk>/', batchfiles.BatchFilesList.as_view(), name='batch_files_list'),
    path('batch-files-process/', batchfiles.BatchFilesProcess.as_view(), name='batch_files_process'),

    path('batch-scripts-list/', batchscripts.BatchScripts.as_view(), name='batch_scripts'),
    path('batch-scripts-taskschedule/', batchscripts.TaskScheduleApi.as_view(), name='batch_scripts_taskschedule'),
    path('batch-scripts-process/', batchscripts.BatchScriptsProcess.as_view(), name='batch_scripts_process'),


    path('crontabs-list/', crontab.CrontabsListAll.as_view(), name='crontabs_list'),
    path('crontabs-add/', crontab.CrontabsAdd.as_view(), name='crontabs_add'),
    path('crontabs-all-del/', crontab.CrontabsAllDel.as_view(), name='crontabs_all_del'),
    path('crontabs-update/<int:pk>/', crontab.CrontabsUpdate.as_view(), name='crontabs_update'),
    #
    path('intervals/', crontab.IntervalsListAll.as_view(), name='intervals_list'),
    path('intervals-add/', crontab.IntervalsAdd.as_view(), name='intervals_add'),
    path('intervals-all-del/', crontab.IntervalsAllDel.as_view(), name='intervals_all_del'),
    path('intervals-update/<int:pk>/', crontab.IntervalsUpdate.as_view(), name='intervals_update'),
    #
    path('periodictasks-list/', crontab.PeriodicTasksListAll.as_view(), name='periodictasks_list'),
    path('periodictasks-add/', crontab.PeriodicTasksAdd.as_view(), name='periodictasks_add'),
    path('periodictasks-all-del/', crontab.PeriodicTaskAllDel.as_view(), name='periodictasks_all_del'),
    path('periodictasks-update/<int:pk>/', crontab.PeriodicTasksUpdate.as_view(), name='periodictasks_update'),

    path('batch-cmd-list/', batchcmd.CmdListAll.as_view(), name='cmd_list'),
    path('batch-cmd/', batchcmd.BatchCommandExecute.as_view(), name='execution_command'),
    path('batch-cmd-result/', batchcmd.BatchExecutionResult.as_view(), name='execution_result'),
    path('batch-cmd-result-flush/', batchcmd.BatchExecutionResultFlush.as_view(), name='execution_flush'),

    path('orchestration-list/', orchestration.OrchestrationListAll.as_view(), name='orchestration_list'),
    path('orchestration-add/', orchestration.OrchestrationAdd.as_view(), name='orchestration_add'),
    path('orchestration-all-del/', orchestration.OrchestrationAllDel.as_view(), name='orchestration_all_del'),
    path('orchestration-update/<uuid:pk>/', orchestration.OrchestrationUpdate.as_view(), name='orchestration_update'),

    path('batch-task-list/', batchtask.BatchTask.as_view(), name='batch_task'),
    path('batch-task-taskschedule/', batchtask.BatchTaskApi.as_view(), name='batch_task_taskschedule'),
    path('batch-task-process/', batchtask.BatchTaskProcess.as_view(), name='batch_task_process'),

    ]
