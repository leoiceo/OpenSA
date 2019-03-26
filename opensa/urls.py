"""opensa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from .views import IndexView,CheckCode,page_not_found,server_error,permission_denied
from .api import Choice_Project
from django.conf.urls.static import static
from opensa import settings
import os
from asset.api import AssetViewSet,IdcViewSet,ServiceViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('asset', AssetViewSet)
router.register('idc', IdcViewSet)
router.register('service', ServiceViewSet)

handler404 = page_not_found
handler500 = server_error
handler403 = permission_denied

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('choice-project/', Choice_Project.as_view(), name='choice_project'),
    path('checkcode/', CheckCode, name='checkcode'),
    path('users/', include('users.urls', namespace='users')),
    path('asset/', include('asset.urls', namespace='asset')),
    path('jobs/', include('jobs.urls', namespace='jobs')),
    path('audit/', include('audit.urls', namespace='audit')),
    path('api/', include(router.urls)),
]
