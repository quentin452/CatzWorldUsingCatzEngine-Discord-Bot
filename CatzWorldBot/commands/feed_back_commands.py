import discord
from discord.ext import commands
import json
from discord import ui

class FeedbackCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.feedback_channel_id = self.load_feedback_channel_id()
        self.feedback_counter = self.load_feedback_counter()
        self.feedbacks = self.load_feedbacks()

    def load_feedback_channel_id(self):
        try:
            with open('feedback_channel_id.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def save_feedback_channel_id(self):
        with open('feedback_channel_id.json', 'w') as f:
            json.dump(self.feedback_channel_id, f)

    def load_feedback_counter(self):
        try:
            with open('feedback_counter.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return 0

    def save_feedback_counter(self):
        with open('feedback_counter.json', 'w') as f:
            json.dump(self.feedback_counter, f)

    def load_feedbacks(self):
        try:
            with open('feedbacks.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_feedbacks(self):
        with open('feedbacks.json', 'w') as f:
            json.dump(self.feedbacks, f)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_feedback_channel(self, ctx):
        self.feedback_channel_id = ctx.channel.id
        self.save_feedback_channel_id()
        embed = discord.Embed(
            title="Submit a Report",
            description="If you want to submit a report,\nthen press the button below!\n\nTo submit a report, press the button.",
            color=discord.Color.green()
        )
        view = FeedbackView(self)
        await ctx.send(embed=embed, view=view)
        await ctx.send(f"Feedback channel set to {ctx.channel.mention}")

    @commands.command()
    async def submit_feedback(self, ctx, *, feedback):
        if not self.feedback_channel_id:
            await ctx.send("Feedback channel not set.")
            return

        guild = ctx.guild
        self.feedback_counter += 1
        self.save_feedback_counter()

        feedback_channel = await guild.create_text_channel(f'feedback-{self.feedback_counter}')
        await feedback_channel.set_permissions(guild.default_role, read_messages=False)
        await feedback_channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
        for role in guild.roles:
            if role.permissions.administrator:
                await feedback_channel.set_permissions(role, read_messages=True, send_messages=True)

        feedback_entry = {
            'feedback_id': self.feedback_counter,
            'user_id': ctx.author.id,
            'feedback': feedback,
            'channel_id': feedback_channel.id
        }
        self.feedbacks.append(feedback_entry)
        self.save_feedbacks()

        feedback_embed = discord.Embed(title=f"Feedback #{self.feedback_counter}", description=feedback, color=discord.Color.green())
        feedback_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        await feedback_channel.send(embed=feedback_embed)
        await ctx.send(f"Feedback #{self.feedback_counter} created. You can view it in {feedback_channel.mention}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def close_feedback(self, ctx, feedback_id: int):
        feedback = next((f for f in self.feedbacks if f['feedback_id'] == feedback_id), None)
        if not feedback:
            await ctx.send(f"No feedback found with ID {feedback_id}.")
            return

        channel = self.bot.get_channel(feedback['channel_id'])
        if channel:
            await channel.delete()

        self.feedbacks = [f for f in self.feedbacks if f['feedback_id'] != feedback_id]
        self.save_feedbacks()
        await ctx.send(f"Feedback #{feedback_id} closed and deleted.")

class FeedbackView(ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    @ui.button(label="Submit a Report", style=discord.ButtonStyle.primary)
    async def submit_feedback_button(self, interaction: discord.Interaction,button: ui.Button):
        await interaction.response.send_message("Button Clicked!", ephemeral=True)

class SubmitFeedbackModal(ui.Modal):
    def __init__(self, cog):
        super().__init__(title="Submit a Report")
        self.cog = cog
        self.add_item(ui.TextInput(label="Feedback", style=discord.TextInputStyle.paragraph))

    async def callback(self, interaction: discord.Interaction):
        feedback = self.children[0].value
        ctx = await self.cog.bot.get_context(interaction.message)
        await self.cog.submit_feedback(ctx, feedback=feedback)

async def setup(bot):
    await bot.add_cog(FeedbackCommands(bot))