#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo

from rest_framework import viewsets
from asset.models import Asset,Idc,Service
from asset.serializers import AssetSerializer, IdcSerializer, ServiceSerializer

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

class IdcViewSet(viewsets.ModelViewSet):
    queryset = Idc.objects.all()
    serializer_class = IdcSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer