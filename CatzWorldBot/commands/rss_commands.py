import discord
from discord.ext import commands
import feedparser
import requests
import asyncio
from bs4 import BeautifulSoup
import json

from config import load_config

config = load_config()
api_key = config['api_key']
game_id = config['game_id']

class RssCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rss_task = None
        self.getting_rss = False
        self.rss_channel_ids = self.load_rss_channel_ids()
        self.last_rss_entries = self.load_last_rss_entries()  # Load last RSS entries from file
        self.bot.loop.create_task(self.run_rss_loop())

    def load_rss_channel_ids(self):
        try:
            with open('rss_channel_ids.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_rss_channel_ids(self):
        with open('rss_channel_ids.json', 'w') as f:
            json.dump(self.rss_channel_ids, f)

    def load_last_rss_entries(self):
        try:
            with open('last_rss_entries.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_last_rss_entries(self):
        with open('last_rss_entries.json', 'w') as f:
            json.dump(self.last_rss_entries, f)

    async def get_last_rss(self, channel):
        rss_url = 'https://iamacatfrdev.itch.io/catzworld/devlog.rss'
        feed = feedparser.parse(rss_url)
        if 'entries' in feed:
            for entry in feed.entries:
                title = entry.get('title', 'Pas de titre')
                link = entry.get('link', 'Pas de lien')
                try:
                    if self.last_rss_entries.get(str(channel.id)) == link:
                        break
                except AttributeError as e:
                    print(f"Erreur lors de l'accès à l'ID du canal : {e}")
                    break  # Exit the loop if there's an error accessing ctx.channel.id
                response = requests.get(link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    section = soup.find('section', {'class': 'object_text_widget_widget base_widget user_formatted post_body'})
                    if section:
                        content = "\n".join([line.strip() for line in section.get_text(separator='\n').splitlines() if line.strip()])
                        await channel.send(f"**{title}**\n{content}\n{link}")
                    else:
                        await channel.send(f"**{title}**\nContenu non trouvé.\n{link}")
                else:
                    await channel.send(f"**{title}**\nImpossible de récupérer la page liée.\n{link}")
                # Update last_rss_entries for this channel
                self.last_rss_entries[str(channel.id)] = link
                self.save_last_rss_entries()  # Save last_rss_entries to file
                break  # Only process the first entry for now
        else:
            await channel.send('Impossible de récupérer le flux RSS.')

    @commands.command()
    async def set_rss_channel(self, ctx):
        self.rss_channel_ids[str(ctx.guild.id)] = ctx.channel.id
        self.save_rss_channel_ids()
        await ctx.send(f"L'ID du salon pour les messages RSS a été défini sur {ctx.channel.id} pour le serveur {ctx.guild.name}")
        
    @commands.command()
    async def get_rss(self, ctx):
        rss_url = 'https://iamacatfrdev.itch.io/catzworld/devlog.rss'
        feed = feedparser.parse(rss_url)
        if 'entries' in feed:
            for entry in feed.entries:
                title = entry.get('title', 'Pas de titre')
                link = entry.get('link', 'Pas de lien')
                response = requests.get(link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    section = soup.find('section', {'class': 'object_text_widget_widget base_widget user_formatted post_body'})
                    if section:
                        content = "\n".join([line.strip() for line in section.get_text(separator='\n').splitlines() if line.strip()])
                        await ctx.send(f"**{title}**\n{content}\n{link}")
                    else:
                        await ctx.send(f"**{title}**\nContenu non trouvé.\n{link}")
                else:
                    await ctx.send(f"**{title}**\nImpossible de récupérer la page liée.\n{link}")

    async def run_rss_loop(self):
            await self.bot.wait_until_ready()
            while not self.bot.is_closed():
                for guild_id, channel_id in self.rss_channel_ids.items():
                    guild = self.bot.get_guild(int(guild_id))
                    if guild:
                        channel = guild.get_channel(int(channel_id))
                        if channel:
                            if not self.getting_rss:
                                self.getting_rss = True
                                await self.get_last_rss(channel)
                                self.getting_rss = False
                        else:
                            print(f"Channel with ID {channel_id} not found in guild {guild_id}.")
                    else:
                        print(f"Guild with ID {guild_id} not found.")
                await asyncio.sleep(30)
async def setup(bot):
    await bot.add_cog(RssCommands(bot))