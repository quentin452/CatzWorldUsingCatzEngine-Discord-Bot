from discord.ext import commands
import discord
from utils.async_logs import LogMessageAsync
from datetime import datetime
from utils.EmbedUtility import *
from utils.Constants import ConstantsClass
# UNTESTED

class OnMusicLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_music_logs.json','on_music_logs')
        
    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_music_logs.json','on_music_logs',channel_id)
    
    @commands.command(help="Sets the log channel for (Musics) logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_on_music_logs_channel(self, ctx): 
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)
        await ctx.send(f"L'ID du canal de on_music_logs a été mis à jour à {ctx.channel.id}")
    
    @commands.Cog.listener() #TODO untested
    async def on_music_player_connection_error(self, error):
        if self.log_channel:
            try:
                embed = MusicPlayerErrorEmbed(error_message=error).create()
                await self.log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music player connection error: {e}")

    @commands.Cog.listener()#TODO untested
    async def on_music_player_error(self, error):
        if self.log_channel:
            try:
                embed = MusicPlayerErrorEmbed(error_message=error).create()
                await self.log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music player error: {e}")

    @commands.Cog.listener()#TODO untested
    async def on_music_audio_event(self, event_type, details):
        if self.log_channel:
            try:
                embed = MusicAudioEventEmbed(event_type=event_type, details=details).create()
                await self.log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music audio event: {e}")

    @commands.Cog.listener()#TODO untested
    async def on_music_no_result(self, query):
        if self.log_channel:
            try:
                embed = MusicNoResultEmbed(query=query).create()
                await self.log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music player no result: {e}")

    @commands.Cog.listener()#TODO untested
    async def on_music_queue_end(self):
        if self.log_channel:
            try:
                embed = MusicQueueEndEmbed().create()
                await self.log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music queue end: {e}")

    @commands.Cog.listener()#TODO untested
    async def on_music_topgg_vote(self, user):
        if self.log_channel:
            try:
                embed = MusicTopGGVoteEmbed(user=user).create()
                await self.log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music TopGG vote: {e}")

    @commands.Cog.listener()#TODO untested
    async def on_music_track_event(self, event_type, track):
        if self.log_channel:
            try:
                embed = MusicTrackEventEmbed(event_type=event_type, track=track).create()
                await self.log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music track event: {e}")

    @commands.Cog.listener()#TODO untested
    async def on_music_tracks_add(self, tracks):
        if self.log_channel:
            try:
                embed = MusicTracksAddEmbed(tracks=tracks).create()
                await self.log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music tracks add: {e}")

async def setup(bot):
    await bot.add_cog(OnMusicLogs(bot))