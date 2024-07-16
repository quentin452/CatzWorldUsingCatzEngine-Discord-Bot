from discord.ext import commands
import discord
import asyncio
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *

class DiscordLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/log_channel.json','log_channel_id')
        
    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/log_channel.json','log_channel_id',channel_id)

    @commands.command(help="Sets the log channel for logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)

    async def on_ready(self):
        if self.log_channel_id is None:
            self.log_channel_id = self.load_log_channel()
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = BotStartedEmbed().create()
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error sending startup message: {e}")
        else:
            await LogMessageAsync.LogAsync(f"Log channel with ID {self.log_channel_id} not found.")

    def getDiscordLogsCog(self):
        discord_logs_cog = self.bot.get_cog('DiscordLogs')
        if discord_logs_cog is not None:
            log_channel = self.bot.get_channel(discord_logs_cog.log_channel_id)
            return log_channel
        
async def setup(bot):
    await bot.add_cog(DiscordLogs(bot))