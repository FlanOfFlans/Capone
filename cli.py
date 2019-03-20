import discord
import game
import math

NOT_OWNER_MESSAGE = "You do not own this game."
BAD_ID_MESSAGE = "No game found with that ID."
BAD_ARGS_MESSAGE = "Insufficient arguments for that command."
BAD_USER_MESSAGE = ("Target player not found. "
                    "Note that only usernames, "
                    "not nicknames, can be used, "
                    "and the discriminator (#1234) "
                    "is required.")

#Helper functions
#This breaks strings apart, reading things "in quotes" as one token.
async def _split_tokens(xstr):
    prev_index = 0
    string_mode = False
    tokens = []

    for index in range(0, len(xstr)):

        to_append = ""

        #Break token on spaces
        if (not string_mode) and xstr[index] == " " :
            if index == prev_index: continue
            
            to_append = xstr[prev_index:index]
            prev_index = index + 1

        #Start scanning a string
        elif (not string_mode) and xstr[index] == "\"":
            string_mode = True
            prev_index = index + 1

        #Stop scanning a string
        elif string_mode and xstr[index] == "\"":
            string_mode = False

            to_append = xstr[prev_index:index]
            prev_index = index + 2

        if to_append != "":
            tokens.append(to_append)

    #Don't lose the last token!
    if xstr[prev_index:] != "":
        tokens.append( xstr[prev_index:] )

    #Convert to ints where possible
    converted_tokens = []
    for token in tokens:
        try:
            converted_tokens.append(int(token))
        except ValueError:
            converted_tokens.append(token)

    return converted_tokens
    
async def _fetch_game(game_id):
    return game.game_dict[game_id]


#Command functions
#maf!create [roles] [phase time]
async def _create(args, author, channel):

    if type(channel) == discord.PrivateChannel:
        return "Games cannot be created in DMs. Please try again in a server."

    try:
        new_game = await game.create_game(args[0], args[1], author, channel)
    except TypeError:
        return "Phase time must be a number."
    except AttributeError:
        return "Role list must be a string."

    if new_game == -1:
        return "Invalid role in role list. Roles must be separated by commas, without spaces."
    if new_game == -2:
        return "Phases must be at least one minutes long."
        
    outstr = ("Owner: {0}\n"
              "Roles: {1}\n"
              "ID: {2}\n").format(
              new_game.owner.name,
              args[0].replace(' ', ', '),
              new_game.id)
    return outstr

async def _delete(args, author, channel):
    raise NotImplementedError

#maf!join [game id]
async def _join(args, author, channel):

    if len(args) < 1:
        return BAD_ARGS_MESSAGE
    
    try:
        target_game = await _fetch_game(args[0])
    except KeyError:
        return BAD_ID_MESSAGE

    #To prevent people guessing/mistyping IDs and joining a game they can't see.
    if channel != target_game.home_channel:
        return "You may only join a game in the channel it was created in."

    if target_game.started:
        return "This game has already begun, and cannot be joined."

    elif author in target_game.banned:
        return "You have been banned from this game."

    elif author in target_game.players:
        return "You are already in this game."

    elif len(target_game.players) >= len(target_game.possible_roles):
        return "This game is already full."

    else:
        target_game.players.append(author)
        return "Game successfully joined."
    
#maf!leave [game id]
async def _leave(args, author, channel):

    if len(args) < 1:
        return BAD_ARGS_MESSAGE

    try:
        target_game = await _fetch_game(args[0])
    except KeyError:
        return BAD_ID_MESSAGE

    #Ensure everybody can see that they left.
    #Return values always replies to author directly,
    #So a buffered message must be used instead.
    if channel != target_game.home_channel:
        target_game.buffer_message("{0} has left the game.".format(str(author)))

    try:
        if target_game.started:
            target_game.kill(author)
        else:
            target_game.players.remove(author)

        return "Game sucessfully left."
    
    except (KeyError, ValueError):
        return "You aren't in that game."

#maf!kick [game id] [target]
async def _kick(args, author, channel):

    if len(args) < 2:
        return BAD_ARGS_MESSAGE

    try:
        target_game = await _fetch_game(args[0])
    except KeyError:
        return BAD_ID_MESSAGE

    if author != target_game.owner:
        return NOT_OWNER_MESSAGE

    for player in target_game.players:
        if args[1] == str(player):
            target = player
            break
    else:
        return BAD_USER_MESSAGE

    #Ensure everybody can see it.
    if channel != target_game.home_channel:

        target_game.buffer_message("{0} has been kicked by the owner."
            .format( str(player) ))
    
    if target_game.started:
        kill(target)
    else:
        target_game.players.remove(target)

    return "Player has been kicked."

#maf!ban [game id] [target]
async def _ban(args, author, channel):

    if len(args) < 2:
        return BAD_ARGS_MESSAGE
    
    try:
        target_game = await _fetch_game(args[0])
    except KeyError:
        return BAD_ID_MESSAGE
    
    if author != target_game.owner:
            return NOT_OWNER_MESSAGE

    if target in target_game.banned:
            return "User is already banned."

    
    for member in channel.server.members:
        if args[1] == str(member):
            target = member
            break
        
    else:
        return BAD_USER_MESSAGE

    #Ensure everybody can see it
    if channel != target_game.home_channel:
        target_game.buffer_message("{0} has been banned by the owner."
            .format(str(target)))

    try:
        if target_game.started and target in target_game.players:
            kill(target)
        else:
            target_game.players.remove(target)
            
    #Banning players not in the game yet is expected
    except ValueError:
        pass

    target_game.banned.append(target)
    return "User has been banned."

#maf!unban [game id] [target]
async def _unban(args, author, channel):

    if len(args) < 2:
        return BAD_ARGS_MESSAGE

    try:
        target_game = await _fetch_game(args[0])
    except ValueError:
        return BAD_ID_MESSAGE

    if author != target_game.owner:
        return NOT_OWNER_MESSAGE
    


    for member in channel.server.members:
        if args[1] == str(member):
            target = member
            break
    else:
        return BAD_USER_MESSAGE
    
    try:
        target_game.banned.remove(target)
    except ValueError:
        return "That user is not banned."

    if channel != target_game.home_channel:
        target_game.buffer_message("{0} has been unbanned by the owner"
            .format(str(target)))

    return "User has been unbanned."

#maf!start [game id]
async def _start(args, author, channel):

    if len(args) < 1:
        return BAD_ARGS_MESSAGE

    try:
        target_game = await _fetch_game(args[0])
    except KeyError:
        return BAD_ID_MESSAGE

    if author != target_game.owner:
            return NOT_OWNER_MESSAGE
    
    
    target_game.start()
    return "Game queued to be started!"

#maf!vote [game id] [target]
async def _vote(args, author, channel):

    if len(args) < 2:
        return BAD_ARGS_MESSAGE

    try:
        target_game = await _fetch_game(args[0])
    except KeyError:
        return BAD_ID_MESSAGE

    #debug
    for player in target_game.players:
        print(str(player))

    if not target_game.started:
        return "This game has not started yet."
    
    if author not in target_game.player_roles:
        return "You are either dead or not in this game."

    if channel != target_game.home_channel:
        return "You may only vote in the channel the game was created in."

    if not target_game.can_vote:
        return "Tonight's hanging has already been decided."

    if not target_game.is_day:
        return "You may only vote during the day."

    role = target_game.player_roles[author]

    for player in target_game.players:
        if args[1] == str(player):
            target = player
            break
    else:
        return BAD_USER_MESSAGE

    if target not in target_game.player_roles:
        return "That person is already dead."

    #Voting for the same person twice unvotes
    if role.voted_for == target:
        role.voted_for = None
        target_game.vote_dict[target] -= 1
        return "Vote reset."

    else:
        #Remove previous vote
        if role.voted_for != None:
            target_game.vote_dict[role.voted_for] -= 1
        role.voted_for = target
        target_game.vote_dict[target] += 1

    if target_game.vote_dict[target] >= math.ceil(len(target_game.player_roles) / 2):
        target_game.kill(target)
        return "It is decided; {0} shall hang.".format(str(target))
    else:
        return "Vote cast."




#maf!voteinfo [game id]
async def _voteinfo(args, author, channel):

    if len(args) < 1:
        return BAD_ARGS_MESSAGE
    
    try:
        target_game = await _fetch_game(args[0])
    except KeyError:
        return BAD_ID_MESSAGE

    outlist = []
    for player in target_game.players:
        xstr = str(player) + " - "

        if player not in target_game.player_roles:
            xstr += "dead"
        else:
            xstr += str(target_game.vote_dict[player])
        outlist.append(xstr)

    return "\n".join(outlist)
        
#maf!power [game id] [args depend on power]
async def _power(args, author, channel):

    if type(channel) != discord.PrivateChannel:
        return "Powers cannot be used outside of DMs. You are encouraged to delete the command."

    if len(args) < 2:
        return BAD_ARGS_MESSAGE

    try:
        target_game = await _fetch_game(args[0])
    except KeyError:
        return BAD_ID_MESSAGE

    try:
        player = target_game.player_roles[author]
    except KeyError:
        return "You are either dead, or not in this game."

    player.target_power(args[1:])

#maf!time [game id]
async def _time(args, author, channel):

    if len(args) < 1:
        return BAD_ARGS_MESSAGE
    
    if not started:
        return "This game has not yet started."
    try:
        target_game = await _fetch_game(args[0])
    except KeyError:
        return BAD_ID_MESSAGE

    current_phase = "day" if target_game.is_day else "night"
    next_phase = "night" if target_game.is_day else "day"
    time = target_game.remaining_phase_time

    return ("It is currently {0}.\n"
            "{1} minute(s) until {2}."
           ).format(current_phase, time, next_phase)

#maf!maflist [game id]
async def _maflist(args, author, channel):
    raise NotImplementedError
    
commands = (
{
    "create"   : _create,
    "delete"   : _delete,
    "join"     : _join,
    "leave"    : _leave,
    "kick"     : _kick,
    "ban"      : _ban,
    "unban"    : _unban,
    "start"    : _start,
    "vote"     : _vote,
    "voteinfo" : _voteinfo,
    "power"    : _power,
    "time"     : _time,
    "maflist"  : _maflist
})

async def handle_command(command, author, channel):

    split_message = await _split_tokens(command)
    command_name = split_message[0]
    args = split_message[1:]

    try:
        command_func = commands[command_name]
    except KeyError:
        return None
    
    return await command_func(args, author, channel)
