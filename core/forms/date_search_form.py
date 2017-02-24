# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _


class DateSearchForm(forms.Form):
    date = forms.DateField(required=False, label=_("Search by Date"))
