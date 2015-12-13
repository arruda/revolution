# -*- coding: utf-8 -*-
import os
from django.core.management.base import NoArgsCommand
from revolution.games.models import GameRoom
from revolution.users.models import User

class Command(NoArgsCommand):
    help = "prepare game and players"

    def handle(self, *args, **options):
        GameRoom.objects.all().delete()
        User.objects.all().exclude(username='root').delete()
        users = []
        for i in range(4):
            user = User(username='p%d' % i, email="p%d@email.com" % i)
            user.set_password('p%d' % i)
            user.save()
            user.emailaddress_set.create(primary=True, verified=True, email=user.email)
            user.save()
            users.append(user)

        gameroom = GameRoom()
        gameroom.save()
        for user in users:
            gameroom.add_player(user)
        gameroom.save()
        for player in gameroom.player_set.all():
            player.is_ready = True
            player.save()
        print(gameroom.get_add_player_url())