import nextcord
from nextcord import Interaction
from nextcord.ext import commands
import geopy.exc
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import math
import pycountry as pc
import secrets
from modules.wordle_utils import Emojis
from text_files import countries

loc = Nominatim(user_agent='test')
MAX_DISTANCE_ON_EARTH = 20_000
COUNTRIES = countries.countries
PY_COUNTRIES = [c.name for c in list(pc.countries)]


def get_random_country():
    country = secrets.choice(PY_COUNTRIES)
    return country


def check(msg: str) -> bool:
    if msg.lower() not in COUNTRIES:
        try:
            pc.countries.search_fuzzy(msg)
            return True
        except LookupError:
            return False

    return True


def search_fuzzy(place: str) -> str:
    search = pc.countries.search_fuzzy(place)[0]
    return search.name


def get_coords(place: str) -> tuple:
    try:
        return loc.geocode(place).latitude, loc.geocode(place).longitude
    except geopy.exc.GeocoderUnavailable:
        raise GeocoderUnavailable('The Geocoder is currently unavailable. Please try again in a few minutes.')


def get_distance(point1: tuple, point2: tuple) -> int:
    return round(geodesic(point1, point2).km)


def calculate_compass_bearing(point1: tuple, point2: tuple) -> str:

    start_lat = point1[0]
    end_lat = point2[0]
    start_long = point1[1]
    end_long = point2[1]

    radians = math.atan2((start_long - end_long), (start_lat - end_lat))

    compass_reading = radians * (180 / math.pi)

    coord_names = [Emojis.n, Emojis.ne, Emojis.e, Emojis.se, Emojis.s, Emojis.sw, Emojis.w, Emojis.nw, Emojis.n]
    # compass_bearing = (initial_bearing + 360) % 360
    coord_index = round(compass_reading / 45)
    if coord_index < 0:
        coord_index += 8

    return coord_names[coord_index]


def proximity_percentage(distance: int) -> int:
    proximity = max(MAX_DISTANCE_ON_EARTH - distance, 0)
    return math.floor(proximity / MAX_DISTANCE_ON_EARTH * 100)


def get_squares(prox: int) -> str:
    max_squares = 5
    chars = []
    green_squares = math.floor(prox / 20)
    yellow_squares = 1 if prox - green_squares * 20 >= 10 else 0
    # print(green_squares)
    # print(yellow_squares)
    for i in range(green_squares):
        chars.append(Emojis.green)

    for i in range(yellow_squares):
        chars.append(Emojis.yellow)

    for i in range(max_squares-(green_squares+yellow_squares)):
        chars.append(Emojis.white)

    # print(chars)
    return ''.join(chars)


class Buttons(nextcord.ui.View):

    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.value = None
        self.author = ctx.author
        self.stopped = False

    @nextcord.ui.button(label="Quit", style=nextcord.ButtonStyle.red)
    async def quit(self, button: nextcord.ui.Button, interaction: Interaction):
        if interaction.user == self.author:
            self.value = True
            self.stopped = True
            self.stop()
            button.disabled = True
            await interaction.message.edit(view=self)
            return await interaction.response.send_message(
                f'{interaction.user.mention} Quit the game!',
                ephemeral=False)

    @nextcord.ui.button(label='Help', style=nextcord.ButtonStyle.blurple)
    async def help_button(self, button: nextcord.ui.Button, inter: Interaction):
        if inter.user != self.author:
            return

        self.value = True
        help_embed = nextcord.Embed(
            title='Bootleg Worldle (EXPERIMENTAL PHASE; THINGS MAY GO VERY WRONG)',
            description='**EXAMPLE** (Your guess: Finland)\n'
                        f'`Finland` | **3206km** {Emojis.green * 4 + Emojis.white}{Emojis.se}  |  **83%**\n'
                        f'{Emojis.se} - The country is **SOUTHEAST** of your guess\n'
                        '**3206km** - The country is **3206km** away from your guess\n'
                        '**83%** - The proximity of your guess and the country is **83%**'
        )
        if self.stopped:
            button.disabled = True
            await inter.message.edit(view=self)
            return
        return await inter.response.send_message(embed=help_embed, ephemeral=True)


class GeocoderUnavailable(commands.CommandError):
    def __init__(self, message):
        super().__init__()
        self.message = message
