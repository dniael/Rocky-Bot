# This example requires the 'message_content' privileged intents

import asyncio
import datetime
import urllib.request
from PIL import Image
from nextcord.ext import commands
import os
import random
import nextcord
from transforms import RGBTransform
from cogs.help_cog import HelpCommand
import json
import requests


# class DiscordBot(commands.Bot, HelpCommand):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)


client = commands.Bot(command_prefix='r!', intents=nextcord.Intents.all())
error_codes = {
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Access Forbidden',
    404: 'Content Not Found',
    408: 'Request Timed out',
    429: 'Too many requests made. Chill out!',
    500: 'Internal server error, please try again later!',
    502: 'Bad Gateway. Please try again later!',
    503: 'Sorry, but this service is currently unavailable. Please try again later.',
    504: 'Gateway Timeout. Please try again later'
}


def save_image_from_url(url) -> None:
    req = urllib.request.build_opener()
    req.addheaders = [('User-Agent', 'RockyBot Testing')]
    urllib.request.install_opener(req)
    urllib.request.urlretrieve(url, 'custom_morbin.png')


@client.event
async def on_ready():
    setattr(client, 'error_codes', error_codes)
    setattr(client, 'help_menu', HelpCommand())
    # setattr(client, 'db', db)
    print('rockybot is ready for testing!')


@client.command()
async def hello(ctx: commands.Context):
    await ctx.send(f'hello, {ctx.author}')


@client.command()
async def colour(ctx):
    r, g, b = [random.randint(0, 255) for _ in range(3)]
    pfp = Image.open('pancakerocky.png').convert('RGB')
    colour_pfp = RGBTransform().mix_with((r, g, b), factor=.45).applied_to(pfp)
    colour_pfp.save('colouredrocky.png')
    file = nextcord.File('colouredrocky.png')
    embed = nextcord.Embed(
        title=f'{r}, {g}, {b}',
        colour=nextcord.Colour.from_rgb(r, g, b)
    )
    embed.set_image(url='attachment://colouredrocky.png')
    await ctx.send(embed=embed, file=file)
    os.remove('colouredrocky.png')


@client.command()
async def sarcastic(ctx, *text):
    await ctx.send(funny_text(' '.join(text), '/s'))


@client.command(aliases=['av'])
async def avatar(ctx: commands.Context, user: nextcord.Member = None):
    user = user or ctx.author
    embed = nextcord.Embed(title=user.name).set_image(url=user.avatar.url)
    await ctx.reply(embed=embed)


@client.user_command(name='Avatar', guild_ids=[927381192129519646, 911811204761153637])
async def avatar(ctx: nextcord.Interaction, user: nextcord.Member):
    embed = nextcord.Embed(title=f'{user.name}', colour=user.colour)
    embed.set_author(name=ctx.user, icon_url=ctx.user.avatar.url)
    embed.timestamp = datetime.datetime.now()
    embed.set_image(url=user.avatar.url)
    response: nextcord.InteractionResponse = ctx.response()
    await response.send_message(embed=embed)


@client.command()
async def morbin(ctx: commands.Context, url):
    save_image_from_url(url)
    morb = Image.open('morbin.png').copy()
    img_to_paste = Image.open('custom_morbin.png').resize(morb.size)

    mask = Image\
        .open('mask.png')\
        .convert('L')\
        .resize(morb.size)
    morb.paste(img_to_paste, mask=mask)
    morb.save('pasted_morbin.png')

    file = nextcord.File('pasted_morbin.png')
    await ctx.reply(file=file)
    os.remove('pasted_morbin.png')
    os.remove('custom_morbin.png')


@client.message_command(name='uwuify', guild_ids=[927381192129519646, 911811204761153637])
async def uwuify_message(ctx: nextcord.Interaction, msg: nextcord.Message):
    await ctx.response.send_message('uwuification successful!', ephemeral=True)
    await asyncio.sleep(0.5)
    await msg.reply(funny_text(msg.content, 'uwu'))


@client.message_command(name='sarcasticify', guild_ids=[927381192129519646, 911811204761153637])
async def sarcastic_message(ctx: nextcord.Interaction, msg: nextcord.Message):
    await ctx.response.send_message('message successfully sarcasticified!', ephemeral=True)
    await asyncio.sleep(0.5)
    await msg.reply(funny_text(msg.content, '/s'))


@client.command()
async def uwu(ctx: commands.Context, *text):
    await ctx.send(funny_text(' '.join(text), 'uwu'))


def funny_text(text, mode):
    output_text = ''
    if mode == 'uwu':
        for i, current_char in enumerate(text):
            if current_char == '"' or current_char == "'":
                continue
            previous_char = '&# 092;&# 048;'
            if i > 0:
                previous_char = text[i - 1]
            if current_char == 'L' or current_char == 'R':
                output_text += 'W'
            elif current_char == 'l' or current_char == 'r':
                output_text += 'w'
            elif current_char == 'O' or current_char == 'o':
                if previous_char == 'N' or previous_char == 'n' or previous_char == 'M' or previous_char == 'm':
                    output_text += "yo"
                else:
                    output_text += current_char
            else:
                output_text += current_char

        return output_text
    elif mode == '/s':
        for i, letter in enumerate(text):
            if i % 2 == 0:
                letter = letter.upper() if letter.islower() else letter.lower()

            output_text += letter

        return output_text


extensions = [f'cogs.{filename[:-3]}' for filename in os.listdir('cogs') if filename.endswith('.py')]

if __name__ == '__main__':
    for extension in extensions:
        client.load_extension(extension)
        print(f'{extension[5:]} cog loaded \n')

client.run(os.environ['DISCORD_TOKEN'])

