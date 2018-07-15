import discord
from discord.ext import commands
import json
from glob import glob
import aiohttp
import traceback
import sys
from cogs.store import (whitelist,
blacklist, quick_embed,
logs, only_mentions_bot)
import asyncio

primed = False

try:
    config = json.load(open('cogs/store/config.json'))
except FileNotFoundError:
    print('The config file was not found, let me run the setup')
    config = {
        'discord': {
            'token': input('Enter bot token'),
            'prefix': input('Enter bot prefix'),
            'activity': input('Enter default bot activity'),
            'owner': input('Enter the owners id')
        },
        'wolfram': {
            'key': input('Enter wolfram alpha key (optional)')
        }
    }
    json.dump(config, open('cogs/store/config.json', 'w'), indent = 4)

bot = commands.Bot(
    command_prefix = commands.when_mentioned_or(config['discord']['prefix']),
    activity = discord.Game(name = config['discord']['activity']),
    owner_id = int(config['discord']['owner'])
)

#get rid of the help command to allow for a custom one
bot.remove_command('help')

__version__ = '0.2.0'

@bot.event
async def on_ready():
    print('''
name: {0.user.name}#{0.user.discriminator}
id: {0.user.id}
invite: https://discordapp.com/oauth2/authorize?client_id={0.user.id}&scope=bot&permissions=66321471
discord.py version: {1.__version__}
bot version: {2}
bot ready'''.format(bot, discord, __version__))

@bot.event
async def on_message(context):
    await bot.process_commands(context)

@bot.event
async def on_server_join(server):
    pass

@bot.event
async def on_command_error(ctx, exception):
    if isinstance(exception, discord.ext.commands.errors.MissingRequiredArgument):
        embed = quick_embed(ctx, title = 'Incorrect command usage', description = 'When using command {}'.format(ctx.command.name))
        embed.add_field(name = 'The correct usage is', value = ctx.command.signature)
        return await ctx.send(embed = embed)

    elif isinstance(exception, discord.ext.commands.errors.CheckFailure):
        return

    elif isinstance(exception, discord.ext.commands.errors.CommandNotFound):
        return

    elif isinstance(exception, discord.ext.commands.CommandInvokeError):
        if 'Cannot connect to host' in str(exception.original):#there must be a better way of checking error types
            return await ctx.send('My internet connection to that site has been blocked')

    traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

@bot.check
async def check_commands(ctx):
    #let the bot owner and whitelisted users always override
    if await ctx.bot.is_owner(ctx.author) or ctx.author.id in whitelist:
        return True

    if ctx.author.id in blacklist:#make sure to tell blocked people to eat pant
        await ctx.send('Go away')
        return False

    if ctx.command.name.lower() in config['disabled']['commands']:
        await ctx.send('That command has been disabled globally')
        return False

    if ctx.command.name.cog_name.lower() in config['disabled']['cogs']:
        await ctx.send('That cog has been disabled globally')
        return False

    return True

@bot.after_invoke
async def after_any_command(ctx):
    logs.append('{0.author.name}#{0.author.id} invoked command {0.invoked_with}'.format(ctx))
    json.dump(logs, open('cogs/store/logs.json', 'w'), indent = 4)

    if ctx.cog.__class__.__name__ == 'Owner':#specifically log if an owner only command is used
        print('{0.author.name} tried to use {0.invoked_with}'.format(ctx))

if __name__ == '__main__':
    for cog in glob('cogs/*.py'):
        if not cog in ['cogs/__init__.py', 'cogs/store.py']:
            try:
                bot.load_extension(cog.replace('cogs/', 'cogs.').replace('.py', ''))
            except Exception as e:
                print(cog, 'failed to load becuase: ', e)

#no point catching exceptions here
bot.run(config['discord']['token'])