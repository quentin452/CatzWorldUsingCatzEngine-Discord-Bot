import asyncio
import discord
import yt_dlp
from utils.Constants import ConstantsClass
import json
import os
import random
from discord.ext import commands
import time
from utils.async_logs import LogMessageAsync

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_channel = ConstantsClass.load_channel_template(self, ConstantsClass.MUSIC_SAVE_FOLDER + '/on_music_channel.json', 'on_music_channel')
        self.timestamp_file = os.path.join(ConstantsClass.MUSIC_SAVE_FOLDER, 'timestamp.json')
        self.cleanup_task = None
        self.song_end_event = asyncio.Event()

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
        
    @commands.command(help="Stop music from voice music [url].")
    async def play_song(self, ctx, url: str):
        voice_channel = await self.join_voice_channel(ctx)
        if voice_channel:
            try:
                player = await YTDLSource.from_url(url, loop=self.bot.loop)
                ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

                # Send embed with song title
                await self.send_music_embed(ctx, player.title)

                # Save the timestamp
                with open(self.timestamp_file, 'w') as f:
                    json.dump({'timestamp': time.time()}, f)

                # Schedule the cleanup task
                await self.schedule_cleanup_task()

            except Exception as e:
                await ctx.send(f"An error occurred while trying to play the song: {e}")

    async def send_music_embed(self, ctx, title, repeat_count=None):
        description = "Now playing:"
        if repeat_count is not None:
            description += f" Repeat count: {repeat_count}"
        embed = discord.Embed(title=title, description=description, color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(help="Play music in a loop [url] [ammount].")
    async def loop_song(self, ctx, url: str, repeat_count: int):
        voice_channel = await self.join_voice_channel(ctx)
        if voice_channel:
            try:
                async def after_play(error):
                    nonlocal repeat_count
                    if error:
                        print(f'Error in playing: {error}')
                    if repeat_count > 1:
                        repeat_count -= 1
                        player = await YTDLSource.from_url(url, loop=self.bot.loop)  # Recreate the player
                        await self.send_music_embed(ctx, player.title, repeat_count)  # Update embed with new repeat count
                        ctx.voice_client.play(player, after=lambda e: self.bot.loop.create_task(after_play(e)))  # Ensure future for after_play using bot.loop

                player = await YTDLSource.from_url(url, loop=self.bot.loop)
                ctx.voice_client.play(player, after=lambda e: self.bot.loop.create_task(after_play(e)))

                # Send initial embed with song title and initial repeat count
                await self.send_music_embed(ctx, player.title, repeat_count)

                # Save the timestamp
                with open(self.timestamp_file, 'w') as f:
                    json.dump({'timestamp': time.time()}, f)

            except Exception as e:
                await ctx.send(f"Une erreur s'est produite lors de la tentative de lecture de la chanson : {e}")

    @commands.command(help="Play a random game from the bot's saved files.")
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

    @commands.command(help="Stop music from voice music.")
    async def stop_song(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("I'm not connected to a voice channel.")

    @commands.command(help="Vote to skip music.")
    async def vote_song_skip(self, ctx):
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("No song is currently playing.")
            return
        
        # Vérifier si la chanson en cours provient d'une playlist
        is_playlist = False  # Initialiser la variable pour vérifier si c'est une playlist
        current_source = ctx.voice_client.source
        if isinstance(current_source, YTDLSource):
            is_playlist = current_source.is_playlist
        
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
            # Si suffisamment d'utilisateurs ont voté pour passer la musique
            await ctx.send("The music was skipped by vote.")
            await self.stop_song(ctx)
            
            if is_playlist:
                # Si c'est une playlist, passer à la chanson suivante
                await self.play_next_in_playlist(ctx)
            else:
                # Sinon, jouer une autre musique aléatoire
                await self.play_random_song(ctx)

    async def play_next_in_playlist(self, ctx):
        # Récupérer le source actuel et le joueur
        current_source = ctx.voice_client.source
        if isinstance(current_source, YTDLSource) and current_source.is_playlist:
            # Passer à la prochaine chanson dans la playlist
            await current_source.next_song()
        else:
            await ctx.send("Not currently playing from a playlist.")

    async def extract_playlist_info(self, playlist_url):
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS).extract_info(playlist_url, download=False))
        return data.get('entries', [])

    def handle_playlist_next(self, ctx, playlist_url, playlist_info, playlist_index, error):
        async def after_play(error):
            nonlocal playlist_index
            if error:
                print(f'Error in playing: {error}')
            
            if playlist_index < len(playlist_info):
                playlist_index += 1
                next_song_url = f"{playlist_url}&index={playlist_index}"  # Increment playlist index
                player = await YTDLSource.from_url(next_song_url, loop=self.bot.loop)
                await self.send_music_embed(ctx, player.title, playlist_index)
                ctx.voice_client.play(player, after=lambda e: self.bot.loop.create_task(after_play(e)))
            else:
                await self.schedule_cleanup_task()

        return lambda e: self.bot.loop.create_task(after_play(e))
        
    def song_ended(self, error):
        if error:
            print(f'Player error: {error}')
        self.song_end_event.set()

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

    async def next_song(self):
        self.playlist_index += 1
        self.fils_depute += 1  # Incrémenter le compteur fils depute
        next_song_url = f"{self.url}&index={self.playlist_index}"  # Construire l'URL de la chanson suivante
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS).extract_info(next_song_url, download=False))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if 'url' in data else yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS).prepare_filename(data)
        return YTDLSource(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

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