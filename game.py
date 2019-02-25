import time
import random
import roles

#Unstarted games older than this will be culled
_MAX_UNSTARTED_AGE = 4230 #72 hours
#Started games older than this will be culled
#Age resets when starting
_MAX_STARTED_AGE = 30240 #3 weeks

game_dict = {}

def _generate_id():
    hex_str = hex(round(time.time()))
    #remove leading '0x', add hyphen after 4 hex characters
    hex_str = hex_str[2:6] + '-' + hex_str[6:len(hex_str)]
    #1-digit hex number
    randomized = hex(random.randint(1, 15))
    #remove leading '0x' from this too
    hex_str += randomized[2:len(randomized)]

    #recurse until we get a unique ID
    if hex_str in game_dict:
        return _generate_id()
    else:
        return hex_str

class _Game():

    def __init__(self, owner, phase_time, role_list, home_channel):

        self.home_channel = home_channel

        self.owner = owner
        self.players = [owner]
        self.player_roles = {}
        self.banned = []

        self.phase_length = phase_time
        self.remaining_phase_time = phase_time
        self.is_day = True

        self.possible_roles = role_list
        self.player_roles = {}
        
        self.started = False
        self.age = 0
        
        self.home_channel = None
        self.output_buffer = []
        self.power_buffer = []

        self.id = _generate_id()
        self.culled = False
        game_dict[self.id] = self


    def _cull():
        #The tick loop handles actually culling the game
        if not started and self.age > _MAX_UNSTARTED_AGE:
            self.culled = True
        if started and self.age > _MAX_STARTED_AGE:
            self.culled = True
            
#Runs once per minute, but first tick may be shorter
    def tick():
        self.age += 1
        self.remaining_phase_time -= 1

        if is_day and self.remaining_phase_time == 0:
            self._dusk()

        elif not is_day and self.remaining_phase_time == 0:
            self._dawn()
        
        self._cull()

    def _dusk():
        self.output_buffer.append("It is now night! Town players should refrain from talking to one another at night.")

        self.is_day = False
        self.remaining_phase_time = self.phase_length

        for player in players:
            player_roles[player].dusk()

    def _dawn():
        self.output_buffer.append("It is now day! Town players may talk freely.")

        #Sort by priority, highest to lowest
        power_buffer.sort(reverse=True, key=lambda power: power.priority)
        for power in power_buffer:
            power.use()
        
        self.is_day = True
        self.remaining_phase_time = self.phase_length

        for player in players:
            player_roles[player].dawn()

    def try_to_kill(target, source):
        if target.try_to_kill(source):
            kill(target)
    
    def kill(target):
        raise NotImplementedError()


    
async def create_game(role_strings, phase_time, owner, home_channel):

    role_strings = role_strings.split(" ")
    role_list = []

    if phase_time <= 1:
        return -2

    for role_string in role_strings:
        try:
            role_list.append(roles.role_dict[role_string]())
        except KeyError:
            return -1

    return _Game(owner, phase_time, role_list, home_channel)


