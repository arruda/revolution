# -*- coding: utf-8 -*-
import os
from django.core.management.base import BaseCommand, CommandError
from revolution.games.models import GameRoom
from revolution.users.models import User

class Command(BaseCommand):
    help = "prepare game and players"

    def add_arguments(self, parser):
        parser.add_argument('gameroom_id', nargs='+', type=int)

    def handle(self, *args, **options):
        root = User.objects.get(username='root')
        for gameroom_id in options['gameroom_id']:
            try:
                gameroom = GameRoom.objects.get(pk=gameroom_id)
            except GameRoom.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)

            for player in gameroom.player_set.all():
                if player.user != root:
                    player.is_ready = True
                    player.save()

            self.stdout.write('All players(- root) from "%s" are ready' % gameroom.get_absolute_url())
