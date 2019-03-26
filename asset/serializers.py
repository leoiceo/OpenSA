#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo

from rest_framework import serializers
from asset.models import Asset,Idc,Service

class AssetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Asset
        fields = ('hostname','ip')


class IdcSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Idc
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'