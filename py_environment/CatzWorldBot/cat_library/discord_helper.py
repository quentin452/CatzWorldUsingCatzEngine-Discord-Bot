import discord
from discord.ext import commands
from typing import Dict, Callable

def new_commands(command_info: Dict):
    def decorator(func: Callable):
        command_name = command_info.get('name', 'default')
        command_help = command_info.get('help', 'No help available')

        async def command_callback(ctx, *args, **kwargs):
            actions = command_info.get('actions', {})
            message_content = actions.get('send_message', '').format(user=ctx.author)
            embed_info = actions.get('send_embed', {})

            if message_content:
                await ctx.send(message_content)

            if embed_info:
                embed = discord.Embed(
                    title=embed_info.get('title', 'No Title').format(user=ctx.author),
                    description=embed_info.get('description', 'No Description').format(user=ctx.author),
                    color=discord.Color.blue()
                )

                author_name = embed_info.get('author', '').format(user=ctx.author)
                author_url = embed_info.get('author_url', '').format(avatar=ctx.author.avatar_url)

                if author_name:
                    embed.set_author(name=author_name, url=author_url)

                field_info = embed_info.get('add_field', {})
                field_title = field_info.get('title', 'No Field Title')
                field_description = field_info.get('description', 'No Field Description')
                field_inline = field_info.get('inline', False)

                if field_title:
                    embed.add_field(
                        name=field_title,
                        value=field_description,
                        inline=field_inline
                    )

                await ctx.send(embed=embed)

        command_callback.__name__ = command_name
        command_callback.__doc__ = command_help

        return commands.Command(command_callback, name=command_name, help=command_help)

    return decorator
