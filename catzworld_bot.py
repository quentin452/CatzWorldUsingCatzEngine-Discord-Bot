import subprocess
import sys

required_modules = ['discord', 'feedparser', 'requests', 'beautifulsoup4', 'black']

def install_modules(modules):
    for module in modules:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

missing_modules = []
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print(f"Modules manquants détectés : {', '.join(missing_modules)}. Installation en cours...")
    install_modules(missing_modules)

import os
import discord
from discord.ext import commands
import feedparser
import requests
from bs4 import BeautifulSoup

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

itch_io_api_key_file = '!security/itch_io_api_key.txt'
itch_io_game_id_file = '!security/itch_io_game_id.txt'
token_file = '!security/discord_bot_token.txt'

# Vérifier et créer les fichiers si nécessaire pour l'API key itch.io
if not os.path.exists(itch_io_api_key_file):
    with open(itch_io_api_key_file, 'w') as f:
        f.write('itch_io_api_key')

# Vérifier et créer les fichiers si nécessaire pour l'ID de jeu itch.io
if not os.path.exists(itch_io_game_id_file):
    with open(itch_io_game_id_file, 'w') as f:
        f.write('itch_io_game_id')

# Vérifier et créer les fichiers si nécessaire pour le token Discord
if not os.path.exists(token_file):
    with open(token_file, 'w') as f:
        f.write('discord_bot_token_id')

# Lire les valeurs depuis les fichiers
with open(itch_io_api_key_file, 'r') as f:
    api_key = f.read().strip()

with open(itch_io_game_id_file, 'r') as f:
    game_id = f.read().strip()

with open(token_file, 'r') as f:
    token = f.read().strip()

# Vérifier si les valeurs sont vides et afficher un message approprié si nécessaire
if not api_key:
    print("Veuillez mettre votre API key de votre jeu d'itch.io dans le fichier '!security/itch_io_api_key.txt'.")
if not game_id:
    print("Veuillez mettre l'ID de votre jeu itch.io dans le fichier '!security/itch_io_game_id.txt'.")
if not token:
    print("Veuillez mettre le token de votre bot discord dans le fichier '!security/discord_bot_token.txt'.")

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
async def get_downloads(ctx):
    url = f'https://itch.io/api/1/{api_key}/game/{game_id}/uploads'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if 'uploads' in data:
            for upload in data['uploads']:
                title = upload.get('filename', 'Pas de titre')
                download_url = upload.get('url', 'Pas de lien')
                await ctx.send(f"**{title}**\n{download_url}")
        else:
            await ctx.send('Aucun fichier téléchargeable trouvé.')
    else:
        await ctx.send('Impossible de récupérer les fichiers téléchargeables.')


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

@bot.command()
@commands.has_permissions(administrator=True)
async def reset_channel(ctx):
    def check_message(message):
        return True

    deleted = 0
    while True:
        deleted_messages = await ctx.channel.purge(limit=100, check=check_message)
        deleted += len(deleted_messages)
        if len(deleted_messages) < 100:
            break
    await ctx.send(f"Le salon a été réinitialisé. {deleted} messages ont été supprimés.")

@hello.error
async def hello_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Veuillez fournir un nom après la commande !hello.')
    else:
        await ctx.send(f'Une erreur est survenue : {error}')

@reset_channel.error
async def reset_channel_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('Vous n\'avez pas la permission d\'utiliser cette commande.')
    else:
        await ctx.send(f'Une erreur est survenue : {error}')

bot.run(token)
