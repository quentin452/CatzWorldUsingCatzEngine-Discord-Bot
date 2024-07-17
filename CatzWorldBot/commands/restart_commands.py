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
            await ctx.send("Redémarrage du bot...")
            await self._restart_bot()

    async def _restart_bot(self):
        await self.bot.close()

        # Restart using subprocess
        python = sys.executable
        subprocess.Popen([python, *sys.argv])

        # Exit the current process
        sys.exit()

async def setup(bot):
    await bot.add_cog(RestartCommand(bot))
