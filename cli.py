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
async def _create(args, author, channel):

    if type(channel) == discord.PrivateChannel:
        return "Games cannot be created in DMs. Please try again in a server."
    
    elif  await check_arguments(args, [str, int]):
            await new_game = create_game(args[0], args[1], author, channel)

            if new_game == None:
                return "Invalid role in role list."
            
            outstr = ("Owner: %s"
                     "Roles: %s"
                     "ID: %s") %
                     (new_game.owner.name, args[0].replace(',', ', '), new_game.id)
            return outstr

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


async def _leave(args, author):

    try:
        target_game = game.game_dict[args[0]]
        
        if target_game.started:
            target_game.kill(author)
        else:
            target_game.players.remove(author)

    except KeyError:
        return "No game found with that ID."

    except ValueError:
            return "You are not in this game."



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
    pass

  if command_name == "ban":
    pass

  if command_name == "unban":
    pass

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
