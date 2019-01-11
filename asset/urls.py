#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
from __future__ import absolute_import

from django.urls import path

from asset.views import asset,idc, product, use, workenv, area
#from . import views
app_name = 'asset'

urlpatterns = [

    # Asset View
    path('asset-list/', asset.AssetListAll.as_view(), name='asset_list'),
    path('asset-add/', asset.AssetAdd.as_view(), name='asset_add'),
    path('asset-update/<uuid:pk>/', asset.AssetUpdate.as_view(), name='asset_update'),
    path('asset-all-del/', asset.AssetAllDel.as_view(), name='asset_all_del'),
    path('asset-detail/<uuid:pk>/', asset.AssetDetail.as_view(), name='asset_detail'),
    path('asset-tree/', asset.AssetZtree, name='asset_ztree'),

    # IDC View
    path('idc-list/', idc.IdcList.as_view(), name='idc_list'),
    path('idc-add/', idc.IdcAdd.as_view(), name='idc_add'),
    path('idc-update/<int:pk>/', idc.IdcUpdate.as_view(), name='idc_update'),
    path('idc-all-del/', idc.IdcDel.as_view(), name='idc_all_del'),

    # Product View
    path('product-list/', product.ProductList.as_view(), name='product_list'),
    path('product-add/', product.ProductAdd.as_view(), name='product_add'),
    path('product-update/<int:pk>/', product.ProductUpdate.as_view(), name='product_update'),
    path('product-all-del/', product.ProductDel.as_view(), name='product_all_del'),

    # Server Use View
    path('use-list/', use.UseList.as_view(), name='use_list'),
    path('use-add/', use.UseAdd.as_view(), name='use_add'),
    path('use-update/<int:pk>/', use.UseUpdate.as_view(), name='use_update'),
    path('use-all-del/', use.UseDel.as_view(), name='use_all_del'),

    # Workenv View
    path('workenv-list/', workenv.WorkEnvList.as_view(), name='workenv_list'),
    path('workenv-add/', workenv.WorkEnvAdd.as_view(), name='workenv_add'),
    path('workenv-update/<int:pk>/', workenv.WorkEnvUpdate.as_view(), name='workenv_update'),
    path('workenv-all-del/', workenv.WorkEnvDel.as_view(), name='workenv_all_del'),

    # Area View
    path('area-list/', area.AreaList.as_view(), name='area_list'),
    path('area-add/', area.AreaAdd.as_view(), name='area_add'),
    path('area-update/<int:pk>/', area.AreaUpdate.as_view(), name='area_update'),
    path('area-all-del/', area.AreaDel.as_view(), name='area_all_del'),
]