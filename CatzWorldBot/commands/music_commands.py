from discord.ext import commands
import asyncio
import discord
import yt_dlp  # Assuming yt_dlp is used instead of youtube_dl
from utils.Constants import ConstantsClass
import json
import os
import time

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_channel = ConstantsClass.load_channel_template(self, ConstantsClass.MUSIC_SAVE_FOLDER + '/on_music_channel.json', 'on_music_channel')
        self.timestamp_file = os.path.join(ConstantsClass.MUSIC_SAVE_FOLDER, 'timestamp.json')

    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self, ConstantsClass.MUSIC_SAVE_FOLDER + '/on_music_channel.json', 'on_music_channel', channel_id)

    async def join_voice_channel(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                self.voice_channel = await channel.connect()
            else:
                await ctx.voice_client.move_to(channel)
            self.save_log_channel(channel.id)  # Save the voice channel ID
            return self.voice_channel
        else:
            await ctx.send("You are not connected to a voice channel.")
            return None

    @commands.command()
    async def play_song(self, ctx, url: str):
        voice_channel = await self.join_voice_channel(ctx)
        if voice_channel:
            try:
                player = await YTDLSource.from_url(url, loop=self.bot.loop)
                ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

                # Save the timestamp
                with open(self.timestamp_file, 'w') as f:
                    json.dump({'timestamp': time.time()}, f)

                # Schedule the cleanup function to run after a certain time (e.g., 1 hour)
                asyncio.get_event_loop().call_later(3600, self.cleanup)
            except Exception as e:
                await ctx.send(f"An error occurred while trying to play the song: {e}")

    def cleanup(self):
        """Delete all unplayed music files."""
        with open(self.timestamp_file, 'r') as f:
            data = json.load(f)
            timestamp = data['timestamp']

        music_directory = ConstantsClass.get_github_project_directory() + "/CatzWorldBot/saves/downloaded_musics/"
        # Delete all files that were created before the timestamp
        for filename in os.listdir(music_directory):
            filepath = os.path.join(music_directory, filename)
            if os.path.isfile(filepath) and os.path.getmtime(filepath) < timestamp:
                os.remove(filepath)

    @commands.command()
    async def stop_song(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("I'm not connected to a voice channel.")

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS).extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS).prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

YTDL_FORMAT_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': ConstantsClass.get_github_project_directory() + "/CatzWorldBot/saves/downloaded_musics/" + '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {
    'options': '-vn'
}

async def setup(bot):
    await bot.add_cog(Music(bot))
