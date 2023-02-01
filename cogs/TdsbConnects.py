import tdsbconnects
import datetime
# import asyncio
import nextcord
from nextcord.ext import commands
import pymongo
import aiohttp
import base64
import os
from cogs.help_cog import HelpCommand

MONGO_URL = os.environ['mongo']
cluster = pymongo.MongoClient(MONGO_URL)
db = cluster['discord']
collection = db['tdsb']


class TdsbConnects(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.description = 'TDSB commands!'

    @commands.group(help='TDSB profile and timetable')
    async def tdsb(self, ctx):
        if ctx.invoked_subcommand is None:
            group = HelpCommand()
            await group.send_group_help_poo(ctx, ctx.command)

    @tdsb.command(help='Registers your TDSB account w/ your Student Number and Password (encoded)')
    async def register(self, ctx):
        await ctx.author.send('Please enter your TDSB Student Number: ')
        username = await self.client.wait_for('message', check=lambda message:
                                              message.author.id == ctx.author.id and message.guild is None, timeout=20)
        username = username.content
        await ctx.author.send('Please enter your TDSB Student Password: ')
        password = await self.client.wait_for('message', check=lambda message:
                                              message.author.id == ctx.author.id and message.guild is None, timeout=20)
        password = password.content
        async with tdsbconnects.TDSBConnects() as session:
            try:
                await session.login(username=username, password=password)
            except aiohttp.ClientResponseError:
                await ctx.author.send('Invalid Username/Password, Please try again')
            else:
                check = collection.find_one({'_id': ctx.author.id})
                if check is None:
                    password = b64_encoder(password)
                    collection.insert_one({'_id': ctx.author.id, 'username': username, 'password': password})
                    await ctx.author.send('TDSB Account successfully registered!')
                else:
                    password = b64_encoder(password)
                    collection.update_many(
                        {'_id': ctx.author.id}, {'$set': {'username': username, 'password': password}}
                    )
                    await ctx.author.send('TDSB Account successfully updated!')

    @tdsb.command(help='Unregisters your TDSB account from the database')
    async def unregister(self, ctx):
        check = collection.find_one({'_id': ctx.author.id})
        if check is None:
            await ctx.send(f'{ctx.author.mention}, you do not have a pre-existing TDSB account registered!')
        else:
            collection.delete_one({'_id': ctx.author.id})
            await ctx.send(f'{ctx.author.mention}, TDSB account successfully unregistered!')

    @tdsb.command(aliases=['prof', 'pf'], help='Shows your TDSB role, name, school and school year')
    async def profile(self, ctx):
        user = collection.find_one({'_id': ctx.author.id})
        if user:
            username = user['username']
            pwd = b64_decoder(user['password'])
            user = await self.client.fetch_user(ctx.author.id)
            avatar = user.avatar.url
            async with tdsbconnects.TDSBConnects() as session:
                await session.login(username=username, password=pwd)
                info = await session.get_user_info()
                profile_embed = nextcord.Embed(title=f'{ctx.author}\'s TDSB profile', description='',
                                               colour=nextcord.Colour.random())
                profile_embed.set_thumbnail(url=avatar)
                profile_embed.add_field(name=f'{info.name}', value=f"Role: `{str(info.roles[0]).replace('Role.', '')}`",
                                        inline=False)
                profile_embed.add_field(
                    name=f'{info.schools[0].name}',
                    value=f"School Year: `{'1-'.join(str(info.schools[0].school_year).split('1'))}`",
                    inline=False
                )
                await ctx.send(embed=profile_embed)
        else:
            await ctx.send(
                f'{ctx.author.mention}, you have not registered your TDSB account yet! Use `r!tdsb register`'
            )

    @tdsb.command(aliases=['tt'], help='Usage: `r!tdsb timetable|tt [YYYY-MM-DD]` \n Date is optional, if a date is not'
                                       ' entered it will default to the current day')
    async def timetable(self, ctx, date=None):
        user = collection.find_one({'_id': ctx.author.id})
        if user:
            username = user['username']
            pwd = b64_decoder(user['password'])
            user = await self.client.fetch_user(ctx.author.id)
            avatar = user.avatar.url
            if not date:
                now = datetime.datetime.now()
                date = f'{now.year}-{now.month}-{now.day}'
                timetable_date = datetime.datetime.strptime(date, '%Y-%m-%d')
            else:
                timetable_date = datetime.datetime.strptime(date, '%Y-%m-%d')

            async with tdsbconnects.TDSBConnects() as session:
                await session.login(username=username, password=pwd)
                info = await session.get_user_info()
                timetable = await info.schools[0].timetable(timetable_date)
                nick = ctx.author.nick or ctx.author
                if timetable:
                    tt_embed = nextcord.Embed(title=f'{nick}\'s'
                                                    f' timetable for `{date}`',
                                              description=f'Day {timetable[0].course_cycle_day}',
                                              colour=nextcord.Colour.random())
                    tt_embed.set_thumbnail(url=avatar)

                    for item in timetable:
                        start = datetime.datetime.strptime(f'{item.course_start.hour}:{item.course_start.minute}',
                                                           '%H:%M').strftime('%I:%M %p')
                        end = datetime.datetime.strptime(f'{item.course_end.hour}:{item.course_end.minute}',
                                                         '%H:%M').strftime('%I:%M %p')
                        tt_embed.add_field(name=f'Period {item.course_period}: {start} - {end}',
                                           value=f'Class: {item.course_name} | {item.course_code} \n'
                                                 f'Teacher: {item.course_teacher_name} | `{item.course_teacher_email}`'
                                                 f'\n`Room {item.course_room}`', inline=False)
                    await ctx.send(embed=tt_embed)
                else:
                    await ctx.send(f'{ctx.author.mention}, there is no timetable for that day!')
        else:
            await ctx.send(
                f'{ctx.author.mention}, you have not registered your TDSB account yet! Use `r!tdsb register`')


def b64_encoder(password):
    password_bytes = password.encode('ascii')
    base64_bytes = base64.b64encode(password_bytes)
    password = base64_bytes.decode('ascii')
    return password


def b64_decoder(password):
    base64_bytes = password.encode('ascii')
    password_bytes = base64.b64decode(base64_bytes)
    password = password_bytes.decode('ascii')
    return password


def setup(client):
    client.add_cog(TdsbConnects(client))
