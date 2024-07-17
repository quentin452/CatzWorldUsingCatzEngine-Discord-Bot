import asyncio
import discord
import yt_dlp
from utils.Constants import ConstantsClass
import json
import os
import random
from discord.ext import commands
import time

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_channel = ConstantsClass.load_channel_template(self, ConstantsClass.MUSIC_SAVE_FOLDER + '/on_music_channel.json', 'on_music_channel')
        self.timestamp_file = os.path.join(ConstantsClass.MUSIC_SAVE_FOLDER, 'timestamp.json')
        self.cleanup_task = None

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

                # Schedule the cleanup task
                await self.schedule_cleanup_task()

            except Exception as e:
                await ctx.send(f"An error occurred while trying to play the song: {e}")

    @commands.command()
    async def play_random_song(self, ctx):
        voice_channel = await self.join_voice_channel(ctx)
        if voice_channel:
            try:
                music_directory = ConstantsClass.get_github_project_directory() + "/CatzWorldBot/saves/downloaded_musics/"
                # Obtenir la liste des fichiers musicaux disponibles
                music_files = [f for f in os.listdir(music_directory) if os.path.isfile(os.path.join(music_directory, f))]
                if not music_files:
                    await ctx.send("No music files found.")
                    return

                # Sélectionner un fichier musical aléatoire parmi les fichiers disponibles, en excluant "none"
                random_music_file = random.choice([f for f in music_files if f.lower() != "none"])
                music_path = os.path.join(music_directory, random_music_file)

                # Créer un embed Discord pour imprimer le titre complet
                embed = discord.Embed(title="Random Music Selected", description=f"Title: {random_music_file}", color=discord.Color.green())
                await ctx.send(embed=embed)

                # Charger et jouer le fichier musical sélectionné
                player = discord.FFmpegPCMAudio(music_path)
                ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

                # Save the timestamp
                with open(self.timestamp_file, 'w') as f:
                    json.dump({'timestamp': time.time()}, f)

                # Schedule the cleanup task
                await self.schedule_cleanup_task()

            except Exception as e:
                await ctx.send(f"An error occurred while trying to play a random song: {e}")

    async def schedule_cleanup_task(self):
        # Annuler la tâche de nettoyage si elle existe déjà
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()

        # Planifier la fonction de nettoyage pour s'exécuter après un certain temps (par exemple, 1 heure)
        self.cleanup_task = asyncio.ensure_future(self.cleanup_after_delay(3600))

    async def cleanup_after_delay(self, delay):
        await asyncio.sleep(delay)
        self.cleanup()

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

    @commands.command()
    async def vote_song_skip(self, ctx):
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("No song is currently playing.")
            return
        
        # Envoyer un message pour démarrer le vote
        message = await ctx.send("Vote to skip the current song. React with 👍 to skip, 👎 to continue listening.")
        # Ajouter les réactions au message
        await message.add_reaction("👍")
        await message.add_reaction("👎")

        def check(reaction, user):
            # Vérifier que la réaction est un pouce vers le haut et que l'utilisateur n'est pas le bot
            return str(reaction.emoji) == "👍" and user != self.bot.user

        try:
            # Attendre qu'un utilisateur réagisse avec un pouce vers le haut
            reaction, user = await self.bot.wait_for("reaction_add", timeout=35.0, check=check)
        except asyncio.TimeoutError:
            # Si personne ne réagit dans le temps imparti, continuer à jouer la musique
            await ctx.send("The vote to skip the music has expired.")
        else:
            # Si suffisamment d'utilisateurs ont voté pour passer la musique, jouer une autre musique aléatoire
            await ctx.send("The music was skipped by vote.")
            await self.stop_song(ctx)
            await self.play_random_song(ctx)

    @staticmethod
    async def search(query, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS).extract_info(query, download=False))
        return data.get('entries', [])

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

    @classmethod
    async def search(cls, query, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS).extract_info("ytsearch:" + query, download=False))
        return data.get('entries', [])

YTDL_FORMAT_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': ConstantsClass.get_github_project_directory() + "/CatzWorldBot/saves/downloaded_musics/" + '%(title)s.%(ext)s',
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
