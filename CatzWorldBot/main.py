import os
import subprocess
import sys
import discord
from discord.ext import commands
from utils.config import load_config
from utils.async_logs import LogMessageAsync
import time
from utils.Constants import ConstantsClass
import psutil
import asyncio

current_path = os.path.dirname(os.path.abspath(__file__))
config = load_config()
token = config['token']
api_key = config['api_key']
game_id = config['game_id']

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

def kill_old_instances():
    current_process = psutil.Process()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        # Vérifiez si le nom du processus ou la ligne de commande correspond à celui du processus actuel
        if proc.info['name'] == current_process.name() or proc.info['cmdline'] == current_process.cmdline():
            # Ne tuez pas le processus actuel
            if proc.pid != current_process.pid:
                proc.kill()

def install_modules(modules):
    subprocess.check_call([sys.executable, "-m", "pip", "install", *modules])

if __name__ == "__main__":
    kill_old_instances()
    required_modules = ['PyNaCl','html5lib','lxml','aiofiles', 'py-cord', 'beautifulsoup4', 'black']
    install_modules(required_modules)
    
async def load_extensions(bot):
    current_folder = os.path.dirname(__file__)
    extensions_folder = os.path.join(current_folder, 'commands')

    if not os.path.exists(extensions_folder):
        await LogMessageAsync.LogAsync(f"The folder '{extensions_folder}' does not exist. Make sure the path is correct.")
        return

    extensions = []
    for root, _, files in os.walk(extensions_folder):
        for filename in files:
            if filename.endswith('.py') and not filename.startswith('__'):
                path = os.path.relpath(os.path.join(root, filename), current_folder)
                module_name = os.path.splitext(path)[0].replace(os.sep, '.')
                extensions.append(module_name)

    for extension in extensions:
        start_time = time.time()
        try:
            bot.load_extension(extension)  # Remove `await` here
            end_time = time.time()
            elapsed_time = (end_time - start_time) * 1000  # Conversion en millisecondes
            await LogMessageAsync.LogAsync(f'Extension Loaded : {extension} en {elapsed_time:.2f} millisecondes')
        except Exception as e:
            await LogMessageAsync.LogAsync(f'Error loading {extension}: {type(e).__name__} - {e}')
            
bot.remove_command('help')

@bot.event
async def on_ready():
    await LogMessageAsync.LogAsync("The github Project Directory is : " + ConstantsClass.get_github_project_directory())
    await LogMessageAsync.reset_log_file()
    # Setting `Playing ` status
    await bot.change_presence(activity=discord.Game(name="https://iamacatfrdev.itch.io/catzworld"))

    # Setting `Streaming ` status
    # await bot.change_presence(activity=discord.Streaming(name="My Stream", url=my_twitch_url))

    # Setting `Listening ` status
    # await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="a song"))

    # Setting `Watching ` status
    # await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="a movie"))

    await load_extensions(bot)

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

    # DiscordLogs Commands
    discord_logs_cog = bot.get_cog('OnReadyLogs')
    if discord_logs_cog is not None:
         await discord_logs_cog.on_ready()

    # Rules Commands
    rules_logs_cog = bot.get_cog('RulesCog')
    if rules_logs_cog is not None:
        rules_logs_cog_view = rules_logs_cog.get_menu_view()
        bot.add_view(rules_logs_cog_view)

    # Help Commands
    help_cog = bot.get_cog('CustomHelpCommandCog')
    if help_cog is not None:
        help_cog_view = help_cog.get_menu_view()
        bot.add_view(help_cog_view)
   
    # Vote Commands
    vote_cog = bot.get_cog('VoteView')
    if vote_cog is not None:
        vote_cog_view = vote_cog.get_menu_view()
        bot.add_view(vote_cog_view)

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
    await bot.sync_commands()

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