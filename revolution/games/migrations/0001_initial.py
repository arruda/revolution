# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentVote',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('result', models.BooleanField(verbose_name='Result', default=False)),
            ],
        ),
        migrations.CreateModel(
            name='GameRoom',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('phase', models.IntegerField(blank=True, default=0, choices=[(0, 'Game Setup'), (1, 'Roles Definition'), (2, 'Leader Definition'), (3, 'Mission Assignment'), (4, 'Mission Votation'), (5, 'Mission Resolution'), (6, 'Gameover Check'), (7, 'Gameover')])),
                ('winner', models.IntegerField(blank=True, default=0, choices=[(0, 'Undefined'), (1, 'Revolutionaries'), (2, 'Spies')])),
            ],
        ),
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('amount_players', models.IntegerField(verbose_name='Amount of players', default=2, blank=True)),
                ('is_active', models.BooleanField(verbose_name='Active', default=False)),
                ('outcome', models.IntegerField(blank=True, default=0, choices=[(0, 'Undefined'), (1, 'Success'), (2, 'Failure')])),
            ],
        ),
        migrations.CreateModel(
            name='MissionResolution',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('outcome', models.BooleanField(verbose_name='Outcome', default=True)),
                ('mission', models.ForeignKey(to='games.Mission')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('number', models.IntegerField(verbose_name='Player Number', default=1, blank=True)),
                ('is_leader', models.BooleanField(verbose_name='Leader', default=False)),
                ('role', models.IntegerField(blank=True, default=0, choices=[(0, 'Revolutionary'), (1, 'Spy')])),
                ('gameroom', models.ForeignKey(to='games.GameRoom')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='missionresolution',
            name='player',
            field=models.ForeignKey(to='games.Player'),
        ),
        migrations.AddField(
            model_name='mission',
            name='assigned_players',
            field=models.ManyToManyField(to='games.Player', verbose_name='Assigned Players'),
        ),
        migrations.AddField(
            model_name='mission',
            name='gameroom',
            field=models.ForeignKey(to='games.GameRoom'),
        ),
        migrations.AddField(
            model_name='assignmentvote',
            name='mission',
            field=models.ForeignKey(to='games.Mission'),
        ),
        migrations.AddField(
            model_name='assignmentvote',
            name='player',
            field=models.ForeignKey(to='games.Player'),
        ),
    ]
