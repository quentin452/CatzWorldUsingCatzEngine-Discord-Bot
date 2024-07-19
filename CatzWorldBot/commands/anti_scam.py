from discord.ext import commands
import discord
import re
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync

# Liste des mots-clés de phishing/scam
phishing_keywords = ["free", "win", "giveaway", "click here", "visit", "congratulations", "claim", "prize"]

# Regex pour détecter les URL
phishing_regex = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')

# Regex pour les URL suspectes, incluant Discord avec différentes variantes de protocoles et sans protocole
suspicious_regex = re.compile(r'(https?://|http://|www\.)?(discord\.gg|discord\.com)')

# Regex pour les URL à exclure des vérifications (YouTube, Google, etc.)
whitelist_regex = re.compile(r'https?://(?:www\.)?(youtube\.com|youtu\.be|google\.com|docs\.google\.com|drive\.google\.com|imgur\.com|printscreen\.com|prntscr\.com|flickr\.com)')

class AntiScam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Vérifiez les messages de l'utilisateur cible
        # if message.author.id == ConstantsClass.IAMACAT_USER_ID:
        # Vérification des mots-clés
        if any(keyword in message.content.lower() for keyword in phishing_keywords):
            try:
                # Supprime le message
                await message.delete()

                # Envoie un message en MP à l'utilisateur
                user = message.author
                try:
                    await user.send("Votre message a été supprimé car il pourrait contenir du contenu de phishing ou de scam.")
                except discord.Forbidden:
                    # Le bot n'a pas la permission d'envoyer des MP à cet utilisateur
                    await LogMessageAsync.LogAsync("Le bot n'a pas les permissions nécessaires pour envoyer des messages privés à l'utilisateur.")
                    
            except discord.Forbidden:
                await LogMessageAsync.LogAsync("Le bot n'a pas les permissions nécessaires pour supprimer les messages.")
            except discord.HTTPException as e:
                await LogMessageAsync.LogAsync(f"Une erreur est survenue en essayant de supprimer le message: {e}")
            
            # Vérification des liens URL
        elif phishing_regex.search(message.content) and not whitelist_regex.search(message.content):
            try:
                # Supprime le message
                await message.delete()

                # Envoie un message en MP à l'utilisateur
                user = message.author
                try:
                    await user.send("Votre message a été supprimé car il pourrait contenir du contenu de phishing ou de scam.")
                except discord.Forbidden:
                    # Le bot n'a pas la permission d'envoyer des MP à cet utilisateur
                    await LogMessageAsync.LogAsync("Le bot n'a pas les permissions nécessaires pour envoyer des messages privés à l'utilisateur.")
                    
                # Optionnel : Envoie également un message dans le canal où le message a été supprimé
                if isinstance(message.channel, discord.DMChannel):
                    # Message en MP
                    await message.channel.send(f'{message.author.mention}, votre message a été supprimé car il pourrait contenir du contenu de phishing ou de scam.')
                else:
                    # Message dans le canal
                    await message.channel.send(f'{message.author.mention}, votre message a été supprimé car il pourrait contenir du contenu de phishing ou de scam.')
                    
            except discord.Forbidden:
                await LogMessageAsync.LogAsync("Le bot n'a pas les permissions nécessaires pour supprimer les messages.")
            except discord.HTTPException as e:
                await LogMessageAsync.LogAsync(f"Une erreur est survenue en essayant de supprimer le message: {e}")

        # Vérification spécifique des liens Discord (à marquer comme suspects)
        elif suspicious_regex.search(message.content):
            try:
                # Marquer le message comme suspect
                # (Vous pouvez ajouter un rôle, envoyer un message d'alerte ou tout autre traitement ici)
                await message.delete()
                # Envoie un message en MP à l'utilisateur
                user = message.author
                try:
                    await user.send("Votre message contient un lien Discord, ce qui peut être suspect. Veuillez vérifier le contenu.")
                except discord.Forbidden:
                    # Le bot n'a pas la permission d'envoyer des MP à cet utilisateur
                    await LogMessageAsync.LogAsync("Le bot n'a pas les permissions nécessaires pour envoyer des messages privés à l'utilisateur.")
                    
                # Optionnel : Envoie également un message dans le canal où le message a été marqué comme suspect
                if isinstance(message.channel, discord.DMChannel):
                    # Message en MP
                    await message.channel.send(f'{message.author.mention}, votre message contient un lien Discord, ce qui peut être suspect.')
                else:
                    # Message dans le canal
                    await message.channel.send(f'{message.author.mention}, votre message contient un lien Discord, ce qui peut être suspect.')
                    
            except discord.Forbidden:
                await LogMessageAsync.LogAsync("Le bot n'a pas les permissions nécessaires pour envoyer des messages.")
            except discord.HTTPException as e:
                await LogMessageAsync.LogAsync(f"Une erreur est survenue en essayant de traiter le message: {e}")

        # Note: ne pas oublier de faire passer les commandes
        await self.bot.process_commands(message)
        # else:
        # Si le message provient d'un autre utilisateur, continuez à traiter les autres événements/messages
        # await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(AntiScam(bot))
