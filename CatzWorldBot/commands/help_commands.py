import discord
from discord.ext import commands

class CustomHelpCommand(commands.MinimalHelpCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            await destination.send(page)

    async def send_command_help(self, command):
        # Ignore hidden commands and those requiring admin permissions
        if command.hidden or any(isinstance(check, commands.has_permissions) and check.kwargs.get('administrator', False) for check in command.checks):
            return
        await super().send_command_help(command)

    @commands.command(name="help_cat")
    async def custom_help_command(self, ctx):
        await self.send_pages()

async def setup(bot):
    bot.help_command = CustomHelpCommand()