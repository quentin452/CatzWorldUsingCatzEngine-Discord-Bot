import discord
from discord.ext import commands
import feedparser
import requests
from bs4 import BeautifulSoup

intents = discord.Intents.all()  # Activer tous les intents disponibles

# Créer une instance de bot avec les intents spécifiés
bot = commands.Bot(command_prefix='!', intents=intents)

token_file = 'token.txt'

@bot.event
async def on_ready():
    print(f'Nous nous sommes connectés en tant que {bot.user}')

@bot.command()
async def hello(ctx, nom: str):
    await ctx.send(f'Bonjour {nom}!')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def get_rss(ctx):
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

@hello.error
async def hello_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Veuillez fournir un nom après la commande !hello.')

with open(token_file, 'r') as f:
    token = f.read().strip()

bot.run(token)