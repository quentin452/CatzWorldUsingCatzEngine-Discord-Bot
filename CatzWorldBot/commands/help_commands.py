import discord
from discord.ext import commands

class CustomHelpCommand(commands.MinimalHelpCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            await destination.send(page)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Bot Commands", description="Here is a list of all commands you can use:", color=discord.Color.blue())
        for cog, commands in mapping.items():
            if cog:
                cog_name = cog.qualified_name
                command_list = "\n".join([f"`{command.name}`: {command.help or 'No description provided'}" for command in commands if not command.hidden])
                if command_list:
                    embed.add_field(name=cog_name, value=command_list, inline=False)
            else:
                command_list = "\n".join([f"`{command.name}`: {command.help or 'No description provided'}" for command in commands if not command.hidden])
                if command_list:
                    embed.add_field(name="Uncategorized", value=command_list, inline=False)
        destination = self.get_destination()
        await destination.send(embed=embed)

    async def send_command_help(self, command):
        if command.hidden or any(isinstance(check, commands.has_permissions) and check.kwargs.get('administrator', False) for check in command.checks):
            return

        embed = discord.Embed(title=f"Help with `{command.name}`", description=command.help or "No description provided", color=discord.Color.blue())
        embed.add_field(name="Usage", value=self.get_command_signature(command), inline=False)
        destination = self.get_destination()
        await destination.send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(title=f"{cog.qualified_name} Commands", description=cog.description or "No description provided", color=discord.Color.blue())
        command_list = "\n".join([f"`{command.name}`: {command.help or 'No description provided'}" for command in cog.get_commands() if not command.hidden])
        if command_list:
            embed.add_field(name="Commands", value=command_list, inline=False)
        destination = self.get_destination()
        await destination.send(embed=embed)

    async def send_group_help(self, group):
        if group.hidden or any(isinstance(check, commands.has_permissions) and check.kwargs.get('administrator', False) for check in group.checks):
            return

        embed = discord.Embed(title=f"Help with `{group.name}`", description=group.help or "No description provided", color=discord.Color.blue())
        embed.add_field(name="Usage", value=self.get_command_signature(group), inline=False)
        if group.commands:
            command_list = "\n".join([f"`{command.name}`: {command.help or 'No description provided'}" for command in group.commands if not command.hidden])
            if command_list:
                embed.add_field(name="Subcommands", value=command_list, inline=False)
        destination = self.get_destination()
        await destination.send(embed=embed)

async def setup(bot):
    bot.help_command = CustomHelpCommand()