import discord
import cli

client = discord.Client()
prefix = "maf!"

@client.event
async def on_message(message):

  if not message.content.starts_with(prefix):
    return

  command_string = message.content[0:len(prefix)]

  output = cli.handle_command(command_string)

  if output != None:
    client.send_message(message.channel, output)

#client.run(token)
