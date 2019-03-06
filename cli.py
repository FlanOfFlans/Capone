import discord
import game

#Helper functions
#This breaks strings apart, reading things "in quotes" as one token.
async def _split_tokens(xstr):
    prev_index = 0
    string_mode = False
    tokens = []

    for index in range(0, len(xstr)):

        to_append = ""
        
        if (not string_mode) and xstr[index] == " " :
            if index == prev_index: continue
            to_append = xstr[prev_index:index]
            prev_index = index + 1
            
        elif (not string_mode) and xstr[index] == "\"":
            string_mode = True
            prev_index = index + 1

        elif string_mode and xstr[index] == "\"":
            string_mode = False
            to_append = xstr[prev_index:index]
            prev_index = index + 2

        if to_append != "":
            tokens.append(to_append)

            
    if xstr[prev_index:len(xstr)] != "":
        tokens.append(xstr[prev_index:len(xstr)])

    #convert to ints where possible, to aid type checking
    converted_tokens = []
    for token in tokens:
        try:
            converted_tokens.append(int(token))
        except ValueError:
            converted_tokens.append(token)

    return converted_tokens

#todo: delete this once it's obsolete
async def _check_arguments(tokens, arg_types):
        if len(tokens) != len(arg_types):
            return False

        for i in range(0, len(tokens)):
            if type(tokens[i]) != arg_types[i]:
                return False

        return True
    
async def _fetch_game(game_id):
    return game.game_dict[args[0]]


#Command functions
#todo: make this EAFP
#maf!create [roles] [phase time]
async def _create(args, author, channel):

    if type(channel) == discord.PrivateChannel:
        return "Games cannot be created in DMs. Please try again in a server."

    elif await _check_arguments(args, [str, int]):
        new_game = await game.create_game(args[0], args[1], author, channel)

        if new_game == -1:
            return "Invalid role in role list."
        if new_game == -2:
            return "Phases must be at least two minutes long."
        
        outstr = ("Owner: {0}\n"
                 "Roles: {1}\n"
                 "ID: {2}\n").format(
                     new_game.owner.name,
                     args[0].replace(' ', ', '),
                     new_game.id)
        return outstr

#maf!join [game id]
async def _join(args, author, channel):
    
    try: target_game = _fetch_game(args[0])
    except KeyError: return "No game found with that ID."

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

    try: target_game = _fetch_game(args[0])
    except KeyError: return "No game found with that ID."

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

    try:
        target_game = game.game_dict[args[0]]



        for player in target_game.players:
            if args[1] == str(player):
                target = player
                break
        else:
            raise ValueError

        if channel != target_game.home_channel:
            target_game.buffer_message("{0} has been kicked by the owner.".format(str(player)))

        if author != target_game.owner:
            return "You do not own this game."
        else:
            if target_game.started:
                kill(target)
            else:
                target_game.players.remove(target)

            return "Player has been kicked."

    except KeyError:
        return "No game found with that ID."

    except ValueError:
        return "Target player not found. Note that only usernames, not nicknames, can be used, and the discriminator (#1234) is required."

#maf!ban [game id] [target]
async def _ban(args, author, channel):

    try:
        target_game = game.game_dict[args[0]]

        if channel != target_game.home_channel:
            target_game.buffer_message("{0} has been banned by the owner.".format(str(author)))

        for member in channel.server.members:
            if args[1] == str(member):
                target = member
                break
            
        #Note: else belongs to for, not if
        else:
            raise ValueError

        if author != target_game.owner:
            return "You do not own this game."

        if target in target_game.banned:
            return "User is already banned."

        if channel != target_game.home_channel:
            target_game.buffer_message("{0} has been banned by the owner.".format(str(target)))

        try:
            if target_game.started and target in target_game.players:
                kill(target)
            else:
                target_game.players.remove(target)

        except ValueError:
            #Banning players not in the game yet is expected
            pass

        target_game.banned.append(target)
        return "User has been banned."

    except KeyError:
        return "No game found with that ID."

    except ValueError:
        return "Target user not found. Note that only usernames, not nicknames, can be used, and the discriminator (#1234) is required. Additionally, they must be present in this server."
    
#maf!unban [game id] [target]
async def _unban(args, author, channel):

    try:
        target_game = game.game_dict[args[0]]

        for member in channel.server.members:
            if args[1] == str(member):
                target = member
                break
            
        #Note: else belongs to for, not if
        else:
            raise ValueError

        if author != target_game.owner:
            return "You do not own this game."


        try: target_game.banned.remove(target)
        except ValueError: return "That user is not banned."

        if channel != target_game.home_channel:
            target_game.buffer_message("{0} has been unbanned by the owner.".format(str(target)))

        return "User has been unbanned."

    except KeyError:
        return "No game found with that ID."

    except ValueError:
        return "Target user not found. Note that only usernames, not nicknames, can be used, and the discriminator (#1234) is required. Additionally, they must be present in this server."

#maf!start [game id]
async def _start(args, author):
    try:
        target_game = game.game_dict[args[0]]

        if author != target_game.owner:
            return "You do not own this game."

        target_game.start()
        return "Game queued to be started!"

    except KeyError:
        return "No game found with that ID."

#maf!vote [game id] [target]
async def _vote(args, author, channel):

    try:
        target_game = game.game_dict[args[0]]

        if not target_game.started:
            return "This game has not started yet."
        
        if author not in target_game.player_roles:
            return "You are either dead or not in this game."

        if channel != target_game.home_channel:
            return "You may only vote in the channel the game was created in."

        role = target_game.player_roles[author]

        for player in target_game.players:
            if args[1] == str(player):
                target = player
                break
        else:
            raise ValueError

        if target not in target_game.player_roles:
            return "That person is already dead."

        if role.voted_for == target:
            role.voted_for = None
            target_game.vote_dict[target] -= 1
            return "Vote reset."

        else:
            if role.voted_for != None:
                target_game.vote_dict[role.voted_for] -= 1
            role.voted_for = target
            target_game.vote_dict[target] += 1

        #if target_game.vote_dict[target] > len(target_game.player_roles):
            #kill the target

    except KeyError:
        return "No game found with that ID."

    except ValueError:
        return "Target user not found. Note that only usernames, not nicknames, can be used, and the discriminator (#1234) is required."

#maf!voteinfo [game id]
async def _voteinfo(args):
    target_game = game.game_dict[args[0]]

    out_list = []
    for player in target_game.players:
        xstr = str(player) + " - "

        if player not in target_game.player_roles:
            xstr += "dead"
        else:
            xstr += str(target_game.vote_dict[player])
        outlist.append(xstr)

    return "\n".join(out_list)
        
#maf!power [game id] [args depend on power]
async def _power(args, author, channel):

    if type(channel) != discord.PrivateChannel:
        return "Powers cannot be used outside of DMs. You are encouraged to delete the command."

    try:
        target_game = game.game_dict[args[0]]
    except KeyError:
        return "No game found with that ID."

    try:
        player = target_game.player_roles[author]
    except KeyError:
        return "You are either dead, or not in this game."

    player.target_power(args[1:len(args)])

    
    
async def handle_command(command, author, channel):

  split_message = await _split_tokens(command)
  command_name = split_message[0]
  args = split_message[1:len(split_message)]
    
  if command_name == "create":
    return await _create(args, author, channel)
    
  if command_name == "join":
    return await _join(args, author, channel)

  if command_name == "leave":
    return await _leave(args, author, channel)


  if command_name == "kick":
    return await _kick(args, author, channel)

  if command_name == "ban":
    return await _ban(args, author, channel)

  if command_name == "unban":
    return await _unban(args, author, channel)

  if command_name == "start":
    return await _start(args, author)


  if command_name == "vote":
    return await _vote(args, author, channel)

  if command_name == "time":
    pass

  if command_name == "maflist":
    pass

  if command_name == "power":
    return await _power(args, author, channel)
