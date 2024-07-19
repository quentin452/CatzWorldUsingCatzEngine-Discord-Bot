import discord
from discord.ext import commands
import random
import asyncio

class EmojiGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_list = [
            # Faces
            "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇",
            "🙂", "🙃", "😉", "😍", "🥰", "😘", "😗", "😙", "😚", "😋",
            "😜", "😝", "😛", "🤪", "😎", "🤓", "😒", "😞", "😔", "😟",
            "😕", "🙁", "☹️", "😣", "😖", "😫", "😩", "😤", "😠", "😡",
            "🤬", "😈", "👿", "💀", "☠️", "💩", "🤯", "😳", "🥺", "😦",
            "😧", "😮", "😲", "😱", "😨", "😰", "😥", "😢", "😭", "😓",
            "😪", "😵", "🤤", "😴", "🥱", "😵‍💫", "😷", "🤒",

            # Objects
            "💡", "🔦", "🏮", "🕯", "🧨", "🎉", "🎊", "🎈", "🎁", "🎗",
            "🎫", "🔮", "🧩", "🧸", "🧵", "🧶", "🎨", "🖼", "🖌", "🖍",
            "📝", "✏️", "✒️", "🔍", "🔎", "🔬", "🔭", "📡", "💻", "🖥",
            "🖨", "⌨️", "🖱", "🖲", "🕹", "🗜", "💽", "🧮", "📱", "📲",
            "☎️", "📞", "📟", "📠", "🔋", "🔌", "💳", "💎", "⚗️", "🔑",

            # Food
            "🍎", "🍏", "🍐", "🍑", "🍒", "🍓", "🫐", "🍆", "🍉", "🍊",
            "🍋", "🍌", "🍍", "🥭", "🍔", "🍟", "🍕", "🌭", "🌮", "🌯",
            "🥙", "🥪", "🍲", "🍛", "🍜", "🍝", "🍠", "🍢", "🍡", "🍧",
            "🍨", "🍦", "🍰", "🎂", "🧁", "🍮", "🍭", "🍬", "🍫", "🍪",
            "🍩", "🍿", "🥤", "🥛", "🧃", "🍺", "🍻", "🥂", "🍷", "🥃",
            "🍸", "🍹", "🍾", "🥄", "🍴", "🍽", "🥢",

            # Activities
            "⚽", "🏀", "🏈", "⚾", "🎾", "🏐", "🏉", "🎱", "🎳", "🥅",
            "🥋", "🎽", "⛷", "🏂", "🏌️‍♂️", "🏌️‍♀️", "🏄‍♂️", "🏄‍♀️", "🚣‍♂️", "🚣‍♀️",
            "🏊‍♂️", "🏊‍♀️", "🤽‍♂️", "🤽‍♀️", "⛹️‍♂️", "⛹️‍♀️", "🧗‍♂️", "🧗‍♀️", "🚴‍♂️", "🚴‍♀️",
            "🚵‍♂️", "🚵‍♀️", "🤸‍♂️", "🤸‍♀️", "🤺", "🤾‍♂️", "🤾‍♀️", "🏇", "🧘‍♂️",
            "🧘‍♀️", "🧎‍♂️", "🧎‍♀️", "🧘", "🤹‍♂️", "🤹‍♀️", "🎪", "🎭", "🎨", "🖼",

            # Symbols
            "❤️", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍", "💔",
            "❌", "⭕", "✅", "🔶", "🔷", "🔸", "🔹", "🔴", "🔵", "🟠",
            "🟢", "🟣", "🟤", "⚪", "⚫", "🔺", "🔻", "💯", "🔢", "🔣",
            "🔤", "🆎", "🆑", "🔠", "🔡", "🔢", "🔣", "🔤", "🆕", "🆖",
            "🆗", "🆘", "🆙", "🆚", "🆓", "💡", "🔋", "🔌", "📶", "📱",
            "📲", "☎️", "📞", "📟", "📠", "🔒", "🔓", "🔐", "🔑", "🔏",
            "🔎", "🔍", "🕯",

            # Nature
            "🌳", "🌲", "🌴", "🌵", "🌾", "🌿", "☘️", "🍀", "🌱", "🌺",
            "🌻", "🌼", "🌷", "🌸", "🌹", "🥀", "🍁", "🌾", "🌿", "🍀"
        ]
        self.active_games = {}

    @commands.command()
    async def emojigame(self, ctx):
        # Check if there is an active game for this user
        if ctx.author.id in self.active_games and self.active_games[ctx.author.id]:
            await ctx.send("You already have an active game. Please finish it before starting a new one.")
            return
        
        # Mark the game as active for this user
        self.active_games[ctx.author.id] = True
        
        # Choose a random emoji
        chosen_emoji = random.choice(self.emoji_list)
        
        # Send a message with the emoji to guess
        await ctx.send(f"Guess this emoji by reacting with it: {chosen_emoji}")

        # Define the reaction check function
        def check(reaction, user):
            return str(reaction.emoji) == chosen_emoji and not user.bot

        try:
            # Wait for a reaction from a player
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

            if user:
                await ctx.send(f"Congratulations {user.mention}! You guessed the correct emoji!")
            else:
                await ctx.send(f"Sorry, no one guessed the correct emoji. The right emoji was {chosen_emoji}.")
                
        except asyncio.TimeoutError:
            await ctx.send(f"Time's up. The correct emoji was {chosen_emoji}.")

        # Mark the game as inactive for this user
        self.active_games[ctx.author.id] = False

# Ensure the bot is configured to add cogs
async def setup(bot):
    await bot.add_cog(EmojiGame(bot))
