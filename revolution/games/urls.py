# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    # URL pattern for the UserListView
    url(
        regex=r'^$',
        view=views.GameRoomListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^~enter-game/(?P<pk>[\w.@+-]+)/$',
        view=views.GameRoomEnterPlayerRedirectView.as_view(),
        name='enter-game'
    ),
    url(
        regex=r'^(?P<pk>[\w.@+-]+)/$',
        view=views.GameRoomDetailView.as_view(),
        name='detail'
    ),
    url(
        regex=r'^~create/$',
        view=views.GameRoomCreateView.as_view(),
        name='create'
    ),
    url(
        regex=r'^~player-ready/(?P<pk>[\w.@+-]+)/$',
        view=views.PlayerChangeReadyStateView.as_view(),
        name='player-ready'
    ),
]
