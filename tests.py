import cli
import asyncio
import main
from sys import argv


class MockServer():
    def __init__(self, members):
        self.members = members

class MockChannel():
    def __init__(self, server):
        self.server = server

class MockUser():
    def __init__(self, username, discriminator):
        self.username = username
        self.discriminator = discriminator

    def __str__(self):
        return "{0}#{1}".format(username, discriminator)
#contains test functions for getattr()

class TestDummy():
    async def basic_creation_test(args):
        print("Starting quick test!")

        game_args = ["town", 1]
        player = MockUser("test", 1234)
        server = MockServer([player])
        channel = MockChannel(server)

        game_id = await cli._create(game_args, player, channel, True)
        print("Game has been created with 1 townie")

        await cli._start(game_id, player, channel)

        print(game_id)

async def run_test():
    try:
        test = getattr(TestDummy, argv[1])
    except AttributeError:
        print("No such test.")
    else:
        await test(argv)

loop = asyncio.get_event_loop()
loop.run_until_complete(run_test())

if len(argv) > 2 and argv[2] == "continue":
    client = main.setup_capone(loop)
    main.start_capone(client)
