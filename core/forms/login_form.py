# -*- coding: utf-8 -*-

from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    """So username is labeled as "Phone\""""

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Phone'
