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
            # initial = kwargs.setdefault('initial', {})
            gameroom = kwargs['instance'].gameroom

            self.fields['players_to_mission'].queryset = gameroom.player_set.all()

            # # The widget for a ModelMultipleChoiceField expects
            # # a list of primary key for the selected data.
            self.initial['players_to_mission'] = [p.pk for p in gameroom.get_active_mission().assigned_players.all()]


class PlayerVoteForMissionStateForm(PlayerChangeReadyStateForm):
    vote = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        # Only in case we build the form from an instance
        if 'instance' in kwargs:
            super(PlayerVoteForMissionStateForm, self).__init__(*args, **kwargs)
            gameroom = kwargs['instance'].gameroom
            active_mission = gameroom.get_active_mission()
            last_vote_in_mission = self.instance.get_last_assignment_vote_for_mission(active_mission)
            if last_vote_in_mission:
                self.initial['vote'] = last_vote_in_mission.result


