import uno
try:
    import discord
except ImportError:
    print("Please install all needed dependencies before running!")
    exit(1)

import json


class Config:
    def reload(self):
        with open("./config.json", "r") as raw_config:
            raw_config = json.loads(raw_config.read())
            self.token = raw_config["bot-token"]

    def __init__(self):
        self.token = ""
        self.reload()


try:
    config = Config()
except FileNotFoundError:
    print("Please Create a config.json File with the code defined in README.md")
    exit(1)
except KeyError as key:
    print(f"Please add {key} entry to .json file as defined in README.md")
    exit(1)
except json.decoder.JSONDecodeError as error:
    print("There has been an unexpected error when reading your config.json file\n\n"
          f"Details: {error}")
    exit(1)
except Exception as error:
    print("Some Unknown Error has happened, please create an issue on GitHub with the following information:")
    raise error

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
del intents

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await client.change_presence(activity=discord.Game(name="IN DEV, DONT USE ANY COMMANDS"), status=discord.Status.dnd)
    # Initialize Modules
    uno.init()
    await tree.sync()
    print("Commands Synced")


if __name__ == "__main__":
    client.run(config.token)
