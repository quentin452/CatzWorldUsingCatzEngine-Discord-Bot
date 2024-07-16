from discord.ext import commands
from utils.async_logs import LogMessageAsync
import discord

class CustomHelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="command that provide a list of all commands from the bot and documented.")
    async def help_cat(self, ctx):
        embed = discord.Embed(title="Aide par catégorie", description="Voici les catégories d'aide disponibles :", color=discord.Color.blue())
        for cog_name, cog in self.bot.cogs.items():
            command_list = "\n".join([f"{self.bot.command_prefix}{command.name}: {command.short_doc or 'Pas de description'}" for command in cog.get_commands() if not command.hidden])
            if command_list:
                embed.add_field(name=cog_name, value=command_list, inline=False)
        
        await ctx.send(embed=embed)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Commandes du bot", color=discord.Color.blue())
        for cog, commands in mapping.items():
            if cog:
                cog_name = cog.qualified_name
            else:
                cog_name = "Non catégorisé"

            command_list = "\n".join([f"{self.bot.command_prefix}{command.name}: {command.help or 'Pas de description'}" for command in commands if not command.hidden])
            if command_list:
                embed.add_field(name=cog_name, value=command_list, inline=False)
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(title="Aide du bot", description=page, color=discord.Color.blue())
            await destination.send(embed=embed)


    async def send_command_help(self, command):
        if command.hidden or any(check.__class__.__name__ == 'has_permissions' and check.kwargs.get('administrator', False) for check in command.checks):
            return
        embed = discord.Embed(title=f"Aide pour {self.bot.command_prefix}{command.name}", color=discord.Color.blue())
        embed.add_field(name="Description", value=command.help or "Pas de description", inline=False)
        embed.add_field(name="Utilisation", value=self.get_command_signature(command), inline=False)
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(title="Aide du bot", description=page, color=discord.Color.blue())
            await destination.send(embed=embed)


    async def send_cog_help(self, cog):
        embed = discord.Embed(title=f"Commandes de {cog.qualified_name}", color=discord.Color.blue())
        command_list = "\n".join([f"{self.bot.command_prefix}{command.name}: {command.help or 'Pas de description'}" for command in cog.get_commands() if not command.hidden])
        if command_list:
            embed.add_field(name="Commandes", value=command_list, inline=False)
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(title="Aide du bot", description=page, color=discord.Color.blue())
            await destination.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CustomHelpCommand(bot))