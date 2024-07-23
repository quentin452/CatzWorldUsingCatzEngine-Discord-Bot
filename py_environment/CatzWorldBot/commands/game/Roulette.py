import discord
from discord.ext import commands
import random

class Roulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Define the roulette wheel with numbers and colors
        self.wheel = {
            0: "Green",
            1: "Red", 2: "Black", 3: "Red", 4: "Black", 5: "Red", 6: "Black", 7: "Red", 8: "Black", 9: "Red",
            10: "Black", 11: "Red", 12: "Black", 13: "Red", 14: "Black", 15: "Red", 16: "Black", 17: "Red", 18: "Black",
            19: "Red", 20: "Black", 21: "Red", 22: "Black", 23: "Red", 24: "Black", 25: "Red", 26: "Black", 27: "Red", 
            28: "Black", 29: "Red", 30: "Black", 31: "Red", 32: "Black", 33: "Red", 34: "Black", 35: "Red", 36: "Black"
        }

    @commands.command()
    async def roulette(self, ctx, bet: str = None, amount: int = None):
        if bet is None or amount is None:
            # Provide the rules and example if no bet or amount is provided
            rules = (
                "Roulette Game Rules:\n"
                "- Bet on a color (`red`, `black`, or `green`) or a specific number (0-36).\n"
                "- If you bet on a color and the wheel lands on that color, you win twice your bet amount.\n"
                "- If you bet on a number and the wheel lands on that number, you win 36 times your bet amount.\n"
                "- If you lose, you lose the amount you bet.\n\n"
                "Example:\n"
                "`/roulette red 100` - Bet 100 on red.\n"
                "`/roulette 17 50` - Bet 50 on the number 17."
            )
            await ctx.send(rules)
            return

        if bet.lower() not in ["red", "black", "green"] and not bet.isdigit():
            await ctx.send("Invalid bet. Please bet on 'red', 'black', 'green', or a number between 0 and 36.")
            return
        
        if amount <= 0:
            await ctx.send("Invalid amount. Please bet a positive amount.")
            return

        # Spin the wheel
        number = random.randint(0, 36)
        color = self.wheel[number]
        
        # Determine if the user won or lost
        if bet.lower() == color.lower():
            result = "win"
            payout = amount * 2
        elif bet.isdigit() and int(bet) == number:
            result = "win"
            payout = amount * 36
        else:
            result = "lose"
            payout = 0

        # Send the result message
        if result == "win":
            await ctx.send(f"The wheel landed on {number} {color}. Congratulations {ctx.author.mention}, you won {payout}!")
        else:
            await ctx.send(f"The wheel landed on {number} {color}. Sorry {ctx.author.mention}, you lost {amount}.")

async def setup(bot):
    await bot.add_cog(Roulette(bot))
