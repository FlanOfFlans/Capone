import discord
import asyncio
import cli
import game

client = discord.Client()
prefix = "maf!"

CULL_MESSAGE = ("To save my host's resources, this game has been culled after going on too long. "
                "If this game was still active, and you frequently encounter this problem, please contact the developer. "
                "Currently, games can last for 3 days after being created, or 3 weeks after being started.")

@client.event
async def on_ready():
  #Mostly for debugging
  print("Capone is ready!")

@client.event
async def on_message(message):

  #Ignore messages that are not aimed at Capone
  if not message.content.startswith(prefix):
    return

  #Chop off prefix
  command_string = message.content[len(prefix):len(message.content)]

  #Handle the effects of the command, and pass the results to Discord.
  output = await cli.handle_command(command_string, message.author, message.channel)

  if output != None:
    await client.send_message(message.channel, output)

#Runs once per minute.
async def tick_games():
  #Prevents this from running before the bot is operational.
  await client.wait_until_ready()

  while not client.is_closed:

    #Loop over all games
    for game_id, current_game in game.game_dict.items():
      current_game.tick()

      #If the game is beyond the current maximum age, kill it, and provide the cull message.
      if current_game.culled:
        await client.send_message(current_game.home_channel, CULL_MESSAGE)
        del game.game_dict[game_id]

      else:
        #Clumps all output to a given channel into one string. 
        output_dict = {}

        for message in current_game.output_buffer:
          #If a channel has no entry in the dictionary, make one.
          try: output_dict[message[1]].append(message[0])
          except KeyError: output_dict[message[1]] = [message[0]]

        #Output everything in output dict to the appropriate channel
        for item in xdict.items():
          message = "\n".join(item[1])
          message = ("Game {0}:\n```\n" + message + "\n```").format(game_id)
          await client.send_message(item[0], message)

        #Clear the buffer
        current_game.output_buffer = []
    #Run this again in 60 seconds
    await asyncio.sleep(60)

client.loop.create_task(tick_games())
#client.run(token)
