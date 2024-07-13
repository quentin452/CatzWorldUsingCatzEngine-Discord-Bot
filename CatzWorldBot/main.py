import os
import subprocess
import sys
import discord
from discord.ext import commands
from config import load_config

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
    current_folder = os.path.dirname(__file__) 
    extensions_folder = os.path.join(current_folder, 'commands')  
    
    if not os.path.exists(extensions_folder):
        print(f"Le dossier '{extensions_folder}' n'existe pas. Assurez-vous que le chemin est correct.")
        return
    
    extensions = []
    for filename in os.listdir(extensions_folder):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = f'commands.{filename[:-3]}'
            extensions.append(module_name)
    
    for extension in extensions:
        try:
            await bot.load_extension(extension)  
            print(f'Extension chargée : {extension}')
        except Exception as e:
            print(f'Erreur lors du chargement de {extension}: {type(e).__name__} - {e}')

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')
    await load_extensions()

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
