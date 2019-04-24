import discord
import asyncio
import cli
import game
from collections import defaultdict
from traceback import format_exc

prefix = "maf!"

CULL_MESSAGE = ("To save my host's resources, this game has been culled after going on too long. "
                "If this game was still active, and you frequently encounter this problem, please contact the developer. "
                "Currently, games can last for 3 days after being created, or 3 weeks after being started.")

def setup_capone(loop = None):
    client = discord.Client()

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
      command = message.content[len(prefix):]
      author = message.author
      channel = message.channel

      #Handle the effects of the command, and pass the results to Discord.
      try:
        output = await cli.handle_command(command, author, channel)
      except NotImplementedError:
        output = "Unfortunately, that command is not available in the current version of Capone."
      except:
        exc = format_exc()
        print(exc)
        output = ("An error has occured. You are encouraged to open an issue at <https://github.com/FlanOfFlans/Capone/issues>\n"
                  "Please include the roles in the game, and what happened to cause this error, as well as the following error message.\n"
                  "You may continue the game, but further errors and strange behavior may occur. Deleting this game and starting a new one is encouraged.\n\n"
                  "```\n{0}\n```"
                  ).format(exc)

      if output != None:
        await client.send_message(message.channel, output)

    return client

async def tick_games():

    #Loop over all games
    for game_id, current_game in game.game_dict.items():
      current_game.tick()

      # If the game is beyond the current maximum age, kill it, and provide the cull message.
      # This can use send_message() because games don't age in testing
      if current_game.culled:
        message = "Game {0}: {1}".format(game_id, CULL_MESSAGE)
        await client.send_message(current_game.home_channel, message)
        del game.game_dict[game_id]

      
      #Clumps all output to a given channel into one string.
      #If no key is found, it's an empty list
      output_dict = defaultdict(list)

      for message in current_game.output_buffer:
        output_dict[message[1]].append(message[0])

      for key, value in output_dict.items():
          message = "\n".join(value)
          output_dict[key] = ("Game {0}:\n```\n" + message + "\n```").format(game_id)

      #Clear the buffer
      current_game.output_buffer = []

    return output_dict

#Runs once per minute.
async def tick_loop(client):

    #Prevents this from running before the bot is operational.
    await client.wait_until_ready()
    await tick_games()

    #Output everything in output dict to the appropriate channel
    for item in output_dict.items():
      await client.send_message(item[0], message)

    await asyncio.sleep(60)

def start_capone(client):
    client.loop.create_task(tick_games(client))

    token = open("capone.ini").readline()
    token = token.replace("\n", "")

    client.run(token)

if __name__ == "__main__":
    client = setup_capone()
    start_capone(client)
