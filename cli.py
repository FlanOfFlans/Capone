import discord
import game

#Helper functions
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

    return tokens

async def _check_arguments(tokens, arg_types):
        if len(tokens) != len(arg_types):
            return False

        for i in range(0, len(tokens)):
            if type(tokens[i]) != arg_types[i]:
                return False

        return True



#Command functions
#todo: make this EAFP
#maf!create [roles] [phase time]
async def _create(args, author, channel):

    if type(channel) == discord.PrivateChannel:
        return "Games cannot be created in DMs. Please try again in a server."
    
    elif  await check_arguments(args, [str, int]):
            await new_game = create_game(args[0], args[1], author, channel)

            if new_game == -1:
                return "Invalid role in role list."
            if new_game == -2:
                return "Phases must be at least two minutes long."
            
            outstr = ("Owner: %s"
                     "Roles: %s"
                     "ID: %s") %
                     (new_game.owner.name, args[0].replace(',', ', '), new_game.id)
            return outstr

#maf!join [game id]
async def _join(args, author):

    try:
        
        target_game = game.game_dict[args[0]]

        if target_game.started:
            return "This game has already begun, and cannot be joined."

        elif author in target_game.banned:
            return "You have been banned from this game."

        elif author in target_game.players:
            return "You are already in this game."

        elif len(players) >= len(role_list):
            return "This game is already full."

        else:
            target_game.players.append(author)
            return "Game successfully joined."
    except:
        return "No game found with that ID."

#maf!leave [game id]
async def _leave(args, author):

    try:
        target_game = game.game_dict[args[0]]

        if author not in target_game.players:
            #kill() expects a valid target
            raise ValueError
        
        if target_game.started:
            target_game.kill(author)
        else:
            target_game.players.remove(author)

    except KeyError:
        return "No game found with that ID."

    except ValueError:
        return "You are not in this game."

#maf!kick [game id] [target]
async def _kick(args, author):

    try:
        target_game = game.game_dict[args[0]]

        for player in target_game.players:
            if args[1] == str(player):
                target = player
                break
        else:
            raise ValueError

        if author != target_game.owner
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

        for member in channel.server.members:
            if args[1] == str(member):
                target = member
                break
        else:
            raise ValueError

        if author != target_game.owner:
            return "You do not own this game."
        else:
            try:
                #kill() expects a valid target
                if target not in target_game.players:
                    raise ValueError
                
                if target_game.started:
                    kill(target)
                else:
                    target_game.players.remove(target)
            except ValueError: pass

            if target in target_game.banned:
                return "User is already banned."
            else:
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
        else:
            raise ValueError

        if author != target_game.owner:
            return "You do not own this game."

        else:
            try:
                target_game.banned.remove(target)
            except:
                return "That user is not banned."
            return "User has been unbanned."

    except KeyError:
        return "No game found with that ID."

    except ValueError:
        return "Target user not found. Note that only usernames, not nicknames, can be used, and the discriminator (#1234) is required. Additionally, they must be present in this server."

async def handle_command(command, author, channel):

  split_message = await split_tokens(command)
  command_name = split_message[0]
  args = split_message[1:len(split_message)]


  if command_name == "create":
    return await _create(args, author, channel)
    
  if command_name == "join":
    return await _join(args, author)

  if command_name == "leave":
    return await _leave(args, author)


  if command_name == "kick":
    return await _kick(args, author)

  if command_name == "ban":
    return await _ban(args, author, channel)

  if command_name == "unban":
    return await _unban(args, author, channel)

  if command_name == "start":
    pass


  if command_name == "vote":
    pass

  if command_name == "time":
    pass

  if command_name == "maflist":
    pass

  if command_name == "power":
    pass
