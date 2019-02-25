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

  if not message.content.startswith(prefix):
    return

  command_string = message.content[len(prefix):len(message.content)]

  output = await cli.handle_command(command_string, message.author, message.channel)

  if output != None:
    await client.send_message(message.channel, output)

async def tick_games():
  await client.wait_until_ready()

  for game_id, game in game.game_dict.iteritems():
    game.tick()

    if game.culled:
      client.send_message(game.home_channel, game.id + ": " + CULL_MESSAGE)
      del game.game_dict[game_id]

    else:
      xdict = {}

      for message in game.output_buffer:
        try:
          xdict[message[1]].append(message[0])
        except KeyError:
          xdict[message[1]] = [message[0]]

      for item in xdict.items():
        message = "\n".join(item[1])
        client.send_message(item[0], message)

  #loops every minute
  await asyncio.sleep(60)

client.loop.create_task(tick_games())
#client.run(token)
