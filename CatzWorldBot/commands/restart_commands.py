import subprocess
import sys
import os
import discord
from discord.ext import commands

class RestartCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_restarting = False

    @commands.command(help="Restart the bot.")
    @commands.has_permissions(administrator=True)
    async def restart(self, ctx):
        if not self.is_restarting:
            self.is_restarting = True
            await ctx.send("Restarting the bot...")
            await self._restart_bot()

            
    @commands.command(help="Stop the bot.")
    @commands.has_permissions(administrator=True)
    async def stop_cat_bot(self, ctx):
        await ctx.send("Stop the bot...")
        sys.exit()

    async def _restart_bot(self):
        await self.bot.close()
        # Restart using subprocess
        python = sys.executable
        subprocess.Popen([python, *sys.argv])
        # Exit the current process
        sys.exit()

async def setup(bot):
    await bot.add_cog(RestartCommand(bot))
