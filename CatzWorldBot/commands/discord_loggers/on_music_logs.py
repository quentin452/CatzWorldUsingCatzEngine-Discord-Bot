from discord.ext import commands
import discord
from utils.async_logs import LogMessageAsync
from datetime import datetime
from utils.EmbedUtility import *

# UNTESTED

class OnMusicLogs(commands.Cog):
    def __init__(self, bot, discord_logs_cog):
        self.bot = bot
        self.discord_logs_cog = discord_logs_cog

    def get_log_channel_id(self):
        discord_logs_cog = self.bot.get_cog('DiscordLogs')
        if discord_logs_cog is not None:
            return discord_logs_cog.log_channel_id
        return None
    
    @commands.Cog.listener()
    async def on_music_player_connection_error(self, error):
        log_channel = self.get_log_channel_id()
        if log_channel:
            try:
                embed = MusicPlayerErrorEmbed(error_message=error).create()
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music player connection error: {e}")

    @commands.Cog.listener()
    async def on_music_player_error(self, error):
        log_channel = self.get_log_channel_id()
        if log_channel:
            try:
                embed = MusicPlayerErrorEmbed(error_message=error).create()
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music player error: {e}")

    @commands.Cog.listener()
    async def on_music_audio_event(self, event_type, details):
        log_channel = self.get_log_channel_id()
        if log_channel:
            try:
                embed = MusicAudioEventEmbed(event_type=event_type, details=details).create()
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music audio event: {e}")

    @commands.Cog.listener()
    async def on_music_no_result(self, query):
        log_channel = self.get_log_channel_id()
        if log_channel:
            try:
                embed = MusicNoResultEmbed(query=query).create()
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music player no result: {e}")

    @commands.Cog.listener()
    async def on_music_queue_end(self):
        log_channel = self.get_log_channel_id()
        if log_channel:
            try:
                embed = MusicQueueEndEmbed().create()
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music queue end: {e}")

    @commands.Cog.listener()
    async def on_music_topgg_vote(self, user):
        log_channel = self.get_log_channel_id()
        if log_channel:
            try:
                embed = MusicTopGGVoteEmbed(user=user).create()
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music TopGG vote: {e}")

    @commands.Cog.listener()
    async def on_music_track_event(self, event_type, track):
        log_channel = self.get_log_channel_id()
        if log_channel:
            try:
                embed = MusicTrackEventEmbed(event_type=event_type, track=track).create()
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music track event: {e}")

    @commands.Cog.listener()
    async def on_music_tracks_add(self, tracks):
        log_channel = self.get_log_channel_id()
        if log_channel:
            try:
                embed = MusicTracksAddEmbed(tracks=tracks).create()
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging music tracks add: {e}")

async def setup(bot):
    discord_logs_cog = bot.get_cog('DiscordLogs')
    await bot.add_cog(OnMusicLogs(bot, discord_logs_cog))