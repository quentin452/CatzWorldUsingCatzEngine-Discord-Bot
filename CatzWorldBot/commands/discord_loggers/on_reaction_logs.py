from discord.ext import commands
import discord
import asyncio
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *
from commands.discord_loggers.discord_logger_base import DiscordLogs
class OnReactionLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def get_log_channel_id(self):
        discord_logs_cog = self.bot.get_cog('DiscordLogs')
        if discord_logs_cog is not None:
            return discord_logs_cog.log_channel_id
        return None
    
    async def log_reaction_change(self, reaction, user, action):
        self.log_channel_id = self.get_log_channel_id()
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                message = reaction.message
                author = message.author
                embed = ReactionAddedEmbed(author, reaction, user, action, message).create()
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging reaction {action}: {e}")

    @commands.Cog.listener() #TODO FIX CREATED MESSAGES BEFORE LAUNCHING THE BOT CANNOT BE LOGGED
    async def on_reaction_add(self, reaction, user):
        await self.log_reaction_change(reaction, user, "added")

    @commands.Cog.listener() #TODO FIX CREATED MESSAGES BEFORE LAUNCHING THE BOT CANNOT BE LOGGED
    async def on_reaction_remove(self, reaction, user):
        await self.log_reaction_change(reaction, user, "removed")

async def setup(bot):
    await bot.add_cog(OnReactionLogs(bot))