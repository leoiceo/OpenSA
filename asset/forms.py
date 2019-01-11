#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from users.models import Project, UserProfile
from .models import Asset, ServerUse, Idc, Product, Work_Env, Area


class AssetForm(forms.ModelForm):

    use = forms.ModelMultipleChoiceField(
        queryset=ServerUse.objects.all(),
        label=_("Server Use"),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
            }
        ),
        required=False,
    )

    # def __init__(self,user=None,*args, **kwargs):
    #     super(AssetForm, self).__init__(*args, **kwargs)
    #     users = UserProfile.objects.get(username=user)
    #     if users.is_superuser:
    #         self.fields['project'].queryset = Project.objects.all()
    #     else:
    #         self.fields['project'].queryset = Project.objects.filter(Project_user=users.id)

    class Meta:
        model = Asset
        # fields='__all__'
        exclude = ("id",)
        fields = ["hostname", "ip", "other_ip", "port", "user", "password", "asset_type", "status",
                  "project", "idc", "product",  "work_env", "use", "os_type",  "system_version", "mac",
                  "cpu_type", "cpu_core", "cpu_total", "sn", "memory",
                  "disk_info", "disk_mount", "server_type",
                  "os_kernel", "system_arch"]


        widgets = {
            'password': forms.DateInput(
                attrs={'type': 'password'}
            )
        }

        help_texts = {
            'hostname':_("* mandatory field"),
            'ip': _("* mandatory field"),
            'user': _("* mandatory field"),
            'port': _("* mandatory field"),
            'password': _("* mandatory field"),
        }
        error_messages = {
            'model': {
                'max_length': _('Input parameters are too short'),
            }
        }


class AssetFormAdd(forms.ModelForm):

    use = forms.ModelMultipleChoiceField(
        queryset=ServerUse.objects.all(),
        label=_("Server Use"),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
            }
        ),
        required=False,
    )

    def clean(self):
        cleaned_data = super(AssetFormAdd, self).clean()
        value = cleaned_data.get('ip')
        try:
            Asset.objects.get(ip=value)
            self._errors['ip'] = self.error_class([_("{} User information already exists".format(value))])
        except Asset.DoesNotExist:
            pass
        return cleaned_data

    # def __init__(self,user=None,*args, **kwargs):
    #     super(AssetFormAdd, self).__init__(*args, **kwargs)
    #     userss = UserProfile.objects.get(username=user)
    #     if userss.is_superuser:
    #         self.fields['project'].queryset = Project.objects.all()
    #     else:
    #         self.fields['project'].queryset = Project.objects.filter(Project_user=userss.id)

    class Meta:
        model = Asset
        exclude = ("id",)
        fields = ["hostname", "ip", "other_ip", "port", "user", "password", "asset_type", "status",
                  "project", "idc", "product",  "work_env", "use", "os_type",  "system_version", "mac",
                  "cpu_type", "cpu_core", "cpu_total", "sn", "memory",
                  "disk_info", "disk_mount", "server_type",
                  "os_kernel", "system_arch"]


        widgets = {
            'password': forms.DateInput(
                attrs={'type': 'password'}
            )
        }

        help_texts = {
            'hostname': _("* mandatory field"),
            'ip': _("* mandatory field"),
            'user': _("* mandatory field"),
            'port': _("* mandatory field"),
            'password': _("* mandatory field")
        }
        error_messages = {
            'model': {
                'max_length': _('Input parameters are too short'),
            }
        }



class IdcForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(IdcForm, self).clean()
        value = cleaned_data.get('name')
        try:
            Idc.objects.get(name=value)
            self._errors['name'] = self.error_class([_("{} User information already exists".format(value))])
        except Idc.DoesNotExist:
            pass
        return cleaned_data

    class Meta:
        model = Idc
        fields = ["name", "address", "net_line", "bandwidth", "linkman", "phone", "cabinet_info", "ip_range", "comment",
                  "area"]
        exclude = ("id",)

        help_texts = {
            'name': _("* mandatory field"),
        }

class IdcFormUpdate(forms.ModelForm):



    class Meta:
        model = Idc
        fields = ["name", "address", "net_line", "bandwidth", "linkman", "phone", "cabinet_info", "ip_range", "comment",
                  "area"]
        exclude = ("id",)

        help_texts = {
            'name': _("* mandatory field"),
        }



class ProductForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(ProductForm, self).clean()
        value = cleaned_data.get('name')
        try:
            Product.objects.get(name=value)
            self._errors['name'] = self.error_class([_("{} User information already exists".format(value))])
        except Product.DoesNotExist:
            pass
        return cleaned_data

    class Meta:
        model = Product
        fields = ["name","mini_name"]
        exclude = ("id",)

        help_texts = {
            'name': _("* mandatory field"),
        }

class ProductFormUpdate(forms.ModelForm):

    class Meta:
        model = Product
        fields = ["name","mini_name"]
        exclude = ("id",)

        help_texts = {
            'name': _("* mandatory field"),
        }

class UseForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(UseForm, self).clean()
        value = cleaned_data.get('name')
        try:
            ServerUse.objects.get(name=value)
            self._errors['name'] = self.error_class([_("{} User information already exists".format(value))])
        except ServerUse.DoesNotExist:
            pass
        return cleaned_data

    class Meta:
        model = ServerUse
        fields = ["name","mini_name"]
        exclude = ("id",)

        help_texts = {
            'name': _("* mandatory field"),
        }

class UseFormUpdate(forms.ModelForm):

    class Meta:
        model = ServerUse
        fields = ["name","mini_name"]
        exclude = ("id",)

        help_texts = {
            'name': _("* mandatory field"),
        }


class WorkenvForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(WorkenvForm, self).clean()
        value = cleaned_data.get('name')
        try:
            Work_Env.objects.get(name=value)
            self._errors['name'] = self.error_class([_("{} User information already exists".format(value))])
        except Work_Env.DoesNotExist:
            pass
        return cleaned_data

    class Meta:
        model = Work_Env
        fields = ["name","mini_name"]
        exclude = ("id",)

        help_texts = {
            'name': _("* mandatory field"),
        }

class WorkenvFormUpdate(forms.ModelForm):

    class Meta:
        model = Work_Env
        fields = ["name","mini_name"]
        exclude = ("id",)

        help_texts = {
            'name': _("* mandatory field"),
        }

class AreaFormUpdate(forms.ModelForm):

    class Meta:
        model = Area
        fields = ["name","mini_name"]
        exclude = ("id",)

        help_texts = {
            'name': _("* mandatory field"),
        }

class AreaForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(AreaForm, self).clean()
        value = cleaned_data.get('name')
        try:
            Area.objects.get(name=value)
            self._errors['name'] = self.error_class([_("{} User information already exists".format(value))])
        except Area.DoesNotExist:
            pass
        return cleaned_data

    class Meta:
        model = Area
        fields = ["name","mini_name"]
        exclude = ("id",)

        help_texts = {
            'name': _("* mandatory field"),
        }