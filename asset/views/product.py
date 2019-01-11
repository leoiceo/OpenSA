#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

from __future__ import unicode_literals

import json
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.utils.translation import ugettext as _
from asset.models import Product
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
from opensa.api import LoginPermissionRequired
from ..forms import ProductForm,ProductFormUpdate

class ProductList(LoginPermissionRequired,ListView):

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
            ret['status'] = False
            ret['error'] = _('Deletion error，{}'.format(e))
        finally:
            return HttpResponse(json.dumps(ret))

