import discord
from discord.ext import commands
import json
from datetime import datetime

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
            json.dump(self.feedbacks, f, default=str)  # Serialize datetime objects to ISO format

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_feedback_channel(self, ctx):
        self.feedback_channel_id = ctx.channel.id
        self.save_feedback_channel_id()
        await ctx.send(f"Feedback channel set to {ctx.channel.mention}")

    @commands.command()
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

        await ctx.send(f"Feedback submitted by {ctx.author.mention}:\n{feedback}")

    @commands.command()
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

async def setup(bot):
    await bot.add_cog(FeedbackCommands(bot))