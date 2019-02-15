async def split_tokens(xstr):
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

    return tokens

async def handle_command(command, target_game):

  split_message = split_tokens(command)
  command_name = split_message[0]
  args = split_message[1:len(split_message)]


  if command_name == "create":
    if(len(args) == 3):
      if (
        type(args[0]) == str and
        type(args[1]) == int and
        type(args[2]) == int):
         return -1

    elif len(args) == 4:
      if (
        type(args[0]) == str and
        type(args[1] == int) and
        type(args[2] == int)and 
        type(args[3] == str)):
          return -1
    
    else:
      #game = make_new_game(args)
      #return game
      pass
    
  if command_name == "join":
    pass

  if command_name == "leave":
    pass


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
