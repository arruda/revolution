# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.views.generic import CreateView

from braces.views import LoginRequiredMixin

from .models import GameRoom, Player
from .forms import PlayerChangeReadyStateForm


class GameRoomDetailView(LoginRequiredMixin, DetailView):
    model = GameRoom

    slug_field = "pk"
    slug_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        context = {}
        # raise Exception()
        current_player = self.object.player_set.get(user=self.request.user)
        context['player'] = current_player
        context['player_ready_form'] = PlayerChangeReadyStateForm(instance=current_player)

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

    def get_success_url(self):
        return self.object.gameroom.get_absolute_url()
