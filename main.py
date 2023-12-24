import json
import uno
try:
    import discord
except ImportError:
    print("Please install all needed dependencies before running!")
    exit(1)


class Config:
    class Debug:
        def __init__(self, debug: bool, token: str):
            self.enabled = debug
            self.token = token

    def reload(self):
        with open("./config.json", "r") as raw_config:
            raw_config = json.loads(raw_config.read())
            self.token = raw_config["bot-token"]
            self.debug = self.Debug(raw_config["debug"],
                                    raw_config["debug-token"])

    def __init__(self):
        self.token = ""
        self.debug = None
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
emojis = {}
del intents


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await client.change_presence(activity=discord.Game(name="IN DEV, DONT USE ANY COMMANDS"), status=discord.Status.dnd)
    await tree.sync()
    print("Commands Synced")
    for guild in client.guilds:
        uno_category = None
        category_exists = False
        for category in guild.categories:
            if category.name == "UNO":
                category_exists = True
                uno_category = category
        if not category_exists:
            uno_category = await guild.create_category_channel("UNO")
        archive_category = None
        category_exists = False
        for category in guild.categories:
            if category.name == "UNO-ARCHIVE":
                category_exists = True
                archive_category = category
        if not category_exists:
            archive_category = await guild.create_category_channel("UNO-ARCHIVE")
        for channel in uno_category.channels:
            await channel.edit(category=archive_category, reason="Archival", name=f"uno-game-{channel.created_at.timestamp()}")
        if guild.name == "Card Game Bot Server":
            for emoji in guild.emojis:
                if emoji.animated:
                    emojis[emoji.name] = f"<a:{emoji.name}:{emoji.id}>"
                else:
                    emojis[emoji.name] = f"<:{emoji.name}:{emoji.id}>"
            print("emojis loaded")
    pass

"""
UNO MODULE
"""


uno_commands = discord.app_commands.Group(
    name="uno",
    description="UNO Game Commands"
)
tree.add_command(uno_commands)


@uno_commands.command(name="start", description="Start an UNO Game")
async def self(interaction: discord.Interaction):
    await interaction.response.send_message("Created Game, React with ✅ to start the game", ephemeral=True)
    embed = discord.Embed(
        title=f"{interaction.user} Wants to start an UNO Game",
        description="Click Below to join/leave"
    )
    embed.add_field(name="Player List", value="")
    embed.add_field(name="", value=interaction.user.mention, inline=False)
    view = discord.ui.View(timeout=None)
    join_button = discord.ui.Button(label="Join Game", style=discord.ButtonStyle.green)
    leave_button = discord.ui.Button(label="Leave Game", style=discord.ButtonStyle.red)
    view.add_item(join_button)
    view.add_item(leave_button)
    message = await interaction.channel.send(content="UNO Game", embed=embed, view=view)
    join_button.callback = uno.join_leave_callback(True, message)
    leave_button.callback = uno.join_leave_callback(False, message)


@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.content == "UNO Game" \
            and reaction.message.author == client.user \
            and user.mention == reaction.message.embeds[0].fields[1].value \
            and reaction.emoji == "✅":
        await reaction.message.reply("Starting Game...")
        await uno.start_game(user, reaction.message.guild, reaction.message, emojis)

@client.event
async def on_message(message: discord.Message):
    if not message.author.bot:
        for game in uno.uno_games:
            game = uno.uno_games[game]
            if isinstance(message.channel, discord.Thread):
                if game.channel == message.channel.parent:
                    await uno.play_card(game, message, emojis)
                    break
            else:
                if game.channel == message.channel:
                    await uno.main_channel_command(game, message, emojis)
                    break


if __name__ == "__main__":
    token = config.token
    if config.debug.enabled:
        token = config.debug.token
    client.run(token)
