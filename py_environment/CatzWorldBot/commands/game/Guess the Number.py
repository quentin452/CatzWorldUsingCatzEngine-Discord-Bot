import discord
from discord.ext import commands
from discord.ui import Button, View
import random

class GuessTheNumberGame:
    def __init__(self, host, num_lines):
        self.host = host
        self.number = random.randint(1, 100)
        self.finished = False
        self.winner = None
        self.attempts = 0
        self.num_lines = num_lines

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
        total_buttons = 5 * self.game.num_lines
        if total_buttons > 25:
            total_buttons = 25
        numbers = random.sample(range(1, 101), total_buttons)
        if self.game.number not in numbers:
            numbers[random.randint(0, total_buttons - 1)] = self.game.number

        for i in range(total_buttons):
            button_number = numbers[i]
            button = Button(label=str(button_number), style=discord.ButtonStyle.secondary, row=i // 5)
            button.callback = self.create_callback(button_number)
            self.add_item(button)

        quit_button = Button(label="Quitter", style=discord.ButtonStyle.danger, row=total_buttons // 5)
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
                embed.title = "Congratulations!"
                embed.description = f"{self.game.winner.mention} won the game in {self.game.attempts} attempts!"
                embed.color = discord.Color.green()
                await interaction.message.edit(embed=embed, view=self)
                self.stop()
            else:
                embed.description = f"Guess the hidden number:\n\n{result}\n\nAttempts: {self.game.attempts}\nUse the buttons below to make your guess."
                await interaction.message.edit(embed=embed, view=self)

            await interaction.response.defer()  # Explicitly acknowledge the interaction
        return callback

    def quit_callback(self, interaction: discord.Interaction):
        if self.game.finished:
            return  # Game is already finished
        
        self.game.finished = True  # Mark game as finished
        for child in self.children:
            child.disabled = True  # Disable all buttons
        
        embed = interaction.message.embeds[0]
        embed.title = "Game Ended"
        embed.description = f"{interaction.user.mention} has quit the game."
        embed.color = discord.Color.red()
        
        self.stop()  # Stop the view
        
        # Update the message
        async def update_message():
            await interaction.message.edit(embed=embed, view=self)
        
        self.bot.loop.create_task(update_message())  # Ensure the message is updated asynchronously

class GuessTheNumberCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @commands.command(help="Start a Guess the Number game with a specified number of lines.")
    async def guess(self, ctx, num_lines: int = None):
        if num_lines is None:
            await ctx.send(
                "Welcome to the Guess the Number game!\n"
                "To start a game, use the command `!guess <number_of_lines>` where `<number_of_lines>` is between 1 and 4.\n"
                "Example: `!guess 2` to play with 2 lines.\n\n"
                "In the game, you will be presented with buttons. Click on a button to make a guess. The game will tell you if the number is higher or lower.\n"
                "You can also click 'Quitter' to end the game early."
            )
            return

        if num_lines < 1 or num_lines > 4:
            await ctx.send("Please specify a number between 1 and 4 for the number of lines.")
            return

        if ctx.author in self.active_games:
            game = self.active_games[ctx.author]
            if game.finished:
                del self.active_games[ctx.author]
                game = GuessTheNumberGame(ctx.author, num_lines)
                self.active_games[ctx.author] = game
                await ctx.send("Your previous game ended. Starting a new game!")
            else:
                await ctx.send("You already have an active game.")
                return
        else:
            game = GuessTheNumberGame(ctx.author, num_lines)
            self.active_games[ctx.author] = game

        def quit_callback(interaction: discord.Interaction):
            if ctx.author in self.active_games:
                del self.active_games[ctx.author]
            for child in view.children:
                child.disabled = True
            embed = discord.Embed(
                title="Game Ended",
                description=f"{ctx.author.mention} has quit the game.",
                color=discord.Color.red()
            )
            view.stop()
            async def update_message():
                await interaction.message.edit(embed=embed, view=view)
            self.bot.loop.create_task(update_message())

        view = GuessTheNumberView(game, quit_callback)
        embed = discord.Embed(
            title="Guess the Number Game!",
            description="Try to guess the hidden number by clicking on the buttons below.",
            color=discord.Color.blue()
        )
        message = await ctx.send(embed=embed, view=view)
        view.message = message

async def setup(bot):
    await bot.add_cog(GuessTheNumberCommands(bot))
