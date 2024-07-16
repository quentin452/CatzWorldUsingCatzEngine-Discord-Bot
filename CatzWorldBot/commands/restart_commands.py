import subprocess
import sys
import os
import discord
from discord.ext import commands

is_restarting = False 

class RestartCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True) 
    async def restart(self, ctx):
        global is_restarting 
        if not is_restarting:
            is_restarting = True
            await ctx.send("Redémarrage du bot...")
            await self._restart_bot()

    async def _restart_bot(self):
        await self.bot.close()
        
        # Redémarrage du script Python
        python = sys.executable
        os.execl(python, python, *sys.argv)

async def setup(bot):
    await bot.add_cog(RestartCommand(bot))
