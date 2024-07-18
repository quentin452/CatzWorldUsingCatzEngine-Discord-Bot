import subprocess
import sys
import os
import discord
from discord.ext import commands
import json
from utils.Constants import ConstantsClass

class RestartCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_restarting = False
        self.restart_channel_id = None

    @commands.command(help="Restart the bot.")
    @commands.has_permissions(administrator=True)
    async def restart(self, ctx):
        if not self.is_restarting:
            self.is_restarting = True
            await ctx.send("Restarting the bot...")
            # Save the restart channel ID to the JSON file
            ConstantsClass.save_channel_template(
                self,
                ConstantsClass.LOGS_SAVE_FOLDER + '/on_ready_logs.json',
                'channel_id',
                ctx.channel.id
            )
            await self._restart_bot()

    @commands.command(help="Stop the bot.")
    @commands.has_permissions(administrator=True)
    async def stop_cat_bot(self, ctx):
        await ctx.send("Stopping the bot...")
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