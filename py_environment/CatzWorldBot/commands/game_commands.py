from discord.ext import commands, tasks
import discord
from utils.Constants import ConstantsClass

class GamesCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = ConstantsClass.load_channel_template(self, ConstantsClass.GAME_INFO_SAVE_FOLDER + '/game_info_channel.json', 'game_info_channel')
        self.check_channel.start()

    def cog_unload(self):
        self.check_channel.cancel()

    @tasks.loop(minutes=4)
    async def check_channel(self):
        self.channel = ConstantsClass.load_channel_template(self, ConstantsClass.GAME_INFO_SAVE_FOLDER + '/game_info_channel.json', 'game_info_channel')
        channel = self.bot.get_channel(self.channel)
        if channel:
            async for message in channel.history(limit=1):
                last_message = message
                if not last_message.embeds or (last_message.components and not isinstance(last_message.components[0], discord.ui.View)):
                    ctx = await self.bot.get_context(last_message)
                    await self.bot.get_command('games').invoke(ctx)
                break

    @check_channel.before_loop
    async def before_check_channel(self):
        await self.bot.wait_until_ready()

    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self, ConstantsClass.GAME_INFO_SAVE_FOLDER + '/game_info_channel.json', 'game_info_channel', channel_id)

    @commands.command(help="Displays a list of all available games.")
    async def games(self, ctx):
        embed = discord.Embed(
            title="🎮 Available Games 🎮",
            description="Here are the games you can play with this bot:",
            color=discord.Color.green()
        )

        games = [
            ("Rock, Paper, Scissors", "✊🖐✌️", "/rps"),
            ("Tic Tac Toe", "⭕❌", "/ttt"),
            ("Emoji Game", "😍🔥🥺", "/emojigame"),
            ("Roulette", "🔴⚫🟢", "/roulette"),
            ("Scrambled Words", "🧠✏️🔤", "/scramble")
        ]

        for game_name, emoji, command in games:
            embed.add_field(
                name=f"{emoji} {game_name}",
                value=f"Command: `{command}`",
                inline=False
            )

        await ctx.send(embed=embed)
        self.save_log_channel(ctx.channel.id)

    @commands.command(help="Set the channel for game info updates.")
    @commands.has_permissions(administrator=True)  # Ensure only admins can use this command
    async def set_game_channel(self, ctx): # TODO NOT DOCUMMENTED IN README.md
        self.save_log_channel(ctx.channel.id)
        self.channel = ctx.channel.id
        await ctx.send(f"Game info channel has been set to {ctx.channel.mention}")


# Registering the cog with the bot
async def setup(bot):
    await bot.add_cog(GamesCommandCog(bot))