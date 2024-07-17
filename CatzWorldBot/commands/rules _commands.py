import discord
from discord.ext import commands
import asyncio
from utils.Constants import ConstantsClass

class RulesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.command(help = "give server rules")
    async def rules_cat(self, ctx):
        # Define the embed content
        embed = discord.Embed(
            title="Server Rules",
            description=(
                "## General Server Rules**\n"
                "• No blank, inappropriate, sexually explicit, or offensive nicknames.\n"
                "• No unreadable Unicode nicknames.\n"
                "• No blank, inappropriate, sexually explicit, or offensive profile pictures.\n"
                "• No members under 18 years old.\n"
                "• Moderators may use their discretion regardless of the rules.\n"
                "• Report any rule loopholes.\n\n"
                "## Text Chat Rules**\n"
                "• No questioning or @mentioning mods (use ⁠💥-issues-💥 for support).\n"
                "• No @everyone/@here without permission.\n"
                "• No @mentioning spam.\n"
                "• No NSFW content.\n"
                "• No personal information sharing.\n"
                "• No personal attacks, witch hunting, harassment, sexism, racism, hate speech, or offensive language.\n"
                "• No spamming or excessive messaging.\n"
                "• No walls of text or overusing emojis/reactions.\n"
                "• Keep conversations in English.\n"
                "• Moderators can delete or edit posts.\n"
                "• Use allowed bot commands only.\n"
                "• No channel hopping.\n"
                "• Stay on-topic.\n\n"
                "## Voice Chat Rules**\n"
                "• No channel hopping.\n"
                "• No annoying, loud, or high-pitched noises.\n"
                "• Minimize background noise.\n"
                "• Moderators may disconnect for poor sound quality.\n"
                "• Moderators can disconnect, mute, deafen, or move members.\n\n"
                "## Bot Specific Rules**\n"
                "• No command spam.\n"
                "• Use bot commands only in ⁠🤖-bot-🤖.\n\n"
            ),
            color=discord.Color.blue(),
            footer_text="Please click on '✅' to access the rest of the server (by clicking, you agree to follow ALL the rules mentioned above)."
        )
        
        # Send the embed
        message = await ctx.send(embed=embed)
        
        # Add reaction to the message
        await message.add_reaction("✅")
        
        # Define a check for the reaction
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '✅' and reaction.message == message
        
        # Wait for the reaction
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("You didn't react in time.")
            return
        
        # Grant a role upon reacting with '✅'
        role = discord.utils.get(ctx.guild.roles, name=ConstantsClass.VERIFIED_ROLE_NAME)
        if role:
            try:
                await ctx.author.add_roles(role)
                await ctx.send(f"Role {role.name} added to {ctx.author.display_name}")
            except discord.Forbidden:
                await ctx.send("I don't have permission to add roles.")
            except discord.HTTPException:
                await ctx.send("Failed to add role.")
        else:
            await ctx.send("Role not found.")

async def setup(bot):
    await bot.add_cog(RulesCog(bot))