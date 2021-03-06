import functools
import random


class _Role():
    def __init__(self, game, player):
        self.game = game
        self.player = player

    def target_power(self, args):
        if args[0] == "unset":
            self.power_call = lambda _: None
            return "Power targetting reset."

    def check_nightkill_immunity(self, source):
        for listener in self.nightkill_listeners:
            result = listener(source)
            if result == False: return True

    def dawn(self):
        pass

    def dusk(self):
        voted_for = None

    short_name = "please don't use this placeholder"
    long_name = "ERROR"
    description = "If you're seeing this, somebody screwed up."
    faction = None
    power_call = None
    voted_for = None
    attribs = {}

    # Functions in nightkill_listeners will run on kill attempt
    # Take one argument, source, a role listing who the attacker is
    # Return True if the victim still dies, False otherwise
    nightkill_listeners = []

    # High priority goes first. Priority can be changed for each ability,
    # but it won't automatically be reset
    priority = 0
    
class Townie(_Role):

    short_name = "town"
    long_name = "Townie"
    description = ("An average law-abiding citizen. "
                   "Try to root out the scum, "
                   "but be careful you don't get stabbed!")
    faction = "town"


class Enforcer(_Role):

    def can_be_killed(self, source):
        dying = super().can_be_killed(source)

        if dying:
            maflist = [player for player, role in self.player_roles.items()
                       if player in game.players and
                       role.faction == "mafia" and
                       not role.attribs.get("no_promote", False)]            

            try:
                promoted = random.choice(maflist)
                self.game.change_role(promoted, Enforcer)
            except IndexError:
                pass

        return dying

    def enforcer_kill(self, target):
        target_role = self.game.player_roles[target]

        if not target_role.check_nightkill_immunity(self):
            self.game.kill(target)
            self.game.buffer_message("You have successfully killed {0}!".format(str(target)), self.player)
            self.game.buffer_message("You have been killed by a visitor!", target)
        else:
            self.game.buffer_message("You attempted to kill {0}, but they were immune!".format(str(target)), self.player)
            self.game.buffer_message("A visitor attempted to kill you, but you were immune!", target)

    def target_power(self, args):
        n = super().target_power(args)
        if n != None:
            return n

        if args[0] == "kill":
            if len(args) != 2:
                return "Insufficient arguments."

            if self.game.is_day:
                return "This power can only be used at night."

            try:
                target = self.game.player_ids[args[1]]
            except KeyError:
                return ("Target player not found. "
                        "Note that only usernames, "
                        "not nicknames, can be used, "
                        "and the discriminator (#1234)"
                        "is required.")

            self.power_call = functools.partial(
                    self.enforcer_kill, target)

            return "Target set."

        else:
            return "You don't have that power."
    
    short_name = "enforcer"
    long_name = "Enforcer"
    description = ("If you think he looks bad, you should see the other guy. "
                   "Take out the Mafia's enemies, but don't get found out. "
                   "Use 'maf!power kill [target]' to kill somebody at night. "
                   "If you die, a random mafia member will become an enforcer.")
    faction = "mafia"


class Goon(_Role):
    short_name = "goon"
    long_name = "Goon"
    description = "Scummy, but harmless. Cooperate with the mafia to take down the town."

role_dict = {
    "town":Townie,
    "enforcer":Enforcer,
    "goon":Goon
}
