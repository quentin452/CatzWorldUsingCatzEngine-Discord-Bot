import discord
from discord.ext import commands
import json
from datetime import datetime
from utils.Constants import ConstantsClass

class FeedbackCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.feedback_channel_id = self.load_feedback_channel_id()
        self.feedback_counter = self.load_feedback_counter()
        self.feedbacks = self.load_feedbacks()

    def get_menu_view(self):
        return FeedbackCommands(self.feedbacks)
    
    def load_feedback_channel_id(self):
        try:
            with open(ConstantsClass.FEED_BACK_SAVE_FOLDER + '/feedback_channel_id.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def save_feedback_channel_id(self):
        with open(ConstantsClass.FEED_BACK_SAVE_FOLDER + '/feedback_channel_id.json', 'w') as f:
            json.dump(self.feedback_channel_id, f)

    def load_feedback_counter(self):
        try:
            with open(ConstantsClass.FEED_BACK_SAVE_FOLDER + '/feedback_counter.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return 0

    def save_feedback_counter(self):
        with open(ConstantsClass.FEED_BACK_SAVE_FOLDER + '/feedback_counter.json', 'w') as f:
            json.dump(self.feedback_counter, f)

    def save_feedbacks(self):
        with open(ConstantsClass.FEED_BACK_SAVE_FOLDER + '/feedbacks.json', 'w') as f:
            json.dump(self.feedbacks, f, default=str) 

    def load_feedbacks(self):
        try:
            with open(ConstantsClass.FEED_BACK_SAVE_FOLDER + '/feedbacks.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    @commands.command(help="Sets the current channel as the feedback channel. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_feedback_channel(self, ctx):
        self.feedback_channel_id = ctx.channel.id
        self.save_feedback_channel_id()
        await ctx.send(f"Feedback channel set to {ctx.channel.mention}")

    #@commands.command(help="Submits feedback to the configured feedback channel.")
    @discord.app_commands.command(name="submit_feedback", description="Submits feedback to the configured feedback channel.")
    async def submit_feedback(self, ctx, *, feedback):
        if not self.feedback_channel_id:
            await ctx.send("Feedback channel not set.")
            return

        feedback_entry = {
            'user': ctx.author.name,
            'feedback': feedback,
            'timestamp': datetime.utcnow().isoformat()  # Add current timestamp in ISO format
        }
        self.feedbacks.append(feedback_entry)
        self.save_feedbacks()

        # Delete the message that triggered the command (/submit_feedback)
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass  # Handle case where message is already deleted
        except discord.Forbidden:
            pass  # Handle case where bot lacks permissions to delete message

        await ctx.send(f"Feedback submitted by {ctx.author.mention}:\n{feedback}")

    @commands.command(help="Views all feedbacks that have been submitted. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def view_feedbacks(self, ctx):
        if not self.feedbacks:
            await ctx.send("No feedbacks have been submitted.")
            return
        
        feedback_list = "\n\n".join([
            f"**User:** {feedback.get('user', 'Unknown')}\n**Feedback:** {feedback.get('feedback', 'No feedback')}\n**Timestamp:** {feedback.get('timestamp', 'No timestamp')}"
            for feedback in self.feedbacks
        ])
        await ctx.send(f"**List of Feedbacks:**\n\n{feedback_list}")

    async def send_feedback_instructions(self):
        channel = self.bot.get_channel(self.feedback_channel_id)
        if channel:
            embed = discord.Embed(
                title="How to submit feedback",
                description="To submit feedback, use the command:\n\n`/submit_feedback Your feedback message here`",
                color=discord.Color.blue()
            )
            await channel.send(embed=embed)

async def setup(bot):
    feedback_cog = FeedbackCommands(bot)
    await bot.add_cog(feedback_cog)
