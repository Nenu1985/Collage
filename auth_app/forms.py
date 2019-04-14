# -*- coding: utf-8 -*-
from django.contrib.auth.forms import UserCreationForm

from auth_app.models import CustomUser


class CustomCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', )
