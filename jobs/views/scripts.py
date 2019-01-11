#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo
from __future__ import unicode_literals
import json,uuid
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.utils.translation import ugettext as _
from django.conf import settings
from django.shortcuts import render
from users.models import KeyManage
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from pure_pagination import PageNotAnInteger, Paginator
from django.urls import reverse_lazy
from jobs.models import ScriptsManage,UpdateConfigLog
from opensa.api import LoginPermissionRequired
from ..forms import ScritsManageForm
from users.models import UserProfile,Project

class ScriptsListAll(LoginPermissionRequired,ListView):
    '''
    密钥列表
    '''
    model = ScriptsManage
    template_name = 'jobs/scripts-list.html'
    queryset = ScriptsManage.objects.all()
    ordering = ('id',)

    def get_context_data(self, **kwargs):
        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger as e:
            page = 1
        p = Paginator(self.queryset, getattr(settings, 'DISPLAY_PER_PAGE'), request=self.request)
        scripts_list = p.page(page)

        context = {
            "jobs_active": "active",
            "scripts_manage_active": "active",
            "scripts_list": scripts_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None
        self.queryset = super().get_queryset()

        if self.request.GET.get('name'):
            query = self.request.GET.get('name', None)
            self.queryset = self.queryset.filter(Q(name__icontains=query)|
                                                 Q(create_user__username__icontains=query)
                                                 ).order_by('create_date')
        else:
            self.queryset = self.queryset.filter(project__name=project).order_by('create_date')

        return self.queryset


class ScriptsAdd(LoginPermissionRequired,CreateView):
    '''
    添加脚本
    '''
    model = ScriptsManage
    form_class = ScritsManageForm
    template_name = 'jobs/scripts-add.html'
    success_url = reverse_lazy('jobs:scripts_list')

    def get_context_data(self, **kwargs):
        error = self.request.GET.get('error')
        msg = self.request.GET.get('msg')
        context = {
            "jobs_active": "active",
            "scripts_manage_active": "active",
            "error": error,
            "msg": msg,
        }

        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        comment = request.POST.get("comment")
        script_type = request.POST.get("script_type")
        content = request.POST.get("content")
        args_list = request.POST.getlist("input[]")
        create_user =  UserProfile.objects.get(email="{}".format(request.user))
        # print(content)
        # a=content.replace('\r\n','\n')
        # print(a)
        try:
            project = request.session["project"]
        except Exception as e:
            project = None

        try:
            if project is None:
                raise Exception(_("Please Choice Your Project!"))
            if args_list:
                input_args = {}
                for num in range(len(args_list)):
                    arg_name = args_list[num]
                    if len(arg_name) > 0:
                        input_args["arg{}".format(num)] = arg_name
            else:
                input_args = None
            project_obj = Project.objects.get(name=project)
            sm_obj = ScriptsManage.objects.create(name=name,comment=comment,type=int(script_type),args=input_args,content=content,create_user=create_user,project=project_obj)
        except Exception as e:
            return HttpResponseRedirect('/jobs/scripts-add/?error={}'.format(e))
        return HttpResponseRedirect(self.success_url)

class ScriptsUpdate(LoginPermissionRequired,UpdateView):
    '''
    更新密钥
    '''
    model = ScriptsManage
    form_class = ScritsManageForm
    template_name = 'jobs/scripts-edit.html'
    success_url = reverse_lazy('jobs:scripts_list')

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        script_obj = ScriptsManage.objects.get(id=pk.hex)
        script_args = eval(script_obj.args)
        context = {
            "jobs_active": "active",
            "scripts_manage_active": "active",
            "script_obj": script_obj,
            "script_args": script_args,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        name = request.POST.get("name")
        comment = request.POST.get("comment")
        content = request.POST.get("content")
        args_list = request.POST.getlist("input[]")
        update_user = UserProfile.objects.get(email="{}".format(request.user))
        try:
            if args_list:
                input_args = {}
                for num in range(len(args_list)):
                    arg_name = args_list[num]
                    if len(arg_name) > 0:
                        input_args["arg{}".format(num)] = arg_name
            else:
                input_args = None
            script_obj = ScriptsManage.objects.get(id=pk.hex)
            ucl_obg = UpdateConfigLog.objects.create(update_user=update_user, type='Script', content=script_obj.content)
            script_obj.name = name
            script_obj.comment = comment
            script_obj.content = content
            script_obj.args = input_args
            script_obj.save()
            script_obj.update.add(ucl_obg.id)
            # new_file = generate_scripts(script_obj.id, content)
            # scripts_dir = "{}/script/".format(DATA_DIR)
            #diff_content("{}/{}.old.sh".format(scripts_dir, script_obj.id), new_file,ucl_obg.id)
        except Exception as e:
            return HttpResponseRedirect('/jobs/scripts-add/?error={}'.format(e))
        return HttpResponseRedirect(self.success_url)


class ScriptsDiffList(LoginPermissionRequired,ListView):

    model = UpdateConfigLog
    form_class = ScritsManageForm
    template_name = 'jobs/scripts-diff-list.html'
    success_url = reverse_lazy('jobs:scripts_list')

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        script_name = ScriptsManage.objects.get(id=pk.hex).name
        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger as e:
            page = 1
        p = Paginator(self.queryset, getattr(settings, 'DISPLAY_PER_PAGE'), request=self.request)
        script_old = p.page(page)
        context = {
            "jobs_active": "active",
            "scripts_manage_active": "active",
            "script_name":script_name,
            "script_old": script_old,
            "pk":pk
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = super().get_queryset()
        pk = self.kwargs.get('pk')
        script_new = ScriptsManage.objects.get(id=pk.hex)
        self.queryset = script_new.update.all()
        return self.queryset

class ScriptsDiff(LoginPermissionRequired,View):

    model = UpdateConfigLog

    def get(self, request, *args, **kwargs):
        pk = self.request.GET.get("id").strip('-')
        try:
            diff_id = self.request.GET.getlist("diff_id")[0].split(',')
            new = UpdateConfigLog.objects.get(id=diff_id[1].strip('-'))
            old = UpdateConfigLog.objects.get(id=diff_id[0].strip('-'))
            if new.update_date < old.update_date:
                new_content = old.content
                old_content = new.content
            else:
                new_content = new.content
                old_content = old.content

        except Exception as e:
            diff_id = self.request.GET.getlist("diff_id")
            new_content = ScriptsManage.objects.get(id=pk).content
            old_content = UpdateConfigLog.objects.get(id=diff_id[0].strip('-')).content
        return render(request, 'jobs/scripts-diff.html', {'jobs_active': "active", "scripts_manage_active": "active",
                                                  "new_content": new_content.replace('\r\n','\\n').replace('\"','\\"'),
                                                  "old_content": old_content.replace('\r\n','\\n').replace('\"','\\"')})



# class ScriptsDiff(LoginPermissionRequired,ListView):
#
#     model = UpdateConfigLog
#     form_class = ScritsManageForm
#     template_name = 'jobs/test.html'
#     queryset = UpdateConfigLog.objects.all()
#     success_url = reverse_lazy('jobs:scripts_list')
#
#     def get_context_data(self, **kwargs):
#         #pk = self.kwargs.get(self.pk_url_kwarg, None)
#         #script_obj = ScriptsManage.objects.get(id=pk.hex)
#         context = {
#             "jobs_active": "active",
#             "scripts_manage_active": "active",
#             #"script_obj": script_obj,
#         }
#         kwargs.update(context)
#         return super().get_context_data(**kwargs)

    # form_class = ScritsManageForm
    # template_name = 'jobs/scripts-diff.html'
    # queryset = UpdateConfigLog.objects.all()
    # success_url = reverse_lazy('jobs:scripts_list')
    #
    # def get_context_data(self, **kwargs):
    #     pk = self.request.POST.get("id")
    #     diff_id = self.request.POST.getlist("diff_id[]")
    #     #script_obj = ScriptsManage.objects.get(id=pk.hex)
    #     context = {
    #         "jobs_active": "active",
    #         "scripts_manage_active": "active",
    #         #"script_obj": script_obj,
    #     }
    #     kwargs.update(context)
    #     return super().get_context_data(**kwargs)

class ScriptsAllDel(LoginPermissionRequired,DeleteView):
    """
    删除密钥
    """
    model = ScriptsManage

    def post(self, request, *args, **kwargs):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                id = request.POST.get('nid', None)
                ScriptsManage.objects.get(id=id).delete()
            else:
                ids = request.POST.getlist('id', None)
                ScriptsManage.objects.filter(id__in=ids).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = _('Deletion error，{}'.format(e))
        finally:
            return HttpResponse(json.dumps(ret))
