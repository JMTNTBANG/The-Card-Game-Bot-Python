import discord
import parse
import random

import main


colors = [
    "red",
    "yellow",
    "green",
    "blue",
    "wild"
]

kinds = [
    "normal",
    "skip",
    "reverse",
    "draw"
]

uno_games = {}


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


def print_card(card: UNO.Card, emojis: dict):
    if card.number == -1:
        return emojis[f'{card.kind}{card.color}_1']
    else:
        return emojis[f'{card.kind}{card.color}{card.number}']
    # return f"{kinds[card.kind]} {colors[card.color]} {card.number}"


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


async def show_hands(game: UNO, emojis: dict, specific_player: UNO.Player = None):
    for player in game.members:
        if specific_player is None or player == specific_player:
            message = ""
            for card in player.hand:
                message += print_card(card, emojis) + " "
            await player.thread.send(message)


async def next_turn(game: UNO, emojis: dict):
    await show_hands(game, emojis)
    await game.channel.send(f"## Current Card: \n"
                            f"# {print_card(game.current_card, emojis)}\n"
                            f"# It is now {game.current_player.user.mention}s Turn!")
    uno_games[game.channel.created_at] = game


async def play_card(game: UNO, message: discord.Message, emojis: dict):
    for player in game.members:
        if player.user == message.author:
            if message.content.lower() == "draw":
                drawn_card = random.choice(game.deck)
                player.hand.append(drawn_card)
                game.deck.remove(drawn_card)
                await show_hands(game, emojis, player)
                uno_games[game.channel.created_at] = game
            else:
                try:
                    color, number_kind = parse.parse("{} {}", message.content)
                except TypeError:
                    color = parse.parse("{}", message.content)
                    number_kind = "-1"
                if color.lower() in colors:
                    for card in player.hand:
                        if colors[card.color] == color.lower() \
                                and kinds[card.kind] == number_kind.lower() \
                                or number_kind.isnumeric() and card.number == int(number_kind):
                            if card.color == game.current_card.color \
                                    or card.kind == game.current_card.kind and kinds[card.kind] != "normal" \
                                    or card.number == game.current_card.number and card.number >= 0:
                                game.current_card = card
                                player.hand.remove(card)
                                await next_turn(game, emojis)
                                break
            break


async def start_game(owner: discord.Member, guild: discord.Guild, lobby: discord.Message, emojis: dict):
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
            uno_games[game.channel.created_at.timestamp()] = game
            await next_turn(game, emojis)
            break
