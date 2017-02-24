# -*- coding: utf-8 -*-

from django import forms

from referrals.models import ReferralCode


class ReferralTokenForm(forms.ModelForm):

    class Meta:
        model = ReferralCode
        fields = ['code']
