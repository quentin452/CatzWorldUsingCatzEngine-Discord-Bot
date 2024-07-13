import discord
from discord.ext import commands
import feedparser
import requests
from bs4 import BeautifulSoup
from config import load_config

config = load_config()
api_key = config['api_key']
game_id = config['game_id']

class GetDownloadCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def get_download(self, ctx):
                url = f'https://itch.io/api/1/{api_key}/game/{game_id}/uploads'
                response = requests.get(url)

                if response.status_code == 200:
                    data = response.json()
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

async def setup(bot):
         await bot.add_cog(GetDownloadCommands(bot))
