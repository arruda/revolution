# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms
from django.forms import ModelForm, Form

from .models import Player


class PlayerChangeReadyStateForm(ModelForm):

    class Meta:
        model = Player
        fields = ['is_ready']

class PlayerIsLeaderStateForm(PlayerChangeReadyStateForm):
    players_to_mission = forms.ModelMultipleChoiceField(queryset=Player.objects.all())

    def __init__(self, *args, **kwargs):
        # Only in case we build the form from an instance
        if 'instance' in kwargs:
            super(PlayerIsLeaderStateForm, self).__init__(*args, **kwargs)
            # We get the 'initial' keyword argument or initialize it
            # as a dict if it didn't exist.
            initial = kwargs.setdefault('initial', {})
            gameroom = kwargs['instance'].gameroom

            self.fields['players_to_mission'].queryset = gameroom.player_set.all()
            # # The widget for a ModelMultipleChoiceField expects
            # # a list of primary key for the selected data.
            # initial['players_to_mission'] = [p.pk for p in gameroom.player_set.all()]

