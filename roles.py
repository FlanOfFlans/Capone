import functools
import random


class _Role():
    def __init__(self, game):
        self.game = game

    def target_power(self, args):

        if args[0] == "unset":
            self.power_call = lambda _: None
            return "Power targetting reset."

    def can_be_killed(self, source):
        if self.attribs.get("protected", False):
            return False
        else:
            return True

    def dawn(self):
        pass

    def dusk(self):
        voted_for = None

    short_name = "please don't use this placeholder"
    long_name = "ERROR"
    description = "If you're seeing this, somebody screwed up."
    faction = None
    power_call = None
    attribs = {}
    voted_for = None

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

    def target_power(self, args):
        n = super().target_power(args)
        if n != None:
            return n

        if args[0] == "kill":
            if len(args) < 2:
                return "Insufficient arguments."

            for player in self.game.players:
                if args[1] == str(player):
                    target = player
                    break
            else:
                return ("Target player not found. "
                        "Note that only usernames, "
                        "not nicknames, can be used, "
                        "and the discriminator (#1234)"
                        "is required.")

            print(type(target))
            self.power_call = functools.partial(
                    self.game.try_to_kill, [target, self])
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
