import discord
import cli

client = discord.Client()
prefix = "maf!"

@client.event
async def on_message(message):
  if not message.content.starts_with(prefix):
    return

    command_string = message.content[0:len(prefix)]

    cli.handle_command(command_string)

async def test():
  print("test")

#client.run(token)
