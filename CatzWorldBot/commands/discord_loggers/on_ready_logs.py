import discord
from discord.ext import commands
import json
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import BotStartedEmbed

class OnReadyLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = self.load_log_channel()

    def save_log_channel(self, channel_id):
        with open(ConstantsClass.LOGS_SAVE_FOLDER + '/on_ready_logs.json', 'w') as f:
            json.dump({'channel_id': channel_id}, f)

    def load_log_channel(self):
        try:
            with open(ConstantsClass.LOGS_SAVE_FOLDER + '/on_ready_logs.json', 'r') as f:
                data = json.load(f)
                return data['channel_id']
        except (FileNotFoundError, KeyError):
            return None


    @commands.command(help="Sets the log channel for (Ready) logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_on_ready_logs_channel(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)
        await ctx.send(f"L'ID du canal de on_ready_logs a été mis à jour à {ctx.channel.id}")

    async def on_ready(self):
        await self.bot.wait_until_ready()  # Wait until bot is fully ready
        log_channel = self.bot.get_channel(self.log_channel_id or self.load_log_channel())  # Use loaded channel if available
        if log_channel:
            try:
                embed = BotStartedEmbed().create()
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error sending startup message: {e}")
        else:
            await LogMessageAsync.LogAsync(f"Log channel with ID {self.log_channel_id} not found.")

def setup(bot):
    bot.add_cog(OnReadyLogs(bot))