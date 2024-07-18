from discord.ext import commands
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *
import discord
from datetime import datetime

class OnWelcomeGoodbyeLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(
            self, ConstantsClass.LOGS_SAVE_FOLDER + '/on_member_join_goodbye_logs.json', 'on_member_join_goodbye_logs'
        )
        
    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(
            self, ConstantsClass.LOGS_SAVE_FOLDER + '/on_member_join_goodbye_logs.json', 'on_member_join_goodbye_logs', channel_id
        )
        
    async def log_member_event(self, member, embed):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging member event: {e}")

    @commands.command(help="Sets the log channel for (Goodbye/Welcome Message) logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_welcome_goodbye_logs_channel(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)
        await ctx.send(f"L'ID du canal de welcome_goodbye_logs a été mis à jour à {ctx.channel.id}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        server = member.guild  # get the server (guild) from the member
        embed = MemberLeftEmbed(member, server).create()
        await self.log_member_event(member, embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        server = member.guild  # get the server (guild) from the member
        
        # Fetch the role by name
        role = discord.utils.get(server.roles, name=ConstantsClass.MEMBER_ROLE_NAME)
        
        if role:
            try:
                await member.add_roles(role)
                await LogMessageAsync.LogAsync(f"Added role {role.name} to {member.name}")
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Failed to add role {role.name} to {member.name}: {e}")
        else:
            await LogMessageAsync.LogAsync(f"Role with name {ConstantsClass.MEMBER_ROLE_NAME} not found")
        
        embed = MemberJoinedEmbed(member, server).create()  # pass the server as an argument
        await self.log_member_event(member, embed)

    @commands.command(help="Simulates a member joining the server.")
    @commands.has_permissions(administrator=True)
    async def simulate_join(self, ctx, member: commands.MemberConverter):
        server = ctx.guild  # get the server (guild) from the context
        embed = MemberJoinedEmbed(member, server).create()  # pass the server as an argument
        await self.log_member_event(member, embed)
        await ctx.send(f"Simulated member join for {member.display_name}")

    @commands.command(help="Simulates a member leaving the server.")
    @commands.has_permissions(administrator=True)
    async def simulate_leave(self, ctx, member: commands.MemberConverter):
        server = ctx.guild  # get the server (guild) from the context
        embed = MemberLeftEmbed(member, server).create()
        await self.log_member_event(member, embed)
        await ctx.send(f"Simulated member leave for {member.display_name}")

def setup(bot):
    bot.add_cog(OnWelcomeGoodbyeLogs(bot))