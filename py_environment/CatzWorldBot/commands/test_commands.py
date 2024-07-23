import discord
from discord.ext import commands
from typing import Dict, Callable
from cat_library.discord_helper import new_commands

class TestCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @new_commands({
        'name': 'hellotest',
        'help': 'hello commands',
        'actions': {
            'send_message': 'yo {user.mention}',
            'send_embed': {
                'author': '{user.name}',
                'author_url': '{avatar}',
                'title': 'title',
                'description': 'description',
                'add_field': {
                    'title': 'gros gg',
                    'description': 'gg',
                    'inline': True
                }
            }
        }
    })
    async def hellotest(self, ctx):  # Function to be called
        pass

async def setup(bot):
    cog = TestCommands(bot)
    await bot.add_cog(cog)
