import cli
import main

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

def quick_test(args):
    game_args = ["townie", 2]
    player = MockUser("test", 1234)
    server = MockServer([player])
    channel = MockChannel(server)

    game_id = cli._create_game(game_args, player, channel, True)
    cli._start(game_id, player, channel)

    print("Game has been started.")
    if len(args) > 3 and args[3] == "continue":
        print(game_id)

