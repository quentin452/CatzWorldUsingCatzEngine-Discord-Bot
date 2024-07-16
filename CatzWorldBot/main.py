import os
import subprocess
import sys
import discord
from discord.ext import commands
from utils.config import load_config
from utils.async_logs import LogMessageAsync
import time

current_path = os.path.dirname(os.path.abspath(__file__))
config = load_config()
token = config['token']
api_key = config['api_key']
game_id = config['game_id']

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

def install_modules(modules):
    subprocess.check_call([sys.executable, "-m", "pip", "install", *modules])

if __name__ == "__main__":
    required_modules = ['aiofiles', 'discord', 'feedparser', 'requests', 'beautifulsoup4', 'black']
    install_modules(required_modules)
    
async def load_extensions():
    current_folder = os.path.dirname(__file__) 
    extensions_folder = os.path.join(current_folder, 'commands')  
    
    if not os.path.exists(extensions_folder):
        await LogMessageAsync.LogAsync(f"Le dossier '{extensions_folder}' n'existe pas. Assurez-vous que le chemin est correct.")
        return
    
    extensions = []
    for filename in os.listdir(extensions_folder):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = f'commands.{filename[:-3]}'
            extensions.append(module_name)
    
    for extension in extensions:
        start_time = time.time()
        try:
            await bot.load_extension(extension)  
            end_time = time.time()
            elapsed_time = (end_time - start_time) * 1000  # Conversion en millisecondes
            await LogMessageAsync.LogAsync(f'Extension chargée : {extension} en {elapsed_time:.2f} millisecondes')
        except Exception as e:
            await LogMessageAsync.LogAsync(f'Erreur lors du chargement de {extension}: {type(e).__name__} - {e}')

@bot.event
async def on_ready():
    await LogMessageAsync.reset_log_file()
    # Setting `Playing ` status
    await bot.change_presence(activity=discord.Game(name="https://iamacatfrdev.itch.io/catzworld"))

    # Setting `Streaming ` status
    # await bot.change_presence(activity=discord.Streaming(name="My Stream", url=my_twitch_url))

    # Setting `Listening ` status
    # await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="a song"))

    # Setting `Watching ` status
    # await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="a movie"))

    await load_extensions()

    # PERSISTANT SAVING
    
    # Rôle Menu
    rmenu_cog = bot.get_cog('RoleMenu')
    if rmenu_cog is not None:
        role_menu_view = rmenu_cog.get_menu_view()
        bot.add_view(role_menu_view)

    # Ticket Commands
    ticket_cog = bot.get_cog('TicketCommands')
    if ticket_cog is not None:
        ticket_menu_view = ticket_cog.get_menu_view()
        bot.add_view(ticket_menu_view)


    # Feedback Commands
   # feedback_cog = bot.get_cog('FeedbackCommands')
   # if feedback_cog is not None:
   #     feedback_menu_view = feedback_cog.get_menu_view()
   #     bot.add_view(feedback_menu_view)

    # RSS Commands
    # rss_cog = bot.get_cog('RssCommands')
    #if rss_cog is not None:
    #    rss_menu_view = rss_cog.get_menu_view()
    #    bot.add_view(rss_menu_view)

    discord_log_cog = bot.get_cog('DiscordLogs')
    if discord_log_cog is None:
        await LogMessageAsync.LogAsync("L'extension 'DiscordLogs' n'est pas chargée.")
    else:
        if hasattr(discord_log_cog, 'log_channel_id'):
            channel = bot.get_channel(discord_log_cog.log_channel_id)
            if channel is None:
                await LogMessageAsync.LogAsync("Le salon avec l'ID donné n'existe pas ou le bot n'a pas la permission de le voir.")
            else:
                await channel.send("The bot has successfully started/restarted.")
        else:
            await LogMessageAsync.LogAsync("L'extension 'DiscordLogs' ne contient pas d'attribut 'log_channel_id'.")
@bot.event
async def on_commanderror(ctx, error):
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
