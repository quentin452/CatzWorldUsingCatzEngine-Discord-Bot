import discord
from discord.ext import commands

# Define your intents
intents = discord.Intents.default()
intents.messages = True  # Enable the intent for receiving message events

token_file = 'token.txt'

# Pass intents parameter when creating the bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Nous nous sommes connectés en tant que {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Bonjour!')

# Read token from file
with open(token_file, 'r') as f:
    token = f.read().strip()

bot.run(token)