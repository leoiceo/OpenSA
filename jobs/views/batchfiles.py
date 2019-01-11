#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import HttpResponse,render,HttpResponseRedirect
from django.views.generic import ListView, View, CreateView, UpdateView
from django.urls import reverse_lazy
from ..forms import ScritsManageForm
from opensa import settings
import json, datetime, uuid,subprocess,os,time
from asset.models import Asset
from jobs.models import ScriptsManage
from audit.models import JobsResults,TaskSchedule
from users.models import Project,UserProfile,KeyManage
from opensa.api import LoginPermissionRequired,mkdir
from jobs.utils import list_upload_info
from jobs.tasks import batch_files_func


class BatchFiles(LoginPermissionRequired,CreateView):

    model = ScriptsManage
    form_class = ScritsManageForm
    template_name = 'jobs/batch_files.html'
    success_url = reverse_lazy('jobs:batch_files')

    def get_context_data(self, **kwargs):

        context = {
            "jobs_active": "active",
            "batch_tasks_active": "active",
            "batch_file_active": "active",
        }

        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        upload_files = [request.FILES.get('file[%d]' % i) for i in range(0, len(request.FILES))]
        upload_dir = "{}/upload".format(settings.DATA_DIR)
        temp_dir = "{}".format(uuid.uuid4())
        try:

            for upload_file in upload_files:
                file_path = '{}/{}'.format(upload_dir,temp_dir)
                mkdir(file_path)

                with open("{}/{}".format(file_path,upload_file.name), 'wb+') as f:
                    for chunk in upload_file.chunks():
                        f.write(chunk)

                if upload_file.name.split(".")[-1] == "zip":
                    cmd = "unzip -o -O GB18030 {0}/{1} -d {0};rm -f {0}/{1}".format(file_path,upload_file.name)
                    result = subprocess.getstatusoutput(cmd)

                    if result[0]:
                        raise Exception(result[1])
            msg = temp_dir
        except Exception as e:
            msg = "{}: {}".format(_("Upload File failed"),e)

        return HttpResponse(msg)


class BatchFilesList(LoginPermissionRequired,CreateView):
    model = ScriptsManage
    form_class = ScritsManageForm
    template_name = 'jobs/batch_files_list.html'

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        project = self.request.session["project"]
        key_list = Project.objects.get(name=project).key.all()
        asset_list = Asset.objects.filter(project__name=project, status=1)

        file_info = list_upload_info(pk)

        context = {
            "jobs_active": "active",
            "batch_tasks_active": "active",
            "batch_file_active": "active",
            "upload_id": pk,
            "key_list": key_list,
            "asset_list": asset_list,
            "file_info": file_info,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class BatchFilesProcess(LoginPermissionRequired,CreateView):
    model = ScriptsManage
    form_class = ScritsManageForm
    template_name = 'jobs/batch_files_process.html'

    def get_context_data(self, **kwargs):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None

        upload_id = self.request.POST.get("upload_id")
        key_id = self.request.POST.get("key_id")
        asset_info = self.request.POST.get("asset_info")
        timeout = self.request.POST.get("timeout")
        remote_path = self.request.POST.get("remotepath")

        operator = UserProfile.objects.get(email=self.request.user).username
        project_id = Project.objects.get(name=project)
        file_info = list_upload_info(upload_id)
        key_obj = KeyManage.objects.get(id=key_id.strip('-'))
        asset_list = asset_info.split(',')
        while '' in asset_list:
            asset_list.remove('')
        asset_count = len(asset_list)

        jr_obj = JobsResults.objects.create(type=2, operator=operator, key=key_obj,project=project_id,
                                            job_name=_("File Distribution"),remote_path=remote_path)

        from celery import group
        yet = group(batch_files_func.s(jr_obj.id, upload_id, remote_path,timeout, i) for i in asset_list)()
        jobs_obj = JobsResults.objects.get(id=jr_obj.id)

        context = {
            "jobs_active": "active",
            "batch_tasks_active": "active",
            "batch_script_active": "active",
            "keymanage_obj": key_obj,
            "remote_path": remote_path,
            "jobs_obj": jobs_obj,
            "file_info": file_info,
            "asset_count": asset_count,
            "timeout": timeout,
            "yet": yet,
        }

        kwargs.update(context)
        return super().get_context_data(**kwargs)
