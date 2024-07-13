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
        self.sent_rss_titles = self.load_sent_rss_titles()  # Load sent RSS titles from file
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

    def load_sent_rss_titles(self):
        try:
            with open('sent_rss_titles.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_sent_rss_titles(self):
        with open('sent_rss_titles.json', 'w') as f:
            json.dump(self.sent_rss_titles, f)

    async def get_last_rss(self, channel):
        # Obtenez le rôle que vous voulez mentionner
        role = discord.utils.get(channel.guild.roles, name="CatWorld game ping updates")

        if role is None:
            await channel.send("Le rôle CatWorld game ping updates n'existe pas dans ce serveur.")
            return

        rss_url = 'https://iamacatfrdev.itch.io/catzworld/devlog.rss'
        feed = feedparser.parse(rss_url)
        if 'entries' in feed:
            new_entries = [entry for entry in feed.entries if entry.get('title', 'Pas de titre') not in self.sent_rss_titles]

            if not new_entries:
                return

            for entry in new_entries:
                title = entry.get('title', 'Pas de titre')
                link = entry.get('link', 'Pas de lien')

                response = requests.get(link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    section = soup.find('section', {'class': 'object_text_widget_widget base_widget user_formatted post_body'})
                    if section:
                        content = "\n".join([line.strip() for line in section.get_text(separator='\n').splitlines() if line.strip()])
                        await channel.send(f"{role.mention}\n**{title}**\n```\n{content}\n```\n`{link}`")  # Encapsulate link in backticks
                    else:
                        await channel.send(f"{role.mention}\n**{title}**\nContenu non trouvé.\n`{link}`")  # Encapsulate link in backticks
                else:
                    await channel.send(f"{role.mention}\n**{title}**\nImpossible de récupérer la page liée.\n`{link}`")  # Encapsulate link in backticks

                # Update sent RSS titles
                self.sent_rss_titles.append(title)
                self.save_sent_rss_titles()  # Save sent RSS titles to file
                break  # Only process the first new entry for now
        else:
            await channel.send(f'{role.mention} Impossible de récupérer le flux RSS.')

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
            await asyncio.sleep(60)

async def setup(bot):
    await bot.add_cog(RssCommands(bot))