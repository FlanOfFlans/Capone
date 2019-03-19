import time
import random
import roles

#Unstarted games older than this will be culled
_MAX_UNSTARTED_AGE = 4230 #72 hours

#Started games older than this will be culled
#Age resets when starting
_MAX_STARTED_AGE = 30240 #3 weeks

game_dict = {}

def _generate_id(depth=0):

    if depth >= 5 and depth % 5 == 0:
        print("Spending a lot of time regenerating IDs!")
    
    hex_str = hex(round(time.time()))
    
    #remove leading '0x', add hyphen after 4 hex characters
    hex_str = hex_str[2:6] + '-' + hex_str[6:]
    
    #1-digit hex number
    randomized = hex(random.randint(1, 15))
    
    #remove leading '0x' from this too
    hex_str += randomized[2:]

    #recurse until we get a unique ID
    if hex_str in game_dict:
        return _generate_id(depth + 1)
    else:
        return hex_str

class _Game():

    def __init__(self, owner, phase_time, role_list, home_channel):
        self.home_channel = home_channel

        self.owner = owner
        self.players = [owner]
        self.banned = []

        self.phase_length = phase_time
        self.remaining_phase_time = phase_time
        self.is_day = True

        self.possible_roles = role_list
        self.player_roles = {}
        self.all_players = {} #includes dead people

        
        self.started = False
        self.age = 0
        
        self.home_channel = home_channel
        self.output_buffer = []
        self.power_buffer = []
        self.vote_dict = {}

        self.id = _generate_id()
        self.culled = False
        game_dict[self.id] = self

    #Runs once per minute
    def tick(self):
        self.age += 1

        #Flags game for culling
        #The tick loop handles actually culling the game
        if not self.started and self.age > _MAX_UNSTARTED_AGE:
            self.culled = True

        if self.started and self.age > _MAX_STARTED_AGE:
            self.culled = True

        if self.started:
            self.remaining_phase_time -= 1

            if self.is_day and self.remaining_phase_time == 0:
                self._dusk()

            elif not self.is_day and self.remaining_phase_time == 0:
                self._dawn()

    def try_to_kill(target, source):
        if target.try_to_kill(source):
            kill(target)
    
    def kill(target):
        target_role = player_roles.pop(target)
        
        title = str(target) + ", the " + target_role.long_name
        self.buffer_message(title + ", has been found dead!")

    def change_role(self, target, new_role):
        role = new_role(self)
        role.attribs = target.attribs
        self.buffer_message(("You are now a " + role.long_role +"!\n"
                            "%s\n" % role.description),
                            target)

        player_roles[player] = role

    def buffer_message(self, message, channel=None):
        if channel == None:
            channel = self.home_channel

        self.output_buffer.append((message, channel))  

    def start(self):
        if self.started:
            return

        self.age = 0
        self.started = True

        unchosen_players = self.players
        for role in self.possible_roles:
            chosen_player = random.choice(unchosen_players)
            unchosen_players.remove(chosen_player)

            self.player_roles[chosen_player] = role(self)
            self.buffer_message(("You are **{0}**!\n"
                            "{1}").format(role.long_name, role.description),
                            chosen_player)

        for player in self.players:
            self.vote_dict[player] = 0
        
        self.buffer_message("The game has started!")

    def _dusk(self):
        self.buffer_message("It is now night! Town players should refrain from talking to one another at night.")

        self.is_day = False
        self.remaining_phase_time = self.phase_length

        roles = self.player_roles.values()

        for role in roles:
            role.dusk()

    def _dawn(self):
        self.buffer_message("It is now day! Town players may talk freely.")

        self.is_day = True
        self.remaining_phase_time = self.phase_length

        #Sort by priority, highest to lowest
        roles = self.player_roles.values()
        sorted(roles, key=lambda x: x.priority, reverse=True)

        for role in roles:
            try: role.power_call()
            except TypeError: pass

        for role in roles:
            role.dawn()
  

    
async def create_game(role_strings, phase_time, owner, home_channel):

    role_strings = role_strings.split(" ")
    role_list = []

    if phase_time < 1:
        return -2

    for role_string in role_strings:
        try:
            role_list.append(roles.role_dict[role_string])
        except KeyError:
            return -1

    return _Game(owner, phase_time, role_list, home_channel)


