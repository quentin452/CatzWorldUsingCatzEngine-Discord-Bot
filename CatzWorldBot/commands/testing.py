from discord.ext import commands
import discord
from utils.async_logs import LogMessageAsync
from utils.Constants import ConstantsClass
class Testing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_member_logs.json','on_member_logs')

    @commands.command(help="Simulates a boost event for the current user. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def simulate_boost(self, ctx):
        # Replace with the member object you want to simulate boosting
        # You can use `ctx.author` to simulate your own boosting
        member = ctx.author

        # Manually call the on_member_boost event
        await self.on_member_boost(member)

    async def on_member_boost(self, member):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='Member Boosted Server',
                    description=f'{member.name}#{member.discriminator} has boosted the server!',
                    color=discord.Color.gold()
                )
                embed.set_thumbnail(url=member.avatar.url)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging member boost: {e}")

# Add this cog to your bot
def setup(bot):
    bot.add_cog(Testing(bot))
