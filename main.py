import discord
import asyncio
import cli
import game
import collections
import traceback
import sys


prefix = "maf!"
debug_mode = False

CULL_MESSAGE = ("To save my host's resources, this game has been culled "
                "after going on too long. If this game was still active, "
                "and you frequently encounter this problem, please contact "
                "the developer. Currently, games can last for 3 days after"
                "being created, or 3 weeks after being started.")


def setup_capone(loop = None):
    client = discord.Client()

    @client.event
    async def on_ready():
      #Mostly for debugging
      print("Capone is ready!")

    @client.event
    async def on_message(message):

      # Ignore messages that are not aimed at Capone
      if not message.content.startswith(prefix):
        return

      # Chop off prefix
      command = message.content[len(prefix):]
      author = message.author
      channel = message.channel

      # Handle the effects of the command, and pass the results to Discord.
      try:
        output = await cli.handle_command(command, author, channel)
      except NotImplementedError:
        output = "That command is not available in this version of Capone."
      except:
        exc = traceback.format_exc()
        print(exc)
        output = ("An error has occured. You are encouraged to open an "
                  "issue at <https://github.com/FlanOfFlans/Capone/issues>\n"
                  "Please include the roles in the game, what happened to "
                  "cause this error, and the following error message.\n"
                  "You may continue the game, but further errors and "
                  "strange behavior may occur. Deleting this game and "
                  "starting a new one is encouraged.\n\n"
                  "```\n{0}\n```"
                  ).format(exc)

      if output != None:
        await message.channel.send(output)

    return client


async def tick_games(client, interval):

    # Loop over all games
    await client.wait_until_ready()
    while True:
        print("Ticking games...")

        delete_list = []
        for game_id, current_game in game.game_dict.items():
            current_game.tick()

            # If the game is beyond the current maximum age, 
            # kill it, and provide the cull message.
            # Normally, send_message() is not used in client methods,
            # to support tests. This can use send_message() because games don't 
            # age in testing
            if current_game.culled:
                message = "Game {0}: {1}".format(game_id, CULL_MESSAGE)
                await client.send_message(current_game.home_channel, message)
                delete_list.append(game_id)
          
            # Clumps all output to a given channel into one string.
            # If no key is found, it's an empty list
            output_dict = collections.defaultdict(list)

            for message in current_game.output_buffer:
                output_dict[message[1]].append(message[0])

            for key, value in output_dict.items():
                message = ("\n**Game {0}**:\n" + ("\n".join(value))) \
                    .format(game_id)
                
                output_dict[key] = message

            for target, message in output_dict.items():
                await target.send(message)

            if current_game.deleted:
                delete_list.append(game_id)
            
            # Clear the buffer
            current_game.output_buffer = []

        for game_id in delete_list:
            del game.game_dict[game_id]

        await asyncio.sleep(interval)

def start_capone(client):
    if len(sys.argv) == 1:
        interval = 60
    else:
        interval = int(sys.argv[1])

    client.loop.create_task(tick_games(client, interval))

    token = open("capone.ini").readline()
    token = token.replace("\n", "")

    client.run(token)

if __name__ == "__main__":
    client = setup_capone()
    start_capone(client)
