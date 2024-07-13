import os
import subprocess
import sys
import discord
from discord.ext import commands
from config import load_config
from commands.rss_commands import RssCommands  # Assurez-vous d'importer RssCommands depuis le bon chemin

current_path = os.path.dirname(os.path.abspath(__file__))
config = load_config()
token = config['token']
api_key = config['api_key']
game_id = config['game_id']

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

def install_modules(modules):
    for module in modules:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

if __name__ == "__main__":
    required_modules = ['discord', 'feedparser', 'requests', 'beautifulsoup4', 'black']
    install_modules(required_modules)

async def load_extensions():
    initial_extensions = [
        'commands.basic_commands',
        'commands.admin_commands',
        'commands.rss_commands',
        'commands.get_download_commands',
        'commands.help_commands'
    ]

    for extension in initial_extensions:
        try:
            await bot.load_extension(extension) 
            print(f'Extension chargée : {extension}')
        except Exception as e:
            print(f'Erreur lors du chargement de {extension}: {type(e).__name__} - {e}')

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')
    await load_extensions()

    rss_cog = bot.get_cog('RssCommands')
    if rss_cog:
        rss_cog.rss_task = bot.loop.create_task(rss_cog.run_rss_loop())
    else:
        print("Impossible de trouver le Cog RssCommands.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Commande introuvable.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Argument manquant.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Mauvais argument fourni.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('Vous n\'avez pas la permission d\'utiliser cette commande.')
    else:
        await ctx.send(f'Une erreur est survenue : {str(error)}')

bot.run(token)
