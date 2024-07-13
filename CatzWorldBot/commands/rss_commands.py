import discord
from discord.ext import commands
import feedparser
import requests
import asyncio
from bs4 import BeautifulSoup
from config import load_config


config = load_config()
api_key = config['api_key']
game_id = config['game_id']

class RssCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rss_task = None
        self.rss_channel_id = 0
        self.getting_rss = False 
        self.bot.loop.create_task(self.run_rss_loop())

    @commands.command()
    async def get_last_rss(self, ctx):
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
                
                # Sortir de la boucle après avoir envoyé la première entrée
                break
        else:
            await ctx.send('Impossible de récupérer le flux RSS.')

    @commands.command()
    async def set_rss_channel(self, ctx):
        self.rss_channel_id = ctx.channel.id
        await ctx.send(f"L'ID du salon pour les messages RSS a été défini sur {self.rss_channel_id}")

    async def run_rss_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            channel = self.bot.get_channel(self.rss_channel_id)
            if channel:
                if not self.getting_rss:
                    self.getting_rss = True
                    await self.get_last_rss(channel)
                    self.getting_rss = False
            else:
                if self.rss_channel_id == 0:
                    print(f"Channel with ID {self.rss_channel_id} not found.")                   
            await asyncio.sleep(5)

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
