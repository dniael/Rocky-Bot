import datetime
from typing import Union, List
import nextcord
from nextcord.ext import commands
import os
import pymongo
import urllib.request

MONGO_URL = os.environ['mongo']

cluster = pymongo.MongoClient(MONGO_URL)
db = cluster['discord']
collection = db['bots']


def url_to_bytes(ctx: commands.Context, url: str) -> bytes:
    req = urllib.request.build_opener()
    req.addheaders = [('User-Agent', 'RockyBot Testing')]
    urllib.request.install_opener(req)
    urllib.request.urlretrieve(url, f'{ctx.author.id}_avatar.png')

    with open(f'{str(ctx.author)}_avatar.png', 'rb') as image:
        img_bytes = image.read()
        os.remove(f'{str(ctx.author)}_avatar.png')
        return img_bytes


async def find_webhook_from_channel(channel: nextcord.TextChannel, name: str) -> nextcord.Webhook:
    """
    Finds and returns a webhook that matches the given name from a given discord channel
    :param channel: a nextcord.TextChannel object
    :param name: the name of the webhook object to search for

    :return: a nextcord.Webhook object
    """
    try:
        webhooks = await channel.webhooks()
        webhook = [webhook for webhook in webhooks if webhook.name == name][0]
        return webhook
    except IndexError:
        pass


def find_webhook_from_db(channel_id: str, user: dict, include_channel_id: bool = False) -> Union[dict, tuple]:
    """
    Finds and returns a user's webhook dictionary that is in the MongoDB Database.

    :param channel_id: a stringified version of the channel id of the webhook
    :param user: a user dictionary from the database to search the webhook from
    :param include_channel_id: why is this here

    :return: a dictionary with the user's webhook attributes
    """
    try:
        bot: dict = [bot for bot in user['bots'] if channel_id in bot][0]
        if include_channel_id:
            return bot[channel_id], [k for k in bot.keys()][0]
        return bot[channel_id]
    except (KeyError, IndexError):
        pass


class Bots(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.description = 'Testing stuff'

    async def find_all_user_webhooks(self, webhooks: List[dict]) -> List[nextcord.Webhook]:
        """
        Takes all the webhooks of a user in the database and returns the nextcord.Webhook object equivalent to each

        :param webhooks: the webhooks of a user

        :return: A list of nextcord.Webhook objects
        """
        webhook_ids: List[int] = []
        for webhook in webhooks:
            for v in webhook.values():
                webhook_ids.append(v['id'])

        all_webhooks = [await self.client.fetch_webhook(_id) for _id in webhook_ids]

        return all_webhooks

    @commands.group()
    async def bot(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.client.help_menu.send_group_help_poo(ctx, ctx.command)

    @bot.command()
    async def create(self, ctx: commands.Context, prefix: str, *name: str):
        if not prefix:
            embed = nextcord.Embed(title='You must specify a prefix', description='Use `t!bot create <prefix> <name>`')
            embed.set_footer(text='Surround your prefix with quotation marks if it has spaces in it\n'
                                  'Example: t!bot create <"Your prefix here"> <name>')
            return await ctx.reply(embed=embed)

        if prefix == 't!':
            return await ctx.reply('Prefix cant be the same as the bot\'s')

        name = ' '.join(name) if name else f'{str(ctx.author)}\'s bot'

        if user := collection.find_one({'_id': ctx.author.id}):
            key = str(ctx.channel.id)

            if find_webhook_from_db(key, user):
                return await ctx.reply(
                    'Sorry, but you are only allowed one bot per channel as this feature is still in beta. '
                    'Use t!bot delete to delete your current bot'
                )

            webhook = await ctx.channel.create_webhook(
                name=name,
                reason='testing'
            )

            collection.update_many(
                {'_id': ctx.author.id},
                {'$push': {'bots': {key: {'prefix': prefix, 'name': name, 'disabled': False, 'id': webhook.id}}}}
            )

            embed = nextcord.Embed(
                title='Hello!', description=f'I am a custom webhook in ONLY this channel {ctx.channel}'
            )
            embed.add_field(name='Use *t!bot edit* to edit my name, prefix and avatar', value='‎')
            embed.add_field(name='Use *t!bot delete* to delete me', value='‎', inline=False)
            embed.add_field(name=f'Use *{prefix} <your message>* to echo messages', value='‎', inline=False)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            embed.timestamp = datetime.datetime.now()
            return await webhook.send(embed=embed)

        webhook = await ctx.channel.create_webhook(
            name=name,
            reason='testing'
        )
        collection.insert_one({
            '_id': ctx.author.id,
            'bots': [
                {
                    str(ctx.channel.id): {
                        'prefix': prefix,
                        'name': name,
                        'disabled': False,
                        'id': webhook.id
                    }
                }
            ]
        })
        embed = nextcord.Embed(
            title='Hello!',
            description=f'I am a custom webhook in ONLY this channel {ctx.channel}',
            colour=ctx.author.colour
        )
        embed.add_field(name='Use *t!bot edit* to edit my name, prefix and avatar', value='‎')
        embed.add_field(name='Use *t!bot delete* to delete me', value='‎', inline=False)
        embed.add_field(name=f'Use *{prefix} <your message>* to echo messages', value='‎', inline=False)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        embed.timestamp = datetime.datetime.now()
        await webhook.send(embed=embed)

    @bot.command(aliases=['del', 'd'])
    async def delete(self, ctx: commands.Context):
        if user := collection.find_one({'_id': ctx.author.id}):

            all_webhooks = await self.find_all_user_webhooks(user['bots'])
            view = DeleteWebhook(ctx, all_webhooks)
            return await ctx.reply('Delete a bot', view=view)

        await ctx.reply('No bot found')

    @bot.command()
    async def profile(self, ctx: commands.Context):

        pass

    @bot.command(aliases=['t'], help='Toggles the bot in this channel')
    async def toggle(self, ctx: commands.Context):
        if not (user := collection.find_one({'_id': ctx.author.id})):
            return await ctx.reply('No bot found')

        key = str(ctx.channel.id)

        if not (bot := find_webhook_from_db(key, user)):
            return await ctx.reply('No bot in this channel')

        collection.update_many(
            {f'bots.{key}.prefix': bot['prefix']},
            {
                '$set': {
                    f'bots.$.{key}.disabled': not bot['disabled']
                }
            }
        )

        await ctx.reply(f'Bot successfully toggled, it is now {"enabled" if bot["disabled"] else "disabled"}')

    @bot.command()
    async def edit(self, ctx: commands.Context):
        if user := collection.find_one({'_id': ctx.author.id}):
            bot = find_webhook_from_db(str(ctx.channel.id), user)
            webhook = await find_webhook_from_channel(ctx.channel, bot['name'])

            view = WebhookButtons(ctx, webhook)
            embed = nextcord.Embed(title='Edit your bot\'s name, prefix, and pfp')
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            return await ctx.reply(embed=embed, view=view)

        await ctx.reply('No bot found')

    # @bot.command(name='all')
    # async def _all(self, ctx: commands.Context):
    #     guild1 = await self.client.fetch_guild(927381192129519646)
    #     # guild2 = await self.client.fetch_guild(911811204761153637)
    #
    #     async for webhook in guild1.webhooks():
    #         await webhook.send(f'The end is NEAR')
    #
    #     # for webhook in await guild2.webhooks():
    #     #     await webhook.send(f'The end is NEAR')
    #
    #     for _ in range(3):
    #         await ctx.command.reinvoke(ctx)

    @commands.Cog.listener()
    async def on_message(self, msg: nextcord.Message):
        if msg.author.bot: return

        if not (user := collection.find_one({'_id': msg.author.id})): return

        if not (bot := find_webhook_from_db(str(msg.channel.id), user)): return

        if bot['disabled']: return

        if msg.content.startswith(bot['prefix']):

            # get the message content after the prefix
            message = msg.content[len(bot['prefix']):]
            if len(message) < 1: return
            try:
                await msg.delete()
                webhook = await find_webhook_from_channel(msg.channel, bot['name'])
                if message.strip() == 'id':
                    return await webhook.send(str(webhook.id))
                return await webhook.send(message)

            except nextcord.HTTPException:
                pass


class AllUserWebhooks(nextcord.ui.Select):
    def __init__(self, webhooks: List[nextcord.Webhook]):
        options = [
            nextcord.SelectOption(
                label=webhook.name,
                description=f'In channel {webhook.channel_id} | #{webhook.channel.name}',
                value=webhook.name
            )
            for webhook in webhooks
        ]
        super().__init__(placeholder='Select a bot', min_values=1, max_values=1, options=options)
        self.webhooks = webhooks
        self.webhooks_queue: List[nextcord.Webhook] = []

    async def callback(self, interaction: nextcord.Interaction):
        webhook = [webhook for webhook in self.webhooks if webhook.name == self.values[0]][0]
        self.webhooks_queue.append(webhook)
        await interaction.response.send_message(
            f'Selected webhook {self.values[0]}. Press the delete button to confirm delete',
            ephemeral=True
        )


class DeleteWebhook(nextcord.ui.View):
    def __init__(self, ctx: commands.Context, webhooks: List[nextcord.Webhook]):
        super().__init__(timeout=None)
        self.view = AllUserWebhooks(webhooks)
        self.add_item(self.view)
        self.ctx = ctx

    @nextcord.ui.button(label='Delete', style=nextcord.ButtonStyle.danger)
    async def delete_webhook(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        if inter.user.id != self.ctx.author.id: return

        webhook = self.view.webhooks_queue[-1]
        name, channel_name = webhook.name, webhook.channel.name
        user = collection.find_one({'_id': inter.user.id})
        key = str(webhook.channel_id)
        if not (bot := find_webhook_from_db(key, user)):
            return await inter.response.send_message('No bot found in this channel', ephemeral=True)

        collection.update_many(
            {'_id': inter.user.id},
            {
                '$pull': {
                    'bots': {
                        key: {
                            'prefix': bot['prefix'],
                            'name': bot['name'],
                            'disabled': bot['disabled'],
                            'id': bot['id']
                        }
                    }
                }
            }
        )
        await webhook.delete()
        await inter.response.send_message(
            f'Webhook {name!r} in channel {channel_name!r} has been deleted',
            ephemeral=True
        )


class WebhookButtons(nextcord.ui.View):
    def __init__(self, ctx: commands.Context, webhook: nextcord.Webhook):
        super().__init__(timeout=None)
        self.value = None
        self.ctx = ctx
        self.stopped = False
        self.webhook = webhook

    @nextcord.ui.button(label='Edit name', style=nextcord.ButtonStyle.blurple)
    async def edit_name(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        if inter.user.id != self.ctx.author.id: return

        await inter.response.send_modal(EditName(self.webhook))

    @nextcord.ui.button(label='Edit prefix', style=nextcord.ButtonStyle.blurple)
    async def edit_prefix(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        if inter.user.id != self.ctx.author.id: return

        await inter.response.send_modal(EditPrefix())

    @nextcord.ui.button(label='Edit pfp', style=nextcord.ButtonStyle.blurple)
    async def edit_pfp(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        if inter.user.id != self.ctx.author.id: return

        await inter.response.send_modal(EditPfp(self.ctx, self.webhook))


class EditName(nextcord.ui.Modal):
    def __init__(self, webhook: nextcord.Webhook):
        super().__init__('Edit Your Bot\'s Name')
        self.webhook = webhook

        self.name = nextcord.ui.TextInput(
            label='Bot Name',
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=50,
            required=True,
            placeholder='Enter a new name for your bot!'
        )
        self.add_item(self.name)

    async def callback(self, interaction: nextcord.Interaction):
        key = str(interaction.channel_id)
        user = collection.find_one({'_id': interaction.user.id})
        bot = find_webhook_from_db(key, user)
        collection.update_many(
            {f'bots.{key}.prefix': bot['prefix']},
            {
                '$set': {
                    f'bots.$.{key}.name': self.name.value
                }
            }
        )
        await self.webhook.edit(name=self.name.value)
        await interaction.response.send_message(
            f'{interaction.user.mention} Bot name successfully changed to {self.name.value!r}',
            ephemeral=True
        )


class EditPrefix(nextcord.ui.Modal):
    def __init__(self):
        super().__init__('Edit Your Bot\'s Prefix')

        self.prefix = nextcord.ui.TextInput(
            label='Bot Prefix',
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=10,
            required=True,
            placeholder='Enter a new prefix!'
        )

        self.add_item(self.prefix)

    async def callback(self, interaction: nextcord.Interaction):
        key = str(interaction.channel_id)
        user = collection.find_one({'_id': interaction.user.id})
        bot = find_webhook_from_db(key, user)
        collection.update_many(
            {f'bots.{key}.prefix': bot['prefix']},
            {
                '$set': {
                    f'bots.$.{key}.prefix': self.prefix.value
                }
            }
        )
        await interaction.response.send_message(
            f'{interaction.user.mention} Bot prefix successfully changed to {self.prefix.value!r}',
            ephemeral=True
        )


class EditPfp(nextcord.ui.Modal):
    def __init__(self, ctx: commands.Context, webhook: nextcord.Webhook):
        super().__init__('Edit Your Bot\'s Profile Picture')
        self.ctx = ctx
        self.webhook = webhook

        self.avatar_url = nextcord.ui.TextInput(
            label='Bot Avatar',
            style=nextcord.TextInputStyle.short,
            required=True,
            placeholder='Enter a new avatar url! (PNG OR JPG ONLY)'
        )
        self.add_item(self.avatar_url)

    async def callback(self, interaction: nextcord.Interaction):
        try:
            await self.webhook.edit(avatar=url_to_bytes(self.ctx, url=self.avatar_url.value))
            await interaction.response.send_message(
                f'{interaction.user.mention} Bot pfp successfully changed to {self.avatar_url.value}',
                ephemeral=True
            )

        except Exception as e:
            return await interaction.response.send_message(
                f'{interaction.user.mention} Error: {e}\nCheck the url '
                'and try again (it must be a url and png/jpg format)',
                ephemeral=True
            )


def setup(client):
    client.add_cog(Bots(client))
