import asyncio
import nextcord
from nextcord.ext import commands
# import os
import secrets
# from cogs.help import HelpCommand
from modules import wordle_utils as wd, geography as geo


def reference(msg: nextcord.Message):
    ref = msg.reference
    if not ref or not isinstance(ref.resolved, nextcord.Message):
        return False

    return True


class WordleGames(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.description = 'Wordle and more!'

    async def get_user_avatar(self, user_id):
        user = await self.client.fetch_user(user_id)
        avatar = user.avatar.url
        return avatar

    # @commands.group()
    # async def wordle(self, ctx):
        # if ctx.invoked_subcommand is None:
        #     group = HelpCommand()
        #     await group.send_group_help_poo(ctx, ctx.command)

    @commands.command(aliases=['p'])
    async def wordle(self, ctx: commands.Context):
        max_ = 6
        embed = nextcord.Embed(title='Bootleg Wordle',
                               description=f'{wd.Emojis.green} - correct letter and correct location\n'
                                           f'{wd.Emojis.yellow} - correct letter but wrong location\n'
                                           f'{wd.Emojis.white} - the letter is not in this word')
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        view = wd.QuitGame(ctx, False)
        await ctx.reply(embed=embed, view=view)
        if view.stopped:
            return

        wordle = secrets.choice(wd.WORDS).upper()
        correct, timeout = False, False
        for guesses in range(max_):
            await ctx.send(f'{ctx.author.mention} `Attempt {guesses + 1}/{max_}` '
                           f'| Reply to this message to guess')
            try:
                msg = await self.client.wait_for(
                    'message', check=lambda message:
                    message.author.id == ctx.author.id and
                    message.channel.id == ctx.channel.id and
                    reference(message) and
                    wd.check_alpha(message.content) is True, timeout=60
                )

            except asyncio.TimeoutError:
                if view.stopped:
                    break

                embed.add_field(name='Timed out!',
                                value=f'{ctx.author.mention}, you have timed out!\n'
                                      f'The word was: **{wordle}**',
                                inline=False)
                await ctx.send(embed=embed)
                timeout = True
                view.stop()
                break

            else:
                if view.stopped:
                    break

                length = len(msg.content)
                if msg.content.upper() == wordle:
                    embed.add_field(name=f'Attempt {guesses + 1}',
                                    value=f'`{msg.content.upper()}` {wd.Emojis.green * length}', inline=False)
                    embed.add_field(name='Correct!',
                                    value=f'{ctx.author.mention}\n'
                                          f'The word was **{wordle}** and you got it in **{guesses + 1}** '
                                          f'{"attempts" if guesses > 0 else "attempt"}',
                                    inline=False)
                    await msg.reply(embed=embed)
                    view.stop()
                    correct = True
                    break

                squares = wd.generate_squares(msg.content.upper(), wordle)
                embed.add_field(name=f'Attempt {guesses + 1}',
                                value=f'`{msg.content.upper()}` {squares}',
                                inline=False)
                sent = await msg.reply(embed=embed, view=view)

        if not correct and not timeout and not view.stopped:
            view.stop()
            embed.add_field(name='Maximum amount of guesses reached!',
                            value=f'{ctx.author.mention}\n'
                                  f'The word was: **{wordle}**',
                            inline=False)
            return await sent.edit(embed=embed, view=None)

    @commands.command()
    @commands.max_concurrency(2, commands.BucketType.guild)
    async def worldle(self, ctx: commands.Context):
        max_ = 6
        view = geo.Buttons(ctx)
        embed = nextcord.Embed(
            title='Bootleg Worldle (EXPERIMENTAL PHASE; THINGS MAY GO VERY WRONG)')
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=embed, view=view)
        if view.stopped:
            return

        country = geo.get_random_country()
        correct, timeout = False, False
        for guess in range(max_):
            if view.stopped:
                return
            await ctx.send(f'{ctx.author.mention} `Attempt {guess + 1}/{max_}` '
                           f'| Reply to this message to guess')
            try:

                msg = await self.client.wait_for(
                    'message',
                    check=lambda message: message.author.id == ctx.author.id and reference(message) and
                    message.channel.id == ctx.channel.id and geo.check(message.content) and not view.stopped,
                    timeout=60
                )

                if msg.content.lower() not in geo.COUNTRIES:
                    place = geo.search_fuzzy(msg.content)
                else:
                    place = msg.content
            except asyncio.TimeoutError:
                if view.stopped:
                    return

                embed.add_field(name='Timed out!',
                                value=f'{ctx.author.mention}, you have timed out!\n'
                                      f'The country was: **{country}**',
                                inline=False)
                await ctx.reply(embed=embed, view=None)
                timeout = True
                view.stop()
                break

            else:
                if view.stopped:
                    return

                guess_coords, country_coords = geo.get_coords(place), geo.get_coords(country)
                distance = geo.get_distance(country_coords, guess_coords)
                bearing = geo.calculate_compass_bearing(country_coords, guess_coords)
                proximity = geo.proximity_percentage(distance)
                squares = geo.get_squares(proximity)

                if distance == 0:
                    embed.add_field(
                        name=f'Attempt {guess + 1}',
                        value=f'`{place}` | ***{distance}km***  {squares}  {wd.Emojis.tada}  |  **{proximity}%**',
                        inline=False
                    )
                    embed.add_field(
                        name='Correct!',
                        value=f'{ctx.author.mention}\n'
                              f'The country was **{country}** and you got it in **{guess + 1}** '
                              f'{"attempts" if guess > 0 else "attempt"}',
                        inline=False
                    )
                    await msg.reply(embed=embed)
                    correct = True
                    view.stop()
                    break

                embed.add_field(
                    name=f'Attempt {guess+1}',
                    value=f'`{place}` | **{distance}km**  {squares}{bearing}  |  **{proximity}%**',
                    inline=False
                )
                sent = await msg.reply(embed=embed, view=view)

        if not correct and not timeout and not view.stopped:
            view.stop()
            embed.add_field(name='Maximum amount of guesses reached!',
                            value=f'{ctx.author.mention}\n'
                                  f'The country was: **{country}**',
                            inline=False)
            return await sent.edit(embed=embed, view=None)

    @worldle.error
    async def worldle_error(self, ctx, error):
        if isinstance(error, geo.GeocoderUnavailable):
            return await ctx.send(f'{ctx.author.mention} {error.message}')
        if isinstance(error, commands.MaxConcurrencyReached):
            return await ctx.send(
                f'{ctx.author.mention} As this command is still experimental, only **2** users are allowed to use it '
                f'at a time. Please wait until the current players finish.')
        if isinstance(error, AttributeError):
            return


def setup(client):
    client.add_cog(WordleGames(client))
