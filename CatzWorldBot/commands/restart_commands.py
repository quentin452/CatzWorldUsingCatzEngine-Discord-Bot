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
        await self.bot.close()
        sys.exit()

    async def _restart_bot(self):
        try:
            # Properly close the bot's connection
            await self.bot.close()
        except Exception as e:
            print(f"Error closing the bot: {e}")

        # Give some time for connections to close
        await asyncio.sleep(1)

        # Restart using subprocess
        python = sys.executable
        try:
            subprocess.Popen([python, *sys.argv])
        except Exception as e:
            print(f"Error restarting the bot: {e}")

        # Exit the current process
        sys.exit()

def setup(bot):
    bot.add_cog(RestartCommand(bot))