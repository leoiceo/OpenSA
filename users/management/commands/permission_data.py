#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo
from django.core.management.base import BaseCommand
from users.models import PermissionList,Project,UserProfile,MenuList
from asset.models import Asset,Idc,Area,Product,ServerUse,Work_Env
from django.utils.translation import ugettext as _

class Command(BaseCommand):
    help = 'Import permission data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('begin import'))
        self.permission_data()
        self.init_data()
        self.stdout.write(self.style.SUCCESS('end import'))


    def permission_data(self):
        # clear all data

        MenuList.objects.all().delete()
        MenuListInfo = [
            {"first":"asset-list","name":"asset_list"},
            {"first":"idc-list","name": "asset_list"},
            {"first": "product-list","name": "asset_list"},
            {"first": "use-list","name": "asset_list"},
            {"first": "workenv-list","name": "asset_list"},
            {"first": "area-list","name": "asset_list"},
            {"first": "scripts-list","name": "jobs_list"},
            {"first": "periodictasks","name": "jobs_list"},
            {"first": "crontabs","name": "jobs_list"},
            {"first": "intervals","name": "jobs_list"},
            {"first": "batch-files","name": "jobs_list"},
            {"first": "batchcmd","name": "jobs_list"},
            {"first": "batch-scripts","name": "jobs_list"},
            {"first": "batch-tasks","name": "jobs_list"},
            {"first": "orchestration-list","name": "jobs_list"},
            {"first": "login-log","name": "audit_list"},
            {"first": "request-log","name": "audit_list"},
            {"first": "jobs-log","name": "audit_list"},
            {"first": "password-change-log","name": "audit_list"},
            {"first": "user-manage","name": "users_list"},
            {"first": "role-manage","name": "users_list"},
            {"first": "project-manage","name": "users_list"},
            {"first": "user-manage","name": "users_list"},
            {"first": "department-manage","name": "users_list"},
            {"first": "permission-manage","name": "users_list"},
        ]

        for i in MenuListInfo:
            MenuList.objects.create(name=i["name"],first=i["first"])

        PermissionList.objects.all().delete()
        PermissionListInfo = [
            {
                "name":_("System Setup"),
                "lable_name":"users_list",
                "url":"/users/"
            },{
                "name": _("Service Manage"),
                "lable_name": "asset_list",
                "url": "/asset/"
            },{
                "name": _("Audits"),
                "lable_name": "audit_list",
                "url": "/audit/"
            },{
                "name": _("Jobs Manage"),
                "lable_name": "jobs_list",
                "url": "/jobs/"
            },

        ]

        for i in PermissionListInfo:
            PermissionList.objects.create(name=i["name"],lable_name=i["lable_name"],url=i["url"])


    def init_data(self):
        UserProfile.objects.all().delete()
        UserProfile.objects.create(email="opensa@imdst.com", username="opensa",is_superuser=True,is_active=True,level=2,
                                   password="pbkdf2_sha256$120000$59U5Ujk0NU5w$qqQupYAaNOZf0R1gC3Gz3Y57XQeY0XVKRxDFTF0vR9A=",
                                   )