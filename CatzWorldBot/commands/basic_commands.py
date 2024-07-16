import discord
from discord.ext import commands

class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Greets the user with a hello message.")
    async def hello(self, ctx, nom: str):
        await ctx.send(f"Hello {nom}!")

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))
