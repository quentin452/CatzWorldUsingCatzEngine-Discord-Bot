from discord.ext import commands

class OnMessageLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Check if the message mentions the bot
        if self.bot.user.mentioned_in(message):
            # Prepare the personalized response
            response = (
                f"Hello {message.author.mention}! I am {self.bot.user.name}, a Discord bot.\n"
                "To see the available commands, use the `/help_cat` command."
            )
            # Reply to the user's message
            await message.reply(response)

async def setup(bot):
    await bot.add_cog(OnMessageLogs(bot))
