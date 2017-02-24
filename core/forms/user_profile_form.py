# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError

from core.models import Profile


class UserProfileForm(forms.ModelForm):

    def clean_phone(self):
        """Ensure phone is unique"""
        phone = self.cleaned_data.get('phone')
        if Profile.objects.filter(phone=phone). \
                exclude(pk=self.instance.pk).exists():
            raise ValidationError(
                u'This phone is already registered.',
                code='invalid'
            )

        return phone

    class Meta:
        model = Profile
        fields = ['phone', ]
