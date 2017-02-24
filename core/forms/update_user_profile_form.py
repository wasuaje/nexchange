# -*- coding: utf-8 -*-

from django import forms

from core.models import Profile


class UpdateUserProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name']
