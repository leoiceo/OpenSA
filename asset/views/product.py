#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

from __future__ import unicode_literals

import json
import time
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.utils.translation import ugettext as _
from django.conf import settings
from asset.models import Product,Service,Asset
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from pure_pagination import PageNotAnInteger, Paginator
from django.urls import reverse_lazy
from asset.forms import AssetFormAdd, AssetForm
from opensa.api import LoginPermissionRequired
from ..forms import ProductForm,ProductFormUpdate
import logging
logger = logging.getLogger("Opensa.log")

class ProductList(LoginPermissionRequired,ListView):
    '''
    产品列表
    '''
    template_name = 'asset/product-list.html'
    model = Product
    context_object_name = "product_list"

    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_product_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.queryset = super().get_queryset()
        queryset = self.queryset.all().order_by('id')
        return queryset


class ProductAdd(LoginPermissionRequired,CreateView):
    """
    产品增加
    """
    model = Product
    form_class = ProductForm
    template_name = 'asset/product-add-update.html'
    success_url = reverse_lazy('asset:product_list')


    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_product_active": "active",
        }
        if '__next__' in self.request.POST:
            context['i__next__'] = self.request.POST['__next__']
        else:
            try:
                context['i__next__'] = self.request.META['HTTP_REFERER']
            except Exception as e:
                pass
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def form_invalid(self, form):
        return super(ProductAdd, self).form_invalid(form)
#
class ProductUpdate(LoginPermissionRequired,UpdateView):
    '''
    产品更新信息
    '''
    model = Product
    form_class = ProductFormUpdate
    template_name = 'asset/product-add-update.html'
    success_url = reverse_lazy('asset:product_list')


    def get_context_data(self, **kwargs):

        context = {
            "asset_active": "active",
            "asset_product_active": "active",
        }
        if '__next__' in self.request.POST:
            context['i__next__'] = self.request.POST['__next__']
        else:
            try:
                context['i__next__'] = self.request.META['HTTP_REFERER']
            except Exception as e:
                pass
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def form_invalid(self, form):
        return super(ProductUpdate, self).form_invalid(form)

    def get_success_url(self):
        self.url = self.request.POST['__next__']
        return self.url

class ProductDel(LoginPermissionRequired,View):
    """
    删除产品
    """
    model = Product

    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid') :
                id = request.POST.get('nid', None)
                Product.objects.get(id=id).delete()
            else:
                ids = request.POST.getlist('id', None)
                Product.objects.filter(id__in=ids).delete()
        except Exception as e:
            logger.error(f'{e.__class__.__name__}: {e}')
            ret['status'] = False
            ret['error'] = _('Deletion error，{}'.format(e))
        finally:
            return HttpResponse(json.dumps(ret))

class ProductChat(LoginPermissionRequired,DeleteView):
    model = Product
    template_name = 'asset/product-chat.html'
    success_url = reverse_lazy('asset:product_list')

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        product_obj = Product.objects.get(id=pk)
        services = Service.objects.select_related('product').filter(product=product_obj)
        context = {
            "asset_active": "active",
            "asset_product_active": "active",
            "services": services,
            "product_obj": product_obj,
            "id": pk,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class ProductService(LoginPermissionRequired,DeleteView):
    model = Product
    template_name = 'asset/product-service.html'
    success_url = reverse_lazy('asset:product_list')

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        product_obj = Product.objects.get(id=pk)
        services = Service.objects.select_related('product').filter(product=product_obj)
        asset_obj = Asset.objects.all()

        try:
            project = self.request.session["project"]
        except Exception as e:
            project = None

        asset_myobj = asset_obj.filter(project__name=project)

        context = {
            "asset_active": "active",
            "asset_product_active": "active",
            "services": services,
            "product_obj": product_obj,
            "asset_myobj": asset_myobj,
            "pk": pk,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)