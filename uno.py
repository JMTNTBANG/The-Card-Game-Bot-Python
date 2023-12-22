import discord
import parse
import random

import main


colors = {
    0: "Red",
    1: "Yellow",
    2: "Green",
    3: "Blue",
    4: "Wild"
}

kinds = {
    0: "Normal",
    1: "Skip",
    2: "Reverse",
    3: "Draw"
}


# Classes
class UNO:
    class Card:
        def __init__(self, color: int, number: int, kind: int = 0):
            self.color = color
            self.number = number
            self.kind = kind

    class Player:
        def __init__(self, member: discord.Member, thread: discord.Thread, deck: list):
            self.user = member
            self.thread = thread
            hand = []
            for i in range(7):
                drawn_card = random.choice(deck)
                hand.append(drawn_card)
                deck.remove(drawn_card)
            self.hand = hand

    def gen_deck(self):
        deck = []
        for color in range(5):                              # Makes Cards for each color
            for kind in range(4):                           # Makes Cards for each kind
                if color < 4 and kind == 0:                     # All Regular and non-Wild
                    for number in range(10):                    # Cards 0-9
                        deck.append(self.Card(color, number))       # Adds one of each numbered card
                        if number > 0:                              # Adds an extra card for cards > 0
                            deck.append(self.Card(color, number))
                elif color < 4 and kind > 0:                    # All Non-Regular and non-Wild
                    deck.append(self.Card(color, -1, kind))         # Adds 2 of each
                    deck.append(self.Card(color, -1, kind))
                elif color == 4 and kind == 0 or kind == 3:     # All Wild and Regular/Draws
                    deck.append(self.Card(color, -1, kind))         # Adds 4 of each
                    deck.append(self.Card(color, -1, kind))
                    deck.append(self.Card(color, -1, kind))
                    deck.append(self.Card(color, -1, kind))
        self.deck = deck

    def __init__(self):
        self.deck = []
        self.guild: discord.Guild
        self.channel: discord.TextChannel
        self.members = []
        self.current_player: UNO.Player
        self.gen_deck()
        first_card = random.choice(self.deck)
        self.deck.remove(first_card)
        self.current_card: UNO.Card = first_card


def print_card(card: UNO.Card):
    return f"{kinds[card.kind]} {colors[card.color]} {card.number}"


def join_leave_callback(join: bool, message: discord.Message):
    async def callback(interaction: discord.Interaction):
        if join:
            embed = message.embeds[0]
            in_game = False
            for field in embed.fields:
                if field.value == interaction.user.mention:
                    in_game = True
                    await interaction.response.send_message("Already in Game!", ephemeral=True)
            if not in_game:
                embed.add_field(name="", value=interaction.user.mention, inline=False)
                await message.edit(embed=embed)
                await interaction.response.send_message("Successfully Joined Game!", ephemeral=True)
        else:
            embed = message.embeds[0]
            i = 0
            removed_from_game = False
            for field in embed.fields:
                if field.value == interaction.user.mention:
                    if embed.fields[1].value != interaction.user.mention:
                        embed.remove_field(i)
                        await message.edit(embed=embed)
                        await interaction.response.send_message("Successfully Left Game!", ephemeral=True)
                        removed_from_game = True
                    else:
                        await interaction.response.send_message("You started this game, you cannot leave it", ephemeral=True)
                        removed_from_game = True
                    break
                i += 1
            if not removed_from_game:
                await interaction.response.send_message("You're Not in This Game!", ephemeral=True)

    return callback


async def show_hands(game: UNO):
    for player in game.members:
        message = ""
        for card in player.hand:
            message += print_card(card) + "\n"
        await player.thread.send(message)


async def next_turn(game: UNO):
    await show_hands(game)
async def start_game(owner: discord.Member, guild: discord.Guild, lobby: discord.Message):
    for category in guild.categories:
        if category.name == "UNO":
            game = UNO()
            game.guild = guild
            game.channel = await category.create_text_channel(f"{owner.display_name}'s Game")
            for user in lobby.embeds[0].fields:
                if user != lobby.embeds[0].fields[0]:
                    user = guild.get_member(int(parse.parse("<@{}>", user.value)[0]))
                    thread = await game.channel.create_thread(
                        name=user.display_name
                    )
                    await thread.send(user.mention)
                    player = UNO.Player(user, thread, game.deck.copy())
                    for card in player.hand:
                        game.deck.remove(card)
                    game.members.append(player)
            game.current_player = game.members[0]
            main.uno_games[game.channel.created_at] = game
            await next_turn(game)
            break
