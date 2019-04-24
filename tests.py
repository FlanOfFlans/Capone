import cli
import asyncio
import main
import re
from sys import argv


class MockServer():
    def __init__(self, members):
        self.members = members
        print("Server created.")

class MockChannel():
    def __init__(self, server, is_private = False):
        self.server = server
        self.is_private = is_private
        print("Channel created.")

class MockUser():
    def __init__(self, name, discriminator):
        self.name = name
        self.discriminator = discriminator
        print("User created.")

    def __str__(self):
        return "{0}#{1}".format(self.name, self.discriminator)


# Contains test functions for getattr()

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


    async def manual(args):

        assignment_commands = {
                "user"    : MockUser,
                "server"  : MockServer,
                "channel" : MockChannel,
        }
        
        names = {}

        # Matches things of form "name = ..."
        # Puts assigned name in capture group 1
        # Puts command + args in capture group 2
        # Does not validate command or args
        assignment_regex = re.compile("^([\S]+)\\s*=\\s*(.*)$")

        # Matches things of form "user, channel::..."
        # Puts user in capture group 1
        # Puts channel in capture group 2
        # Puts command + args in capture group 3
        # Does not validate command or args
        command_regex = re.compile("^(\\S+)\\s*,\\s*(\\S+)\\s*::\\s*(.*)$")
            

        print("Type q to quit.")

        command = input(">")
        while command != "q":

            re_assignment = re.match(assignment_regex, command)
            re_command = re.match(command_regex, command)

            if command == "tick":
                print("Ticking...")
                output = await main.tick_games()
                for key, value in output.items():
                    print(value)

            elif command == "names":
                for key, value in names.items():
                    # A phantom dictionary entry, __builtins__,
                    # keeps sneaking into names. I don't know 
                    # where it's from, but we can just not print it
                    if key != "__builtins__":
                        print("{0} - {1}".format(key, type(value).__name__))

            elif re_assignment != None:
                new_name = re_assignment.group(1)
                split_command = await cli._split_tokens(re_assignment.group(2))
                command_name = split_command[0]
                command_args = []
                for n in split_command[1:]:
                    n = str(n)
                    try:
                        command_args.append(eval(n, names))
                    except:
                        command_args.append(eval("'"+n+"'", names))

                try:
                    result = assignment_commands[command_name](*command_args)
                    names[new_name] = result
                except KeyError:
                    print("Bad command name.")
                except TypeError:
                    print("Bad arguments.")

            elif re_command != None:
                author = eval(re_command.group(1), names)
                channel = eval(re_command.group(2), names)
                split_command = await cli._split_tokens(re_command.group(3))
                command_name = split_command[0]
                command_args = []

                for n in split_command[1:]:
                    n = str(n)
                    try:
                        command_args.append(eval(n, names))
                    except:
                        command_args.append(eval("'"+n+"'", names))

                try:
                    result = await cli.commands[command_name](command_args, author, channel)
                    print(result)
                except KeyError:
                    print("Bad command name.")
                except TypeError:
                    print("Bad arguments.")



            else:
                print("Malformed command.")

            split_command = await cli._split_tokens(command)
            func_name = split_command[0]
            args = split_command[1:]
            run = True
            
            command = input(">")

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
