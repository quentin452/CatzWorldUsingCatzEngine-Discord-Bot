import discord
from discord.ext import commands
import aiohttp
import json
import asyncio
from utils.Constants import ConstantsClass
from utils.config import load_config
from utils.async_logs import LogMessageAsync

config = load_config()
api_key = config['api_key']
game_id = config['game_id']

class DownloadCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.download_task = None
        self.getting_download = False
        self.download_channel_ids = self.load_download_channel_ids()
        self.sent_download_ids = self.load_sent_download_ids()
        self.bot.loop.create_task(self.run_download_loop())

    def load_download_channel_ids(self):
        try:
            with open(ConstantsClass.DOWNLOAD_SAVE_FOLDER + '/download_channel_ids.json', ConstantsClass.READ_FILE) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_download_channel_ids(self):
        with open(ConstantsClass.DOWNLOAD_SAVE_FOLDER + '/download_channel_ids.json', ConstantsClass.WRITE_TO_FILE) as f:
            json.dump(self.download_channel_ids, f)

    def load_sent_download_ids(self):
        try:
            with open(ConstantsClass.DOWNLOAD_SAVE_FOLDER + '/sent_download_ids.json', ConstantsClass.READ_FILE) as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_sent_download_ids(self):
        with open(ConstantsClass.DOWNLOAD_SAVE_FOLDER + '/sent_download_ids.json', ConstantsClass.WRITE_TO_FILE) as f:
            json.dump(self.sent_download_ids, f)

    async def fetch_uploads(self):
        url = f'https://itch.io/api/1/{api_key}/game/{game_id}/uploads'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('uploads', [])
        return []

    async def last_download_loop(self, channel):
        # Obtenez le rôle que vous voulez mentionner
        role = discord.utils.get(channel.guild.roles, name=ConstantsClass.ROLE_NAME)
        
        if role is None:
            await channel.send("Le rôle " + ConstantsClass.ROLE_NAME + "n'existe pas dans ce serveur.")
            return

        uploads = await self.fetch_uploads()
        if not uploads:
            await channel.send(f'{role.mention} Aucun fichier téléchargeable trouvé.')
            return

        uploads_sorted = sorted(uploads, key=lambda upload: upload.get('position', 0), reverse=True)
        last_upload = uploads_sorted[0]

        last_upload_id = last_upload.get('id')

        # Check if the last upload ID has already been sent
        if last_upload_id in self.sent_download_ids:
            return  # Exit if the id has already been sent recently
        
        keys_reverse = list(last_upload.keys())[::-1]
        info_str = "\n".join(f"{key}: {last_upload[key]}" for key in keys_reverse)

        # Ajoutez la mention du rôle au début du message
        await channel.send(f"{role.mention}\n```\n{info_str}\n```")

        # Save the last upload ID for this channel
        self.sent_download_ids.append(last_upload_id)
        self.save_sent_download_ids()

    @commands.command(help="Fetches and displays all downloadable files for the game from itch.io API. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def get_all_download(self, ctx):
        url = f'https://itch.io/api/1/{api_key}/game/{game_id}/uploads'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'uploads' in data:
                        # Tri des uploads par position décroissante
                        uploads_sorted = sorted(data['uploads'], key=lambda upload: upload.get('position', 0), reverse=True)
                        
                        for upload in uploads_sorted:
                            # Récupérer les clés dans l'ordre inverse
                            keys_reverse = list(upload.keys())[::-1]
                            info_str = "\n".join(f"{key}: {upload[key]}" for key in keys_reverse)
                            await ctx.send(f"```\n{info_str}\n```")
                    else:
                        await ctx.send('Aucun fichier téléchargeable trouvé.')
                else:
                    await ctx.send('Impossible de récupérer les fichiers téléchargeables.')

    @commands.command(help="Fetches and displays the latest downloadable file for the game from itch.io API.")
    async def get_last_download(self, ctx):
        url = f'https://itch.io/api/1/{api_key}/game/{game_id}/uploads'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'uploads' in data:
                        # Tri des uploads par position décroissante
                        uploads_sorted = sorted(data['uploads'], key=lambda upload: upload.get('position', 0), reverse=True)
                        
                        # Récupérer uniquement le dernier upload
                        last_upload = uploads_sorted[0]
                        keys_reverse = list(last_upload.keys())[::-1]
                        info_str = "\n".join(f"{key}: {last_upload[key]}" for key in keys_reverse)
                        await ctx.send(f"```\n{info_str}\n```")
                    else:
                        await ctx.send('Aucun fichier téléchargeable trouvé.')
                else:
                    await ctx.send('Impossible de récupérer les fichiers téléchargeables.')

    async def run_download_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for guild_id, channel_id in self.download_channel_ids.items():
                guild = self.bot.get_guild(int(guild_id))
                if guild:
                    channel = guild.get_channel(int(channel_id))
                    if channel:
                        if not self.getting_download:
                            self.getting_download = True
                            await self.last_download_loop(channel)
                            self.getting_download = False
                    else:
                        await LogMessageAsync.LogAsync(f"Channel with ID {channel_id} not found in guild {guild_id}.")
                else:
                    await LogMessageAsync.LogAsync(f"Guild with ID {guild_id} not found.")
            await asyncio.sleep(60)

    @commands.command(help="Sets the current channel as the download channel for automatic updates.")
    async def set_download_channel(self, ctx):
        self.download_channel_ids[str(ctx.guild.id)] = ctx.channel.id
        self.save_download_channel_ids()
        await ctx.send(f"L'ID du salon pour les téléchargements a été défini sur {ctx.channel.id} pour le serveur {ctx.guild.name}")
        
async def setup(bot):
    await bot.add_cog(DownloadCommands(bot))
