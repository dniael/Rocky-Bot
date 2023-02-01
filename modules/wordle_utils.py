import string
import nextcord
from nextcord import Interaction
from text_files import countries, words

PATH = 'C:/Users/g192t/OneDrive/Desktop/RockyBot/'
COUNTRIES = countries.countries
WORDS = words.words


def check_alpha(word):
    remaining = ''.join([i for i in word if i in string.ascii_letters])
    return len(remaining) == len(word) and len(word) == 5 and remaining.lower() in WORDS


def generate_squares(msg, wordle):
    length = len(msg)
    result = [''] * length
    remaining = wordle

    for letter in range(length):
        if msg[letter] == wordle[letter]:
            remaining = remaining.replace(msg[letter], '')
            result[letter] = Emojis.green
        else:
            result[letter] = Emojis.white

    for letter in range(length):
        if msg[letter] in remaining and msg[letter] != wordle[letter]:
            remaining = remaining.replace(msg[letter], '')
            result[letter] = Emojis.yellow

    return ''.join(result)


class QuitGame(nextcord.ui.View):

    def __init__(self, ctx, stopped: bool):
        super().__init__(timeout=None)
        self.value = None
        self.stopped = stopped
        self.author = ctx.author

    @nextcord.ui.button(label="Quit", style=nextcord.ButtonStyle.red)
    async def quit(self, button: nextcord.ui.Button, interaction: Interaction) -> None:
        if interaction.user == self.author:
            self.value = True
            self.stopped = True
            button.disabled = True
            self.stop()
            await interaction.message.edit(view=self)
            return await interaction.response.send_message(f'{interaction.user.mention} Quit the game!',
                                                           ephemeral=False)
        return


class Emojis(nextcord.Enum):
    green = ':green_square:'
    yellow = ':yellow_square:'
    white = ':white_large_square:'
    n = ':arrow_up:'
    nw = ':arrow_upper_left:'
    ne = ':arrow_upper_right:'
    s = ':arrow_down:'
    sw = ':arrow_lower_left:'
    se = ':arrow_lower_right:'
    w = ':arrow_left:'
    e = ':arrow_right:'
    tada = ':tada:'
