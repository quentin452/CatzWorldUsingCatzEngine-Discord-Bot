import os
import subprocess
import sys
import discord
from discord.ext import commands
from discord.ext.ipc import Server, ClientPayload
from utils.config import load_config
from utils.async_logs import LogMessageAsync
import time
from utils.Constants import ConstantsClass
import psutil

# Chargement de la configuration
current_path = os.path.dirname(os.path.abspath(__file__))
config = load_config()
token = config['token']
api_key = config['api_key']
game_id = config['game_id']

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='/', intents=intents)
        self.ipc = Server(self, secret_key="keks")

    async def on_ready(self):
        """Action à réaliser lorsque le bot est prêt."""
        await self.ipc.start()
        await LogMessageAsync.LogAsync("The github Project Directory is : " + ConstantsClass.get_github_project_directory())
        await LogMessageAsync.reset_log_file()
        await self.change_presence(activity=discord.Game(name="mention me 🤗"))

        await self.load_extensions()

        # DiscordLogs Commands
        discord_logs_cog = bot.get_cog('OnReadyLogs')
        if discord_logs_cog is not None:
            await discord_logs_cog.on_ready()

        # PERSISTANT SAVING
        for cog_name in ['RoleMenu', 'TicketCommands', 'RulesCog', 'CustomHelpCommandCog', 'VoteView']:
            cog = self.get_cog(cog_name)
            if cog is not None:
                view = cog.get_menu_view()
                self.add_view(view)
                if cog_name == 'OnReadyLogs':
                    await cog.on_ready()

    async def on_commanderror(self, ctx, error):
        """Gérer les erreurs des commandes."""
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

    async def load_extensions(self):
        """Charger les extensions depuis le dossier 'commands'."""
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
                await self.load_extension(extension)
                end_time = time.time()
                elapsed_time = (end_time - start_time) * 1000
                await LogMessageAsync.LogAsync(f'Extension Loaded : {extension} en {elapsed_time:.2f} millisecondes')
            except Exception as e:
                await LogMessageAsync.LogAsync(f'Error loading {extension}: {type(e).__name__} - {e}')

    @Server.route()
    async def guild_count(self, _):
        return str(len(self.guilds))

    @Server.route()
    async def bot_guilds(self, _):
        guild_ids = [str(guild.id) for guild in self.guilds]
        return {"data": guild_ids}

    @Server.route()
    async def guild_stats(self, data: ClientPayload):
        guild = self.get_guild(data.guild_id)
        if not guild:
            return {
                "member_count": 69,
                "name": "Unbekannt"
            }

        return {
            "member_count": guild.member_count,
            "name": guild.name,
        }

    @Server.route()
    async def check_perms(self, data: ClientPayload):
        guild = self.get_guild(data.guild_id)
        if not guild:
            return {"perms": False}

        member = guild.get_member(int(data.user_id))
        if not member or not member.guild_permissions.administrator:
            return {"perms": False}

        return {"perms": True}

    async def on_ipc_error(self, endpoint: str, exc: Exception) -> None:
        raise exc

def kill_old_instances():
    """Tuer les anciennes instances du bot pour éviter les conflits."""
    current_process = psutil.Process()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == current_process.name() or proc.info['cmdline'] == current_process.cmdline():
            if proc.pid != current_process.pid and 'bot' in proc.info['cmdline']:
                proc.kill()

def install_modules(modules):
    """Installer les modules requis."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", *modules])

if __name__ == "__main__":
    kill_old_instances()
    required_modules = ['PyNaCl', 'html5lib', 'lxml', 'aiofiles', 'discord', 'beautifulsoup4', 'black']
    install_modules(required_modules)

    bot = Bot()
    bot.run(token)