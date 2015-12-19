# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, FormView
from django.views.generic import CreateView

from braces.views import LoginRequiredMixin

from .models import GameRoom, Player
from .forms import PlayerChangeReadyStateForm, PlayerIsLeaderStateForm, PlayerVoteForMissionStateForm


class GameRoomListView(LoginRequiredMixin, ListView):
    model = GameRoom

    def get_queryset(self):
        return self.request.user.get_user_gamerooms()

class GameRoomEnterPlayerRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    query_string = True
    pattern_name = 'games:detail'

    def get_redirect_url(self, *args, **kwargs):
        gameroom = get_object_or_404(GameRoom, pk=kwargs['pk'])
        if gameroom.add_player(self.request.user):
            return super(GameRoomEnterPlayerRedirectView, self).get_redirect_url(*args, **kwargs)
        else:
            return reverse('home')


class GameRoomDetailView(LoginRequiredMixin, DetailView):
    model = GameRoom

    slug_field = "pk"
    slug_url_kwarg = "pk"

    def get_current_player(self):
        current_player = self.object.player_set.get(user=self.request.user)
        self.current_player = current_player
        return current_player

    def get_player_state_form(self):

        form = PlayerChangeReadyStateForm(instance=self.current_player)

        if self.object.phase == self.object.PHASES.mission_assignment:
            if self.current_player.is_leader:
                form = PlayerIsLeaderStateForm(instance=self.current_player)
        elif self.object.phase == self.object.PHASES.mission_votation:
            form = PlayerVoteForMissionStateForm(instance=self.current_player)

        self.player_state_form = form
        return self.player_state_form

    def get_context_data(self, **kwargs):
        self.get_current_player()
        context = {}
        context['player'] = self.current_player
        context['player_ready_form'] = self.get_player_state_form()

        return super(GameRoomDetailView, self).get_context_data(**context)


class GameRoomCreateView(LoginRequiredMixin, CreateView):
    model = GameRoom
    fields = []

    def form_valid(self, form):
        self.object = form.save()
        self.object.add_player(self.request.user)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class PlayerChangeReadyStateView(LoginRequiredMixin, UpdateView):
    model = Player
    form_class = PlayerChangeReadyStateForm

    slug_field = "pk"
    slug_url_kwarg = "pk"

    def form_valid(self, form):
        response = super(PlayerChangeReadyStateView, self).form_valid(form)
        gameroom = self.object.gameroom
        if self.get_form_class() == PlayerIsLeaderStateForm:
            players_to_mission = form.cleaned_data['players_to_mission']
            gameroom.add_players_to_active_mission(players_to_mission)
        elif self.get_form_class() == PlayerVoteForMissionStateForm:
            vote = form.cleaned_data['vote']
            self.object.vote_for_mission(gameroom.get_active_mission(), vote)
        gameroom.check_all_players_ready()
        return response

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return self.object.gameroom.get_absolute_url()


    def get_player_state_form(self):

        form = PlayerChangeReadyStateForm

        if self.object.gameroom.phase == self.object.gameroom.PHASES.mission_assignment:
            if self.object.is_leader:
                form = PlayerIsLeaderStateForm
        elif self.object.gameroom.phase == self.object.gameroom.PHASES.mission_votation:
            form = PlayerVoteForMissionStateForm

        self.player_state_form = form
        return self.player_state_form

    def get_form_class(self):
        return self.get_player_state_form()