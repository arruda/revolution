# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices


@python_2_unicode_compatible
class GameRoom(models.Model):
    """
    A game room is what represents a role game:
    The players, the gameset, scores and etc..
    By joining a game room, a user can play as a player.
    """

    PHASES = Choices(
        (0, 'setup', _('Game Setup')),
        (1, 'roles_definition', _('Roles Definition')),
        (2, 'leader_definition', _('Leader Definition')),
        (3, 'mission_assignment', _('Mission Assignment')),
        (4, 'mission_votation', _('Mission Votation')),
        (5, 'mission_resolution', _('Mission Resolution')),
        (6, 'gameover_check', _('Gameover Check')),
        (7, 'gameover', _('Gameover')),
    )
    phase = models.IntegerField(choices=PHASES, default=PHASES.setup, blank=True)

    WINNERS = Choices(
        (0, 'undefined', _('Undefined')),
        (1, 'revolutionaries', _('Revolutionaries')),
        (2, 'spies', _('Spies'))
    )
    winner = models.IntegerField(choices=WINNERS, default=WINNERS.undefined, blank=True)

    def add_player(self, user):
        if self.phase == self.PHASES.setup:
            return self.player_set.create(
                user=user
            )
        else:
            return False

    def get_phase_txt(self):
        return self.PHASES[self.phase]

    def get_next_player_number(self, current_number):
        num_players = self.player_set.count()
        next_player_number = current_number + 1 if current_number < num_players else 1
        return next_player_number

    def get_active_mission(self):
        return self.mission_set.get(is_active=True)

    def assign_player_to_active_mission(self, player):
        active_mission = self.get_active_mission()
        active_mission.assigned_players.add(player)

    def define_leader(self):
        """
        Define the next leader.
        It's the next player after the current leader, or, if there is no Leader,
        then it's player 1
        """
        try:
            last_leader = self.player_set.get(is_leader=True)
        except Player.DoesNotExist:
            last_leader = None
            next_leader = self.player_set.get(number=1)
        else:
            next_player_number = self.get_next_player_number(last_leader.number)
            next_leader = self.player_set.get(number=next_player_number)

        next_leader.is_leader = True
        next_leader.save()
        if last_leader:
            last_leader.is_leader = False
            last_leader.save()

        return next_leader

    def phase_resolution(self):
        """
        Work out the current phase.
        """

        if self.phase == self.PHASE.setup:
            self.setup_game()
            self.phase = self.PHASE.roles_definition

        elif self.phase == self.PHASE.roles_definition:
            self.phase = self.PHASE.leader_definition

        elif self.phase == self.PHASE.leader_definition:
            self.define_leader()
            self.phase = self.PHASE.mission_assignment

        elif self.phase == self.PHASE.mission_assignment:
            self.phase = self.PHASE.mission_votation

        elif self.phase == self.PHASE.mission_votation:
            if self.mission_votes_passed():
                self.phase = self.PHASE.mission_resolution
            else:
                self.phase = self.PHASE.leader_definition

        elif self.phase == self.PHASE.mission_resolution:
            self.phase = self.PHASE.gameover_check

        elif self.phase == self.PHASE.gameover_check:
            if self.check_for_gameover():
                self.phase = self.PHASE.gameover
            else:
                self.phase = self.PHASE.leader_definition

        self.save()

    def setup_game(self):
        """
        Start a game
        """
        amount_players = self.player_set.all().count()

        if amount_players < 5:
            return False

        # sets the player's numbers
        player_number = 1
        for player in self.player_set.all():
            player.number = player_number
            player.save()

        # config missions
        num_missions = 5
        if amount_players == 5:
            num_spies = 2
            mission_assignments = [2, 3, 2, 3, 3]
        elif amount_players == 6:
            num_spies = 2
            mission_assignments = [2, 3, 4, 3, 4]

        elif amount_players == 7:
            num_spies = 3
            mission_assignments = [2, 3, 3, 4, 4]

        elif amount_players == 8 or amount_players == 9:
            num_spies = 3
            mission_assignments = [3, 4, 4, 5, 5]

        elif amount_players == 10:
            num_spies = 4
            mission_assignments = [3, 4, 4, 5, 5]

        num_rev = amount_players - num_spies
        for n_mission in xrange(0, num_missions):
            is_first_mission = True if n_mission == 0 else False

            self.mission_set.create(
                amount_players=mission_assignments[n_mission],
                is_active=is_first_mission
            )
        return True

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse('games:detail', args=[str(self.pk)])


@python_2_unicode_compatible
class Player(models.Model):
    """
    A player in a game room, that is the representation of a user
    with a information if it's a revolutionary or a spy role.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    gameroom = models.ForeignKey(GameRoom)
    number = models.IntegerField(_("Player Number"), default=1, blank=True)
    is_leader = models.BooleanField(_("Leader"), default=False, blank=True)
    is_ready = models.BooleanField(_("Ready"), default=False, blank=True)

    ROLES = Choices(
        (0, 'revolutionary', _('Revolutionary')),
        (1, 'spy', _('Spy'))
    )
    role = models.IntegerField(choices=ROLES, default=ROLES.revolutionary, blank=True)

    def __str__(self):
        return self.user.name


@python_2_unicode_compatible
class Mission(models.Model):
    """
    Represents one mission in a game room.
    It contains what where the votations for this mission assignment
    and what was the final outcome of this mission (sucess/failure)
    """

    gameroom = models.ForeignKey(GameRoom)

    amount_players = models.IntegerField(_('Amount of players'), default=2, blank=True)
    is_active = models.BooleanField(_('Active'), default=False, blank=True)

    OUTCOMES = Choices(
        (0, 'undefined', _('Undefined')),
        (1, 'success', _('Success')),
        (2, 'failure', _('Failure'))
    )
    outcome = models.IntegerField(choices=OUTCOMES, default=OUTCOMES.undefined, blank=True)

    assigned_players = models.ManyToManyField(Player, verbose_name=_("Assigned Players"))

    # mission_number = models.IntegerField(_('Mission Number'), default=1, blank=True)

    def __str__(self):
        return self.OUTCOMES[self.outcome]


@python_2_unicode_compatible
class AssignmentVote(models.Model):
    """
    A vote from a player in a mission assignment
    """
    mission = models.ForeignKey(Mission)
    player = models.ForeignKey(Player)

    result = models.BooleanField(_('Result'), default=False, blank=True)

    def __str__(self):
        return "%s/%s"(self.player, self.result)


@python_2_unicode_compatible
class MissionResolution(models.Model):
    """
    A decision for the mission Resolution
    of one of the players that where assigned for this mission
    """
    mission = models.ForeignKey(Mission)
    player = models.ForeignKey(Player)

    outcome = models.BooleanField(_('Outcome'), default=True, blank=True)

    def __str__(self):
        return "%s/%s"(self.player, self.result)