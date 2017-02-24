# -*- coding: utf-8 -*-

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    """So username is not a required field"""

    class Meta:
        model = User
        fields = ['password1', 'password2']
