#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
from __future__ import absolute_import

from django.urls import path

from users.views import login, users, groups, project, permission,role,keys
#from . import views
app_name = 'users'

urlpatterns = [
    # Login View
    path('login/', login.UserLoginView.as_view(), name='login'),
    path('logout/', login.UserLogoutView.as_view(), name='logout'),

    # User View
    path('users-list/', users.UsersListAll.as_view(), name='users_list'),
    path('users-add/', users.UsersAdd.as_view(), name='users_add'),
    path('users-update/<int:pk>/', users.UsersUpdate.as_view(), name='users_update'),
    path('users-all-del/', users.UsersAllDel.as_view(), name='users_all_del'),
    path('users-change-password/', users.UsersChangePassword.as_view(), name='users_change_password'),
    path('users-detail/<int:pk>/', users.UsersDetail.as_view(), name='users_detail'),

    # DepartMent View
    path('groups-list/', groups.GroupsListAll.as_view(), name='groups_list'),
    path('groups-add/', groups.GroupsAdd.as_view(), name='groups_add'),
    path('groups-update/<int:pk>/', groups.GroupsUpdate.as_view(), name='groups_update'),
    path('groups-all-del/', groups.GroupsAllDel.as_view(), name='groups_all_del'),

    # Project View
    path('project-list/', project.ProjectListAll.as_view(), name='project_list'),
    path('project-add/', project.ProjectAdd.as_view(), name='project_add'),
    path('project-update/<int:pk>/', project.ProjectUpdate.as_view(), name='project_update'),
    path('project-all-del/', project.ProjectDel.as_view(), name='project_all_del'),

    # KeyManage View
    path('key-list/', keys.KeyListAll.as_view(), name='key_list'),
    path('key-add/', keys.KeyAdd.as_view(), name='key_add'),
    path('key-update/<uuid:pk>/', keys.KeyUpdate.as_view(), name='key_update'),
    path('key-all-del/', keys.KeyAllDel.as_view(), name='key_all_del'),

    # PermissionList View
    path('permission-list/', permission.PermissionListAll.as_view(), name='permission_list'),
    path('permission-add/', permission.PermissionAdd.as_view(), name='permission_add'),
    path('permission-update/<int:pk>/', permission.PermissionUpdate.as_view(), name='permission_update'),
    path('permission-all-del/', permission.PermissionAllDel.as_view(), name='permission_all_del'),

    # RoleList View
    path('role-list/', role.RoleAll.as_view(), name='role_list'),
    path('role-edit/<int:pk>/', role.RoleEdit.as_view(), name='role_edit'),
    path('role-all-del/', role.RoleAllDel.as_view(), name='role_all_del'),

]