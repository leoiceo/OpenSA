#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo

from django import forms
from django_celery_beat.models import  CrontabSchedule, PeriodicTask, IntervalSchedule
from django.utils.translation import gettext_lazy as _
from jobs.models import ScriptsManage, TaskScheduling
from users.models import KeyManage,Project
from asset.models import Asset


class ScritsManageForm(forms.ModelForm):

    class Meta:
        model = ScriptsManage
        exclude = ("id",)

        fields = [
            "name"
        ]


class CrontabScheduleForm(forms.ModelForm):

    timezone = forms.CharField(
        label=_("Time Zone"),
        initial='UTC',
        required=True,
    )

    class Meta:
        model = CrontabSchedule
        fields = '__all__'

        labels = {
            'minute': _("minute"),
            'hour': _("hour"),
            'day_of_week': _("week"),
            'day_of_month': _("month"),
            'month_of_year':  _("year"),
        }




class IntervalScheduleForm(forms.ModelForm):
    class Meta:
        model = IntervalSchedule
        fields = '__all__'

        labels = {
            'every': _('Interval'),
            'period': _('Hourly Basis'),
        }


class PeriodicTasksForm(forms.ModelForm):

    scripts = forms.ModelChoiceField(
        queryset=ScriptsManage.objects.all(),
        label=_("Scripts Name"),
        widget=forms.Select(
        ),
        required=False,
    )

    scheduling = forms.ModelChoiceField(
        queryset=TaskScheduling.objects.all(),
        label=_("Task Scheduling Name"),
        widget=forms.Select(
        ),
        required=False,
    )

    asser = forms.ModelMultipleChoiceField(
        queryset=Asset.objects.all(),
        label=_("Asset"),
        widget=forms.SelectMultiple(
            attrs={'class': 'select2', }
        ),
        required=True,
    )

    key = forms.ModelChoiceField(
         queryset=KeyManage.objects.all(),
         label=_("Key Name"),
         widget=forms.Select(),
         required=False,
    )

    task = forms.CharField(
        label=_("Tasks Name"),
        initial='jobs.tasks.crontab_scripts',
        required=False,
    )

    def clean(self):
        cleaned_data = super(PeriodicTasksForm, self).clean()
        scripts = cleaned_data.get('scripts')
        scheduling = cleaned_data.get('scheduling')

        if not scripts and not scheduling:
            self._errors['scripts'] = self.error_class(['One of scritps or scheduling must be set.'])
            self._errors['scheduling'] = self.error_class(['One of scritps or scheduling must be set.'])

        if scripts and scheduling:
            self._errors['scripts'] = self.error_class(['Only one of scritps or scheduling must be set'])
            self._errors['scheduling'] = self.error_class(['Only one of scritps or scheduling must be set'])

        value = cleaned_data.get('name')
        try:
            PeriodicTask.objects.get(name=value)
            self._errors['name'] = self.error_class([_("{} User information already exists".format(value))])
        except PeriodicTask.DoesNotExist:
            pass
        return cleaned_data


    class Meta:
        model = PeriodicTask
        fields = ['task','name','enabled','expires','description',"crontab","interval","scripts","scheduling","key","asser"]

        widgets = {
            'expires': forms.DateTimeInput(
                attrs={'id': 'begin','type': 'text'},
            ),
            'key': forms.Select(
                attrs={'placeholder': _('----- Select Key -----')},
            ),
        }

        labels = {
            'enabled': _('Start Task'),
            "expires":_('Expiration Time') ,
            'description': _('Description'),
        }

        help_texts = {
            'name': _("* mandatory field"),
            'interval':_("Use one of interval/crontab"),
            'scripts':_("Use one of scripts/scheduling")
        }

    def __init__(self,project=None, *args, **kwargs):
        super(PeriodicTasksForm, self).__init__(*args, **kwargs)
        if project == '' or project == None:
            self.fields['asser'].queryset = Asset.objects.filter(project__name=project)
            self.fields['key'].queryset = KeyManage.objects.filter(project__name=project)
            self.fields['scripts'].queryset = ScriptsManage.objects.filter(project__name=project)
            self.fields['scheduling'].queryset = TaskScheduling.objects.filter(project__name=project)
        else:
            self.fields['asser'].queryset = Asset.objects.filter(project__name=project)
            self.fields['key'].queryset = KeyManage.objects.filter(project__name=project)
            scripts = [i.id for i in ScriptsManage.objects.filter(project__name=project) if i.args == '{}']
            self.fields['scripts'].queryset = ScriptsManage.objects.filter(id__in=scripts)
            self.fields['scheduling'].queryset = TaskScheduling.objects.filter(project__name=project)

class PeriodicTasksFormUpdate(forms.ModelForm):

    scripts = forms.ModelChoiceField(
        queryset=ScriptsManage.objects.all(),
        label=_("Scripts Name"),
        widget=forms.Select(
        ),
        required=False,
    )

    scheduling = forms.ModelChoiceField(
        queryset=TaskScheduling.objects.all(),
        label=_("Task Scheduling Name"),
        widget=forms.Select(
        ),
        required=False,
    )

    asser = forms.ModelMultipleChoiceField(
        queryset=Asset.objects.all(),
        label=_("Asset"),
        widget=forms.SelectMultiple(
            attrs={'class': 'select2', }
        ),
        required=True,
    )

    key = forms.ModelChoiceField(
         queryset=KeyManage.objects.all(),
         label=_("Key Name"),
         widget=forms.Select(),
         required=False,
    )

    task = forms.CharField(
        label=_("Tasks Name"),
        initial='jobs.tasks.crontab_scripts',
        required=False,
    )

    def clean(self):
        cleaned_data = super(PeriodicTasksFormUpdate, self).clean()
        scripts = cleaned_data.get('scripts')
        scheduling = cleaned_data.get('scheduling')

        if not scripts and not scheduling:
            self._errors['scripts'] = self.error_class(['One of scritps or scheduling must be set.'])
            self._errors['scheduling'] = self.error_class(['One of scritps or scheduling must be set.'])

        if scripts and scheduling:
            self._errors['scripts'] = self.error_class(['Only one of scritps or scheduling must be set'])
            self._errors['scheduling'] = self.error_class(['Only one of scritps or scheduling must be set'])
        return cleaned_data

    class Meta:
        model = PeriodicTask
        fields = ['task','name','enabled','expires','description',"crontab","interval","scripts","scheduling","key","asser"]

        widgets = {
            'expires': forms.DateTimeInput(
                attrs={'id': 'begin','type': 'text'},
            ),
            'key': forms.Select(
                attrs={'placeholder': _('----- Select Key -----')},
            ),
        }

        labels = {
            'enabled': _('Start Task'),
            "expires":_('Expiration Time') ,
            'description': _('Description'),
        }

        help_texts = {
            'name': _("* mandatory field"),
            'interval': _("Use one of interval/crontab"),
            'scripts': _("Use one of scripts/scheduling")
        }

    def __init__(self,project=None, *args, **kwargs):
        super(PeriodicTasksFormUpdate, self).__init__(*args, **kwargs)
        if project == '' or project == None:
            self.fields['asser'].queryset = Asset.objects.filter(project__name=project)
            self.fields['key'].queryset = KeyManage.objects.filter(project__name=project)
            self.fields['scripts'].queryset = ScriptsManage.objects.filter(project__name=project)
            self.fields['scheduling'].queryset = TaskScheduling.objects.filter(project__name=project)
        else:
            self.fields['asser'].queryset = Asset.objects.filter(project__name=project)
            self.fields['key'].queryset = KeyManage.objects.filter(project__name=project)
            scripts = [i.id for i in ScriptsManage.objects.filter(project__name=project) if i.args == '{}']
            self.fields['scripts'].queryset = ScriptsManage.objects.filter(id__in=scripts)
            self.fields['scheduling'].queryset = TaskScheduling.objects.filter(project__name=project)
