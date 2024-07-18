from discord.ext import commands
import discord
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from datetime import datetime
from utils.EmbedUtility import *

class OnUserlogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_user_logs.json','on_user_logs')
        
    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_user_logs.json','on_user_logs',channel_id)
    
    @commands.command(help="Sets the log channel for (Users) logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_on_user_logs_channel(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)
        await ctx.send(f"L'ID du canal de on_user_logs a été mis à jour à {ctx.channel.id}")

    @commands.Cog.listener() # TODO , THIS IS NOT PROPERLY WORK
    async def on_user_update(self, before, after):
        if before.avatar != after.avatar:
            log_channel = self.bot.get_channel(self.log_channel_id)
            if log_channel:
                try:
                    embed = ProfilePictureChangedEmbed(before, after).create()
                    await log_channel.send(embed=embed)
                except Exception as e:
                    await log_channel.send(f"Error logging profile picture change: {e}")

def setup(bot):
    bot.add_cog(OnUserlogs(bot))
