from typing import Optional
from typing import List
import nextcord
from nextcord.ext import commands


class HelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return f't!{command.qualified_name} {command.signature}'

    async def help_embed(self, title: str, description: Optional[str] = None,
                         mapping: Optional[dict] = None,
                         command_set: Optional[List[commands.Command]] = None):
        embed = nextcord.Embed(title=title)
        embed.set_footer(text=f'Use t!help [category/command] for more info\n'
                              f'Commands are **case sensitive**')
        if description:
            embed.description = description
        if command_set:
            command_list = await self.filter_commands(command_set, sort=True)
            for command in command_list:
                embed.add_field(
                    name=self.get_command_signature(command),
                    value=(
                        f'{"Aliases:" ", ".join(command.aliases) if len(command.aliases) > 0 else ""}'
                        f'\n{command.help or ""}'
                    ),
                    inline=False)
        if mapping:
            for cog, command_set in mapping.items():
                filtered = await self.filter_commands(command_set, sort=True)
                if not filtered:
                    continue
                name = cog.qualified_name if cog else "No Category"
                cmd_list = "\n".join(f'`{self.context.clean_prefix}{cmd.name}`' for cmd in filtered)
                value = (f'{cog.description}\n{cmd_list}' if cog and cog.description else cmd_list)
                embed.add_field(name=name, value=value)
        return embed

    async def send_bot_help(self, mapping: dict):
        # print(self)
        # print(mapping)
        embed = await self.help_embed(title='RockyBot Commands',
                                      description='',
                                      mapping=mapping)
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command: commands.Command):
        embed = await self.help_embed(
            title=command.qualified_name,
            description=f'**Aliases**: `{", ".join(command.aliases)}`\n \n{command.help or ""}',
            command_set=command.commands if isinstance(command, commands.Group) else None)
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog: commands.Cog):
        embed = await self.help_embed(title=cog.qualified_name, description=cog.description,
                                      command_set=cog.get_commands())
        await self.get_destination().send(embed=embed)

    send_group_help = send_command_help

    async def send_group_help_poo(self, ctx, group: commands.Group):
        if group.help:
            desc = group.help
        elif group.short_doc:
            desc = group.short_doc
        else:
            desc = ''
        embed = nextcord.Embed(title=group.qualified_name, description=desc)
        filtered = list(group.commands)
        for cmd in filtered:
            embed.add_field(name=f'{self.get_command_signature(cmd)}', value=cmd.help, inline=False)

        embed.set_footer(text=f'Use t!help [command/category] for more info\n'
                              f'Commands are case sensitive!')
        await ctx.send(embed=embed)


class Help(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._original_help_command = client.help_command
        client.help_command = HelpCommand()
        client.help_command.cog = self


def setup(client):
    client.add_cog(Help(client))
