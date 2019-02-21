class _PowerUse():
    def __init__(self, power, priority, args):
        self.priority = priority
        self.power = power
        self.args = args

    def use():
        return self.power(args)



class _Role():

    def __init__(self, game):
        self.game = game

    short_name = "please don't use this placeholder"
    long_name = "ERROR"
    description = "If you're seeing this, somebody screwed up."
    faction = None
    power_dict = {}
    
class Townie(_Role):

    short_name = "town"
    long_name = "Townie"
    description = "An average law-abiding citizen. Try to root out the scum, but be careful you don't get stabbed!"
    faction = "town"

class Thug(_Role):
    short_name = "thug"
    long_name = "Thug"
    description = ("If you think he looks bad, you should see the other guy."
                   "Take out the Mafia's enemies, but don't get found out."
                   "Use 'maf!power 1 [target]' to kill somebody at night.")
    faction = "mafia"



#todo: Maybe make this automatic?
role_dict = {
    "town":Townie,
    "thug":Thug
}
