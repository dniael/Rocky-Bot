from typing import Optional
import nextcord
from nextcord.ext import commands
import pymongo
from aiohttp import request
import arrow
import os
from cogs.help_cog import HelpCommand

API_KEY = os.environ['fm_key']
API_URL = 'http://ws.audioscrobbler.com/2.0/'
MONGO_URL = os.environ['mongo']

cluster = pymongo.MongoClient(MONGO_URL)
db = cluster['discord']
collection = db['lastfm']


class LastFm(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.description = 'LastFm Commands!'

    async def get_user_avatar(self, user_id):
        user = await self.client.fetch_user(user_id)
        avatar = user.avatar.url
        return avatar

    @nextcord.slash_command(
        name='fmsearch',
        description='Search a song or artist on LastFm',
        guild_ids=[927381192129519646, 911811204761153637]
    )
    async def search(
        self,
        interaction: nextcord.Interaction,
        query_type: str = nextcord.SlashOption(
            name='type',
            description='type of search',
            choices={'artist': 'artist', 'song': 'song'}
        ),
        query: str = None
    ):
        await interaction.response.send_message(content=f'{query_type} {query}', ephemeral=True)

    @commands.group(help='LastFm commands for your stats')
    async def fm(self, ctx):
        if ctx.invoked_subcommand is None:
            group = HelpCommand()
            await group.send_group_help_poo(ctx, ctx.command)

    @fm.command(help='adds your LastFm account to the database')
    async def set(self, ctx, username=None):
        if username is None:
            return await ctx.send(f'{ctx.author.mention}, you must specify your username!')
        else:
            check = collection.find_one({'_id': ctx.author.id})
            if check is None:
                content = await user_info(username)
                if content is None:
                    return await ctx.send(f'{ctx.author.mention}, that username was not found!')
                else:
                    collection.insert_one({'_id': ctx.author.id, 'lastfm_user': username})
                    await ctx.send(f'{ctx.author.mention}, LastFm account successfully added to the database!')

            else:
                return await ctx.send(
                    f'{ctx.author.mention}, you already have a pre-existing account in the database!\n'
                    ' Use `r!fm unset` to delete'
                )

    @fm.command(help='delete your LastFm username from the database')
    async def unset(self, ctx):
        check = collection.find_one({'_id': ctx.author.id})
        if check is None:
            return await ctx.send(
                f'{ctx.author.mention}, you do not have a pre-existing LastFm username in the database!'
            )
        else:
            collection.delete_one({'_id': ctx.author.id})
            await ctx.send(
                f'{ctx.author.mention}, LastFm username successfully removed from the database!'
            )

    @fm.command(help='Gets your recently scrobbled songs on LastFm', aliases=['re'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def recent(self, ctx):
        user = collection.find_one({'_id': ctx.author.id})
        if user is None:
            return await ctx.send(
                f'{ctx.author.mention}, you have not added your LastFm username!'
                ' Use `r!fm set <username>`'
            )
        else:
            username = user['lastfm_user']
            avatar = await self.get_user_avatar(ctx.author.id)
            tracks = await get_recent_tracks(username, 10)
            tracks, user_attr = tracks['recenttracks']['track'], tracks['recenttracks']['@attr']
            # np = "@attr" in tracks[0] and "nowplaying" in tracks[0]["@attr"]
            lastfm_embed1 = nextcord.Embed(title=f'{username}\'s recent songs', description='',
                                           colour=nextcord.Colour.random())
            lastfm_embed1.set_thumbnail(url=avatar)
            lastfm_embed1.set_footer(text=f'Total Scrobbles: {user_attr["total"]}')

            for i in range(len(tracks)):
                try:
                    utc_date = arrow.get(int(tracks[i]['date']['uts']))
                    local_date = utc_date.to('local')
                    lastfm_embed1.description += \
                        f"\n**{tracks[i]['name']} 一 {tracks[i]['artist']['#text']} |** " \
                        f"{tracks[i]['album']['#text']}" \
                        f"\n> `{local_date.format('HH:mm:ss')}`"

                except KeyError:
                    lastfm_embed1.description += \
                        f"\n**{tracks[i]['name']} 一 {tracks[i]['artist']['#text']} |** " \
                        f"{tracks[i]['album']['#text']}\n> `Right Now`"

            await ctx.send(embed=lastfm_embed1)

    @fm.command(aliases=['ta'], help='Gets your top artists on LastFm')
    async def topartists(self, ctx):
        user = collection.find_one({'_id': ctx.author.id})
        if user is None:
            return await ctx.send(
                f'{ctx.author.mention}, you have not linked your LastFm account!'
                ' Use `r!fm set <username>`'
            )
        else:
            username = user['lastfm_user']
            avatar = await self.get_user_avatar(ctx.author.id)
            params = {'method': 'user.getTopArtists', 'user': username, 'api_key': API_KEY, 'format': 'json',
                      'limit': 10}

            async with request('GET', API_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    tracks = await get_recent_tracks(username, 1)
                    attr = tracks['recenttracks']['@attr']
                    artists = data['topartists']['artist']
                    nick = ctx.author.nick if ctx.author.nick is not None else ctx.author
                    top_artists_embed = nextcord.Embed(title=f'Your top 10 artists', description='',
                                                       colour=nextcord.Colour.random())
                    top_artists_embed.set_thumbnail(url=artists[0]['image'][-1]['#text'])
                    top_artists_embed.set_footer(text=f'Total Playcount: {attr["total"]}')
                    top_artists_embed.set_author(name=f'{nick} | fm {username}', icon_url=avatar)

                    for i in range(len(artists)):
                        artist = artists[i]['name']
                        playcount = artists[i]['playcount']
                        top_artists_embed.description += f'\n**#{" " if i<9 else ""}{i+1}** ' \
                                                         f'`{playcount} plays` 一 **{artist}** '

                    await ctx.send(embed=top_artists_embed)
                else:
                    return await ctx.send(
                        f'ERROR: {response.status} bad response status. Please try again in a few seconds'
                    )

    @fm.command(name='np')
    async def now_playing(self, ctx):
        user = collection.find_one({'_id': ctx.author.id})
        if not user:
            return await ctx.send(
                f'{ctx.author.mention}, you have not linked your LastFm account!'
                ' Use `r!fm set <username>`'
            )
        else:
            username = user['lastfm_user']
            avatar = await self.get_user_avatar(ctx.author.id)
            track = await get_recent_tracks(username, 2)
            track = track['recenttracks']['track']
            # print(track)
            now = "@attr" in track[0] and "nowplaying" in track[0]["@attr"]
            state = "Now Playing " if now else "Last Song Played "
            artist, name = track[0]["artist"]["#text"],  track[0]["name"]
            track_data = await get_track_data(username, name, artist)
            track_data = track_data['track']
            nick = ctx.author.nick if ctx.author.nick else str(ctx.author)[:-5]

            np_embed = nextcord.Embed(title=f'{state}:notes: ',
                                      description='',
                                      colour=ctx.author.colour)
            np_embed.description += f'[**{name} 一 {artist}**]({track_data["url"]})\n' \
                                    f'> {track[0]["album"]["#text"]}'
            np_embed.set_author(name=f'{nick} | fm {username}', icon_url=avatar)
            np_embed.set_thumbnail(url=track[0]['image'][-1]['#text'])
            np_embed.set_footer(text=f"Your playcount: {track_data['userplaycount']}")

            await ctx.send(embed=np_embed)

    @fm.command(aliases=['tt'], help='Gets your top scrobbled tracks')
    async def toptracks(self, ctx):
        user = collection.find_one({'_id': ctx.author.id})
        if not user:
            return await ctx.send(
                f'{ctx.author.mention}, you have not linked your LastFm account!'
                ' Use r!fm set <username>'
            )
        else:
            username = user['lastfm_user']
            avatar = await self.get_user_avatar(ctx.author.id)
            tracks = await get_top_tracks(username)
            track = await get_recent_tracks(username, 2)
            attr = track['recenttracks']['@attr']
            tracks = tracks['toptracks']['track']
            nick = ctx.author.nick or ctx.author
            tt_embed = nextcord.Embed(title='Your Top 10 Tracks', description='',
                                      colour=ctx.author.colour)
            tt_embed.set_thumbnail(url=avatar)
            tt_embed.set_footer(text=f'Total Playcount: {attr["total"]}')
            tt_embed.set_author(name=f'{nick} | fm {username}', icon_url=avatar)

            for i in range(len(tracks)):
                playcount = tracks[i]['playcount']
                name = tracks[i]['name']
                artist = tracks[i]['artist']['name']
                tt_embed.description += f'\n**#{" " if i+1<10 else ""}{i+1}** ' \
                                        f'`Plays: {playcount}` **{name}** 一 {artist}'

            await ctx.send(embed=tt_embed)

    @recent.error
    async def recent_error(self, ctx, error):
        if isinstance(error, LastFmError):
            return await ctx.send(f'{ctx.author.mention} {error.message}')

        raise error

    @toptracks.error
    async def top_tracks__error(self, ctx, error):
        if isinstance(error, LastFmError):
            return await ctx.send(f'{ctx.author.mention} {error.message}')

        raise error

    @topartists.error
    async def top_artists_error(self, ctx, error):
        if isinstance(error, LastFmError):
            return await ctx.send(f'{ctx.author.mention} {error.message}')

        raise error

    @now_playing.error
    async def np_error(self, ctx, error):
        if isinstance(error, LastFmError):
            return await ctx.send(f'{ctx.author.mention} {error.message}')

        raise error


async def user_info(username):
    params = {'user': username, 'method': 'user.getInfo', 'api_key': API_KEY, 'format': 'json'}
    async with request('GET', API_URL, params=params) as response:
        if response.status == 200:
            data = await response.json()
            if data:
                return True
            else:
                return None


async def get_track_data(username, track, artist):
    params = {'user': username, 'track': track, 'artist': artist, 'method': 'track.getInfo', 'api_key': API_KEY,
              'format': 'json'}
    async with request('GET', API_URL, params=params) as response:
        if response.status == 200:
            data = await response.json()
            return data

        raise LastFmError(f'ERROR: {response.status} bad response status')


async def get_artist_data(username, artist):
    params = {'user': username, 'artist': artist, 'method': 'track.getInfo', 'api_key': API_KEY,
              'format': 'json'}
    async with request('GET', API_URL, params=params) as response:
        if response.status == 200:
            data = await response.json()
            return data

        raise LastFmError(f'ERROR: {response.status} bad response status')


async def get_top_tracks(username):
    params = {'user': username, 'method': 'user.getTopTracks', 'api_key': API_KEY,
              'format': 'json', 'limit': 10}
    async with request('GET', API_URL, params=params) as response:
        if response.status == 200:
            data = await response.json()
            return data

        raise LastFmError(f'ERROR: {response.status} bad response status')


async def get_recent_tracks(username, limit):
    params = {'user': username, 'method': 'user.getRecentTracks', 'api_key': API_KEY,
              'format': 'json', 'limit': limit}
    async with request('GET', API_URL, params=params) as response:
        if response.status == 200:
            data = await response.json()
            return data

        raise LastFmError(f'ERROR: {response.status} bad response status')


async def get_song_or_artist_info(query_type, query):
    pass


class LastFmError(commands.CommandError):
    def __init__(self, message):
        super().__init__()
        self.message = message


def setup(client):
    client.add_cog(LastFm(client))
