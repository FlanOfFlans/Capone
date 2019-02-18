import time
import random
import roles

game_dict = {}

def _generate_id():
    hex_str = hex(round(time.time()))
    hex_str += "-"
    hex_str += str(random.randint(111, 999))

    if hex_str in game_dict:
        return generate_id()
    else:
        return hex_str

class _Game():

    def __init__(self, owner, phase_time, role_list):

        self.owner = owner
        self.players = [owner]

        self.phase_time = phase_time        
        self.is_day = False

        self.possible_roles = role_list
        self.role_dict = {}
        
        self.started = False
        self.age = 0
        self.home_channel = None

        self.id = _generate_id()
        games_dict[self.id] = self

def create_game(owner, phase_time, role_strings):

    role_list = []

    for role_string in role_strings:
        try:
            role_list.apppend(roles.role_dict[role_string])
        except:
            return None

    return _Game(owner, phase_time, role_list)
