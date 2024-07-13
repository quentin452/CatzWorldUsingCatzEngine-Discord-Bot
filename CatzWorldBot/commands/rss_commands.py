import discord
from discord.ext import commands
import feedparser
import requests
from bs4 import BeautifulSoup
from config import load_config

config = load_config()
api_key = config['api_key']
game_id = config['game_id']

class RssCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def get_rss(self, ctx):
            # URL du flux RSS
            rss_url = 'https://iamacatfrdev.itch.io/catzworld/devlog.rss'

            # Récupérer et analyser le flux RSS
            feed = feedparser.parse(rss_url)
            if 'entries' in feed:
                    for entry in feed.entries:
                        title = entry.get('title', 'Pas de titre')
                        link = entry.get('link', 'Pas de lien')

                        # Récupérer le contenu de la page liée
                        response = requests.get(link)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            # Trouver la section spécifique
                            section = soup.find('section', {'class': 'object_text_widget_widget base_widget user_formatted post_body'})
                            if section:
                                # Récupérer le texte de la section et supprimer les lignes vides
                                content = "\n".join([line.strip() for line in section.get_text(separator='\n').splitlines() if line.strip()])
                                await ctx.send(f"**{title}**\n{content}\n{link}")
                            else:
                                await ctx.send(f"**{title}**\nContenu non trouvé.\n{link}")
                        else:
                            await ctx.send(f"**{title}**\nImpossible de récupérer la page liée.\n{link}")
            else:
                    await ctx.send('Impossible de récupérer le flux RSS.')

async def setup(bot):
         await bot.add_cog(RssCommands(bot))
