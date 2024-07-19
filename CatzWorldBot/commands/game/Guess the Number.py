import discord
from discord.ext import commands
from discord.ui import Button, View
import random

class GuessTheNumberGame:
    def __init__(self, host):
        self.host = host
        self.number = random.randint(1, 100)
        self.finished = False
        self.winner = None
        self.attempts = 0

    def make_guess(self, guess):
        if self.finished:
            return "The game has already ended."
        self.attempts += 1
        if guess == self.number:
            self.finished = True
            self.winner = self.host
            return f"Congratulations! You guessed the correct number in {self.attempts} attempts!"
        elif guess < self.number:
            return "The number is higher."
        else:
            return "The number is lower."

class GuessTheNumberView(View):
    def __init__(self, game, quit_callback):
        super().__init__(timeout=180)
        self.game = game
        self.quit_callback = quit_callback
        self.add_buttons()
        self.message = None

    def add_buttons(self):
        numbers = random.sample(range(1, 101), 10)
        if self.game.number not in numbers:
            numbers[random.randint(0, 9)] = self.game.number

        for i in range(10):
            button_number = numbers[i]
            button = Button(label=str(button_number), style=discord.ButtonStyle.secondary, row=i // 5)
            button.callback = self.create_callback(button_number)
            self.add_item(button)

        quit_button = Button(label="Quitter", style=discord.ButtonStyle.danger)
        quit_button.callback = self.quit_callback
        self.add_item(quit_button)

    def create_callback(self, guess):
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.game.host:
                await interaction.response.send_message("You are not allowed to guess.", ephemeral=True)
                return
            
            result = self.game.make_guess(guess)
            embed = interaction.message.embeds[0]

            if self.game.finished:
                for child in self.children:
                    child.disabled = True
                embed.title = "Game Over!"
                embed.description = f"{self.game.winner.mention} won the game in {self.game.attempts} attempts!"
                embed.color = discord.Color.green()
                await interaction.message.edit(embed=embed, view=self)
                self.stop()
            else:
                embed.description = f"Guess the hidden number:\n\n{result}\n\nAttempts: {self.game.attempts}\nUse the buttons below to make your guess."
                await interaction.message.edit(embed=embed, view=self)

            await interaction.response.defer()  # Explicitly acknowledge the interaction
        return callback

class GuessTheNumberCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @commands.command(help="Start a Guess the Number game.")
    async def guess(self, ctx):
        if ctx.author in self.active_games:
            game = self.active_games[ctx.author]
            if game.finished:
                del self.active_games[ctx.author]
                game = GuessTheNumberGame(ctx.author)
                self.active_games[ctx.author] = game
                await ctx.send("Your previous game ended. Starting a new game!")
            else:
                await ctx.send("You already have an active game.")
                return
        else:
            game = GuessTheNumberGame(ctx.author)
            self.active_games[ctx.author] = game

        async def quit_callback(interaction: discord.Interaction):
            if ctx.author in self.active_games:
                del self.active_games[ctx.author]
            for child in self.children:
                child.disabled = True
            await interaction.response.send_message(f"{ctx.author.mention} a quitté la partie.")

        view = GuessTheNumberView(game, quit_callback)
        embed = discord.Embed(
            title="Guess the Number Game!",
            description="Try to guess the hidden number by clicking on the buttons below.",
            color=discord.Color.blue()
        )
        message = await ctx.send(embed=embed, view=view)
        view.message = message

    @commands.command(help="Check the status of your active game.")
    async def game_status(self, ctx):
        if ctx.author not in self.active_games:
            await ctx.send("You don't have an active game.")
            return

        game = self.active_games[ctx.author]
        status = game.make_guess(-1)  # Pass an invalid guess to get the status
        await ctx.send(status)

async def setup(bot):
    await bot.add_cog(GuessTheNumberCommands(bot))