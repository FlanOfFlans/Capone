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

  while not client.is_closed:
    
    for game_id, current_game in game.game_dict.items():
      current_game.tick()

      if current_game.culled:
        client.send_message(current_game.home_channel, game.id + ": " + CULL_MESSAGE)
        del game.game_dict[game_id]

      else:
        xdict = {}

        for message in current_game.output_buffer:
          try:
            xdict[message[1]].append(message[0])
          except KeyError:
            xdict[message[1]] = [message[0]]

        for item in xdict.items():
          message = "\n".join(item[1])
          await client.send_message(item[0], message)

        current_game.output_buffer = []
        
    await asyncio.sleep(60)

client.loop.create_task(tick_games())
client.run("NTMwNDcxNjQ5MzEzODE2NTg2.D1baWQ.bVrHApU0oEqFTIEtxAiuF3ZeOLA")
