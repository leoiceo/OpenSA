#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import UserProfile, DepartMent, Project, PermissionList, RoleList, KeyManage, MenuList

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Username'), max_length=100)
    password = forms.CharField(
        label=_('Password'), widget=forms.PasswordInput,
        max_length=128, strip=False
    )

    def confirm_login_allowed(self, user):
        if not user.is_staff:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',)


class UsersFormAdd(forms.ModelForm):

    password = forms.CharField(
        label=_('Password'),
        widget=forms.DateInput(
            attrs={
                'type': 'password',
            }
        ),
        required=False,
        min_length=7,
    )

    password1 = forms.CharField(
        label=_("Please repeat the new password"),
        error_messages={'required': _("Input password error")},
        widget=forms.DateInput(
            attrs={
                'type': 'password',
            }
        ),
        required=False,
        min_length=7,
    )


    def clean(self):
        cleaned_data = super(UsersFormAdd, self).clean()

        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('password1')

        if password1 and password2:
            if password1 != password2:
                self._errors['password'] = self.error_class([_("Enter a different password twice")])

        value = cleaned_data.get('username')

        try:
            UserProfile.objects.get(username=value)
            self._errors['username'] = self.error_class([_("{} User information already exists".format(value))])
        except UserProfile.DoesNotExist:
            pass
        return cleaned_data

    class Meta:
        model = UserProfile
        exclude = ("id",)
        fields = ["username", "password","password1","email", "department", "mobile", "project", "level", "role",
                  "is_active", "is_superuser", "comment" ]
        widgets = {
            'project': forms.SelectMultiple(
                attrs={'class': 'select2'}
            ),
            'is_active': forms.Select(
                choices=((True, _("Account to Start")), (False, _("Account Closed"))),
                attrs={'class': 'select1', }
            ),
            'is_superuser': forms.Select(
                choices=((True, _("Superuser")), (False, _("Username"))),
                attrs={'class': 'select1', }
            )
        }

        help_texts = {
            'hostname': _("* mandatory field"),
            'email': _("* mandatory field"),
        }
        error_messages = {
            'model': {
                'max_length': _("* The password is too short"),
            }
        }

class UsersForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        # fields='__all__'
        exclude = ("id",)
        fields = ["username", "email", "department", "mobile", "project", "level", "role",
                  "is_active", "is_superuser", "comment"]
        widgets = {
            'project': forms.SelectMultiple(
                attrs={'class': 'select2', }
            ),
            'is_active': forms.Select(
                choices=((True, _("Account to Start")), (False, _("Account Closed"))),
                attrs={'class': 'select1', }
            ),
            'is_superuser': forms.Select(

                choices=((True, _("Superuser")), (False, _("Username"))),
                attrs={'class': 'select1', }
            )
        }

        help_texts = {

            'hostname': _("* mandatory field"),
            'email': _("* mandatory field"),
        }
        error_messages = {
            'model': {
                'max_length': ('太短了'),
            }
        }

class GroupsForm(forms.ModelForm):
    username = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.all(),
        label=_('Username'),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
            }
        ),
        required=False,
    )

    def __init__(self, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('username', {})
            initial.update({
                'username': instance.userprofile_set.all(),
            })
            kwargs['initial'] = initial
        super().__init__(**kwargs)

    def save(self, commit=True):
        var = super().save(commit=commit)
        users = self.cleaned_data['username']
        var.userprofile_set.set(users)
        return var

    class Meta:
        model = DepartMent
        fields = ["name", "comment"]



class PermissionListForm(forms.ModelForm):

    menu = forms.ModelMultipleChoiceField(
        queryset=MenuList.objects.all(),
        label=_('MenuList'),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
            }
        ),
        required=False,
    )

    def clean(self):
        cleaned_data = super(PermissionListForm, self).clean()
        url = cleaned_data.get('url')

        if '/' not in url[-1:] or '/' not in url[:1]:
            self._errors['url'] = self.error_class([_("Url format error")])

    class Meta:
        model = PermissionList
        fields = ["name", "lable_name","url","menu"]

    def __init__(self,lable_name=None, *args, **kwargs):
        super(PermissionListForm, self).__init__(*args, **kwargs)
        if lable_name is not None:
            self.fields['menu'].queryset = MenuList.objects.filter(name=lable_name)


class RoleForm(forms.ModelForm):
    class Meta:
        model = RoleList
        fields = ["name"]

class KeyManageForm(forms.ModelForm):

    class Meta:
        model = KeyManage
        fields = ["name","user" ,"password","private","public"]
        widgets = {
            'private' :forms.Textarea(
                attrs={'style':'height:500px'}
            )
        }

class ProjectForm(forms.ModelForm):

    username = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.all(),
        label=_('Username'),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
            }
        ),
        required=False,
    )

    def __init__(self, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('username', {})
            initial.update({
                'username': instance.userprofile_set.all(),
            })
            kwargs['initial'] = initial
        super().__init__(**kwargs)

    def save(self, commit=True):
        var = super().save(commit=commit)
        users = self.cleaned_data['username']
        var.userprofile_set.set(users)
        return var

    class Meta:
        model = Project
        fields = ["name", "mini_name", "username", "key", "comment"]
        exclude = ("id",)

        widgets = {
            'key': forms.SelectMultiple(
                attrs={'class': 'select2', }
            ),
        }


        help_texts = {
            'name': _("* mandatory field"),
        }



class ProjectFormAdd(forms.ModelForm):

    username = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.all(),
        label=_('Username'),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
            }
        ),
        required=False,
    )

    def __init__(self, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('username', {})
            initial.update({
                'username': instance.Project.all(),
            })
            kwargs['initial'] = initial
        super().__init__(**kwargs)

    def save(self, commit=True):
        var = super().save(commit=commit)
        users = self.cleaned_data['username']
        var.userprofile_set.set(users)
        return var


    def clean(self):
        cleaned_data = super(ProjectFormAdd, self).clean()
        value = cleaned_data.get('name')
        try:
            Project.objects.get(name=value)
            self._errors['name'] = self.error_class([_("{} User information already exists".format(value))])
        except Project.DoesNotExist:
            pass
        return cleaned_data


    class Meta:
        model = Project
        fields = ["name", "mini_name", "username","key", "comment"]
        exclude = ("id",)

        widgets = {
            'key': forms.SelectMultiple(
                attrs={'class': 'select2', }
            ),
        }

        help_texts = {
            'name': _("* mandatory field"),
        }