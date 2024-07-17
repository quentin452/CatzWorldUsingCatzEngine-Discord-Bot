from discord.ext import commands
import discord
import asyncio
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *
class OnReactionLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_reaction_logs.json','on_reaction_logs')
        
    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_reaction_logs.json','on_reaction_logs',channel_id)
    
    @commands.command(help="Sets the log channel for (Reaction) logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_on_reaction_logs_channel(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)
        await ctx.send(f"L'ID du canal de on_reaction_logs a été mis à jour à {ctx.channel.id}")
    
    async def log_reaction_change(self, reaction, user, action):
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