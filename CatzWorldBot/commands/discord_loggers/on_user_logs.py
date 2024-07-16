from discord.ext import commands
import discord
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from datetime import datetime
from utils.EmbedUtility import *

class OnUserlogs(commands.Cog):
    def __init__(self, bot, discord_logs_cog):
        self.bot = bot
        self.discord_logs_cog = discord_logs_cog

    def get_log_channel_id(self):
        discord_logs_cog = self.bot.get_cog('DiscordLogs')
        if discord_logs_cog is not None:
            return discord_logs_cog.log_channel_id
        return None
    
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.avatar != after.avatar:
            self.log_channel_id = self.get_log_channel_id()
            log_channel = self.bot.get_channel(self.log_channel_id)
            if log_channel:
                try:
                    embed = ProfilePictureChangedEmbed(before, after).create()
                    await log_channel.send(embed=embed)
                except Exception as e:
                    await log_channel.send(f"Error logging profile picture change: {e}")

async def setup(bot):
    discord_logs_cog = bot.get_cog('DiscordLogs')
    await bot.add_cog(OnUserlogs(bot, discord_logs_cog))
