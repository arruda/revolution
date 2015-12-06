# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.forms import ModelForm

from .models import Player


class PlayerChangeReadyStateForm(ModelForm):
    class Meta:
        model = Player
        fields = ['is_ready']

