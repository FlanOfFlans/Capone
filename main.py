import discord
import cli

client = discord.Client()
prefix = "maf!"

@client.event
async def on_message(message):

  if not message.content.startswith(prefix):
    return

  command_string = message.content[len(prefix):len(message.content)]

  output = await cli.handle_command(command_string, message.author, message.channel)

  if output != None:
    await client.send_message(message.channel, output)

#client.run(token)
