import nextcord
from nextcord.ext import commands
import asyncio
import random
import os
from aiohttp import request
from cogs.help_cog import HelpCommand

TENOR_KEY = os.environ['tenor']
APP_ID = os.environ['oxford_id']
APP_KEY = os.environ['oxford_key']


class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.description = 'Some misc stuff'

    async def get_user_avatar(self, user_id):
        user = await self.client.fetch_user(user_id)
        avatar = user.avatar.url
        return avatar

    @commands.group()
    async def misc(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.client.help_menu.send_group_help_poo(ctx, ctx.command)

    @commands.command(name='8ball')
    async def eight_ball(self, ctx, *, question):
        if not question.endswith('?'):
            question += '?'

        options = [
            'yeye def :thumbsup:',
            'hell nahhhh',
            '¯\_(ツ)_/¯',
            'idk abt that man',
            'yaaas slayy queen',
            'Perhaps...',
            'I forgor :skull:',
            'LMAOOO good one bro',
            'Absolutely!',
            'Gaslight, Gatekeep, Girlboss',
            ':smiling_imp::smiling_imp::smiling_imp:',
            'rq ima hook up the cia w/ this',
            f'whatever u say {str(ctx.author)[:-5]} :zany_face:',
            'It is certain',
            'It is decidedly so',
            'Without a doubt',
            'Yes, definitely',
            'You may rely on it',
            'As I see it, yes',
            'Most likely',
            'Outlook good',
            'Yes',
            'Signs point to yes',
            'Reply hazy try again',
            'Ask again later',
            'Better not tell you now',
            'Cannot predict now',
            'Concentrate and ask again',
            "Don't count on it",
            'My reply is no',
            'My sources say no',
            'Outlook not so good',
            'Very doubtful',

        ]

        embed = nextcord.Embed(
            title=f'{str(ctx.author)[:-5]}\'s question: {question}',
            description=f'**Answer**: {random.choice(options)}'
        )
        embed.set_thumbnail(
            url='https://www.bing.com/th?id=AMMS_704bf413867e91d76846f876432da298&w=149&h=149&c=8&rs=1&o=5&pid=3.1&rm=2'
        )
        embed.set_author(name='The Magic 8ball!')
        return await ctx.reply(embed=embed)

    @commands.command(name='rocky', aliases=['r'])
    # @commands.cooldown(, 5, commands.BucketType.user)
    async def random_rocky(self, ctx):
        path = '/Rockypics/'
        folder = os.listdir(path)
        image = random.choice(folder)
        print(image[:-4].upper())
        msg = await ctx.send(file=nextcord.File(f'{path}{image}'))
        print(msg)

    @misc.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def gif(self, ctx, *, search=None):
        if not search:
            return await ctx.send(f'{ctx.author.mention}, please specify a gif that you want to search!')
        else:
            url = f"https://g.tenor.com/v1/search?q={search}&key={TENOR_KEY}&contentfilter=high"
            async with request("GET", url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data['results']
                    gif_url = content[random.randint(0, 5)]['url']
                    await ctx.send(gif_url)
                else:
                    return await ctx.send(f'ERROR: {response.status} bad response status. Please try again later!')

    @misc.command(aliases=['nm'], help='memory/speed type minigame ')
    async def number_memory(self, ctx):
        await ctx.send(f'{ctx.author.mention}, you have started the number game! type quit if you want to exit.')
        numbers_list = list('123456789')
        points = 0
        digits = 1
        time_left = 3
        while True:
            completed_number = ''.join(random.choices(numbers_list, k=digits))
            await ctx.send(f'the number is ||{completed_number}||.')
            try:
                response = await self.client.wait_for(
                    'message', check=lambda message:
                    message.author.id == ctx.author.id, timeout=time_left
                )
                if response.content == 'quit':
                    await ctx.send(f'{ctx.author.mention}, you have quit the game with {points} points.')
                    break
                elif response.content == completed_number:
                    await ctx.send('correct number!')
                    points += 1
                    time_left -= 0.05
                    digits += 1
                else:
                    await ctx.send(f'incorrect number, the game has been ended with {points} points')
                    break

            except asyncio.TimeoutError:
                await ctx.send(
                        f'{ctx.author.mention}, you took too long to respond! The game has been ended with {points} '
                        f'points.')
                break

    @commands.command()
    async def touki(self, ctx):
        user = await self.client.fetch_user(582233435859582977)
        avatar = user.avatar.url
        embed = nextcord.Embed(
            title='He is Touki:',
            description='xiao kinnie',
            colour=nextcord.Colour.blue()
        )

        embed.set_footer(text='mommies')
        embed.set_image(url=avatar)
        embed.set_thumbnail(url=avatar)
        embed.set_author(name='Touki Popper Poppingtons')
        embed.add_field(name='totally fabulous', value='totally gay', inline=False)
        embed.add_field(name='one of the best', value='obviously bi', inline=False)
        embed.add_field(name='unfortunately handsome', value='unstraight when mimic', inline=False)
        embed.add_field(name='kys', value='kys', inline=False)
        embed.add_field(name='incredibly hot', value='incredible artist', inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def noodels(self, ctx):
        user = await self.client.fetch_user(436293909552037888)
        avatar = user.avatar.url
        embed = nextcord.Embed(
            title='He is Noodels:',
            description='idiot^2',
            colour=nextcord.Colour.orange()
        )

        embed.set_footer(text='piss')
        embed.set_image(url=avatar)
        embed.set_thumbnail(url=avatar)
        embed.set_author(name='noodelman')
        embed.add_field(name='no motivation', value='not straight', inline=False)
        embed.add_field(name='ordinary', value='obviously gay', inline=False)
        embed.add_field(name='oh ok', value='oh ok', inline=False)
        embed.add_field(name='dead inside', value='definitely bi', inline=False)
        embed.add_field(name='extremely introverted', value='emo', inline=False)
        embed.add_field(name='lazy', value='lazy', inline=False)
        embed.add_field(name='stupid', value='smells fruity', inline=False)

        await ctx.send(embed=embed)

    @misc.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def say(self, ctx, *, string):
        blacklist = '@'
        if blacklist in string:
            return await ctx.send(f'{ctx.author.mention} No pinging bozo')
        else:
            await ctx.message.delete()
            await ctx.send(string)

    @misc.command()
    @commands.cooldown(10, 5, commands.BucketType.user)
    async def dmtest(self, ctx, member: nextcord.Member = None):
        try:
            if not member:
                return await ctx.send(f'{ctx.author.mention}, you must specify one member!')
            else:
                await ctx.author.send('say smth rq thx')
                msg1 = await self.client.wait_for('message', check=lambda message:
                                                  message.author.id == ctx.author.id and message.guild is None,
                                                  timeout=20)
                await member.send('say smth rq thx')
                msg2 = await self.client.wait_for('message', check=lambda message:
                                                  message.author.id == member.id and message.guild is None, timeout=20)

                await ctx.send(
                    f'{member.mention}\'s message: {msg2.content} \n{ctx.author.mention}\'s message: {msg1.content}')

        except asyncio.TimeoutError:
            return await ctx.send(
                f'{ctx.author.mention} and {member.mention}: One of you has failed to respond and timed out!')

    @commands.command(name='what\'s', aliases=['whats', 'what', 'def', 'define'])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def what_is(self, ctx: commands.Context, *search: str):

        search = ' '.join(search)

        base_url = f'https://od-api.oxforddictionaries.com/api/v2/'

        headers = {
            'Accept': 'application/json',
            'app_id': APP_ID,
            'app_key': APP_KEY
        }

        async with request('GET', f'{base_url}lemmas/en/{search}', headers=headers) as response:
            if response.status != 200:
                return await ctx.send(
                    f'{ctx.author.mention} Error code {response.status}: {self.client.error_codes[response.status]}'
                )

            results = await response.json()
            final_results = []
            if results['results']:
                result = results['results'][0]['id']
                def_embed = nextcord.Embed(title=result, colour=nextcord.Colour.from_rgb(126, 25, 27))
                search_url = f'{base_url}entries/en-gb/{result}'
                params = {'strictMatch': 'false'}
                async with request('GET', search_url, headers=headers, params=params) as resp:
                    data = await resp.json()
                    entries = data['results'][0]['lexicalEntries']
                    for entry in entries:
                        index = entry['entries'][0]
                        try:
                            pro = index['pronunciations'][0]['phoneticSpelling']
                        except KeyError:
                            pro = f'\\{search}\\'
                        body = ''
                        synonyms = []
                        word = data['results'][0]['word']

                        for i in range(len(index['senses'])):
                            for definition in index['senses'][i].get('definitions', []):
                                to_add = f'\n \n**`{i + 1}.`** {definition}'
                                if len(body + to_add) > 1024:
                                    break
                                body += to_add

                            for example in index['senses'][i].get('examples', []):
                                try:
                                    body += f'\n \n*"{example["text"]}"*'
                                except KeyError:
                                    pass

                            for syn in index['senses'][i].get('synonyms', []):
                                try:
                                    synonyms.append(syn['text'])
                                except KeyError:
                                    pass

                        word_type = entry['lexicalCategory']['text']
                        body += '' if len(synonyms) == 0 else f"\n \n `Synonyms:` {', '.join(synonyms)}"
                        final_results.append({
                            'word': word,
                            'body': body,
                            'type': word_type,
                        })
                def_embed.set_author(
                    name=f'{str(ctx.author)[:-5]}\'s lookup',
                    icon_url=ctx.author.avatar.url)

                def_embed.title = result
                def_embed.description = pro

                for def_entry in final_results:
                    def_embed.add_field(
                        name=f'{def_entry["type"]}',
                        value=f"{def_entry['body']}",
                        inline=False
                    )
                if search.lower() == 'rocky':
                    def_embed.set_footer(text='Me ;)')

                return await ctx.reply(embed=def_embed)

            return await ctx.reply(f'{ctx.author.mention} No entries for that word found!')

    @commands.command()
    async def urban(self, ctx, *, search):
        url = 'https://mashape-community-urban-dictionary.p.rapidapi.com/define'

        params = {'term': search}

        headers = {
            'X-RapidAPI-Host': 'mashape-community-urban-dictionary.p.rapidapi.com',
            'X-RapidAPI-Key': 'aea5151139msh637cac94e5a08dbp1c04e3jsn1ecc569cc3dc'
        }

        async with request('GET', url, headers=headers, params=params) as resp:
            if resp.status == 200:
                embed = nextcord.Embed(
                    title='Urban Dictionary',
                    description='',
                    colour=nextcord.Colour.from_rgb(18, 78, 228)
                )
                embed.set_thumbnail(
                    url='https://www.bing.com/th?id=AMMS_9defafb39ddd2b907af66a0ffb9b40e3&w=110&h=1'
                        '10&c=7&rs=1&qlt=95&pcl=f9f9f9&o=6&cdv=1&pid=16.1')
                data = await resp.json()
                try:
                    item = data['list'][0]
                except IndexError:
                    embed.add_field(
                        name=':x: No definition found',
                        value='Come up with a better search next time ;)',
                        inline=False)
                    return await ctx.reply(embed=embed)
                else:
                    definition = item['definition']
                    example = item['example']
                    if len(example) > 1024 or len(definition) > 1024:
                        embed.add_field(
                            name='Sorry, the results were too large',
                            value=f'[See the definition on the website]({item["permalink"]})')
                        return await ctx.reply(embed=embed)

                    embed.add_field(name=f'{search}',
                                    value=f'\n{item["definition"]}',
                                    inline=False
                                    )
                    embed.add_field(name='‎', value=f'{item["example"]}', inline=False)

                    await ctx.reply(embed=embed)

    @what_is.error
    async def define_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f'{ctx.author.mention} You must specify a word to search!')
        if isinstance(error, commands.BadArgument):
            return await ctx.send(f'{ctx.author.mention} Your search must be a word!')

        raise error

    @urban.error
    async def urban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.reply(
                'You must specify a word to search! Use r!urban <your search>')

        raise error

    @dmtest.error
    async def dmtest_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'{ctx.author.mention}, invalid format! Use r!dmtest @user')
        if isinstance(error, commands.BadArgument):
            await ctx.send(f'{ctx.author.mention}, invalid argument! Use r!dmtest @user')
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'{ctx.author.mention}, you are on cooldown! Try again in {error.retry_after:.2f}s')

    @eight_ball.error
    async def eight_ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.reply('No question was specified! Use `r!8ball <your_question>`')

    @say.error
    async def say_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f'{ctx.author.mention} Invalid format, use: r!say <your message> !')
        if isinstance(error, commands.BadArgument):
            await ctx.send(
                f'{ctx.author.mention} Invalid arguments, use: r!say <your message> !')
 
    @random_rocky.error
    async def rocky_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'{ctx.author.mention}, you are on cooldown! Try again in {error.retry_after:.2f}s')

        raise error

    @gif.error
    async def gif_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'{ctx.author.mention}, you are on cooldown! Try again in {error.retry_after:.2f}s')


def setup(client):
    client.add_cog(Misc(client))
