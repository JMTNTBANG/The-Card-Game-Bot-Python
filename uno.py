import discord

"""
Colors:
0: Red
1: Orange
2: Green
3: Blue
4: Wild

Kinds:
0: Normal
1: Skip
2: Reverse
3: Draw
"""


# Classes
class UNO:
    class Card:
        def __init__(self, color: int, number: int, kind: int = 0):
            self.color = color
            self.number = number
            self.kind = kind

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
        self.deck = ""
        self.gen_deck()


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
