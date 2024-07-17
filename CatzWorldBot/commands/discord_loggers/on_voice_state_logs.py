from discord.ext import commands
import discord
import asyncio
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *
class OnVoiceStateLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_voice_state_logs.json','on_voice_state_logs')
        
    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_voice_state_logs.json','on_voice_state_logs',channel_id)
    
    @commands.command(help="Sets the log channel for (Voice/Stream State) logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_on_voice_state_logs_channel(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)
        await ctx.send(f"L'ID du canal de on_voice_state_logs a été mis à jour à {ctx.channel.id}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        log_channel = self.bot.get_channel(self.log_channel_id)
        
        if log_channel:
            try:
                # Check if member moved between voice channels
                if before.channel != after.channel:
                    if before.channel and after.channel:
                        # Member moved from one voice channel to another
                        embed = discord.Embed(
                            title='Member Moved Voice Channels',
                            description=f'{member.name}#{member.discriminator} moved from {before.channel.name} to {after.channel.name}',
                            color=discord.Color.dark_magenta()
                        )
                        await log_channel.send(embed=embed)
                    elif before.channel:
                        # Member left a voice channel
                        embed = discord.Embed(
                            title='Member Left Voice Channel',
                            description=f'{member.name}#{member.discriminator} left voice channel {before.channel.name}',
                            color=discord.Color.red()
                        )
                        await log_channel.send(embed=embed)
                    elif after.channel:
                        # Member joined a voice channel
                        embed = discord.Embed(
                            title='Member Joined Voice Channel',
                            description=f'{member.name}#{member.discriminator} joined voice channel {after.channel.name}',
                            color=discord.Color.green()
                        )
                        await log_channel.send(embed=embed)
                
                #TODO FIX STREAMING SECTION DOES NOT WORK
                # Check if member started or stopped streaming
                before_streaming = any(isinstance(activity, discord.Streaming) for activity in member.activities)
                after_streaming = any(isinstance(activity, discord.Streaming) for activity in member.activities)

                if before_streaming != after_streaming:
                    # Streaming status changed during voice state update
                    embed = discord.Embed(
                        title='Streaming Status Changed',
                        description=f'{member.name}#{member.discriminator} has {"started" if after_streaming else "stopped"} streaming.',
                        color=discord.Color.blue() if after_streaming else discord.Color.dark_blue()
                    )
                    embed.set_thumbnail(url=member.avatar.url)
                    await log_channel.send(embed=embed)
                
                # Check if member muted or unmuted themselves
                elif before.self_deaf != after.self_deaf:
                    action = 'Muted' if after.self_deaf else 'Unmuted'
                    embed = discord.Embed(
                        title=f'Member {action}',
                        description=f'{member.name}#{member.discriminator} {action.lower()} themselves in {after.channel.name}',
                        color=discord.Color.blue()
                    )
                    await log_channel.send(embed=embed)

            except Exception as e:
                await log_channel.send(f"Error logging voice state update: {e}")


async def setup(bot):
    await bot.add_cog(OnVoiceStateLogs(bot))