import time
import random
import roles

game_dict = {}

async def _generate_id():
    hex_str = hex(round(time.time()))
    #remove leading '0x', add hyphen after 4 hex characters
    hex_str = hex_str[2:6] + '-' + hex_str[6:len(hex_str)]
    #1-digit hex number
    randomized = hex(random.randint(1, 15))
    #remove leading '0x' from this too
    hex_str += randomized[2:len(randomized)]

    #recurse until we get a unique ID
    if hex_str in game_dict:
        return generate_id()
    else:
        return hex_str

class _Game():

    def __init__(self, owner, phase_time, role_list, home_channel):

        self.home_channel = home_channel

        self.owner = owner
        self.players = [owner]
        self.banned = []

        self.phase_time = phase_time        
        self.is_day = False

        self.possible_roles = role_list
        self.role_dict = {}
        
        self.started = False
        self.age = 0
        self.home_channel = None

        self.id = await _generate_id()
        games_dict[self.id] = self

    def kill(player):
        raise NotImplementedError()

async def create_game(role_strings, phase_time, owner, home_channel):

    role_list = []

    if phase_time >= 1:
        return -2

    for role_string in role_strings:
        try:
            role_list.apppend(roles.role_dict[role_string])
        except:
            return -1

    return _Game(owner, phase_time, role_list, home_channel)
