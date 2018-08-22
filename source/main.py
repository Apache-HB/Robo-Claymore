import json
import os
import sys
import traceback
from glob import glob
from shutil import copyfile

import discord
from discord.ext import commands

from cogs.utils.checks import can_override
from cogs.utils.shortcuts import quick_embed

logs = open('cogs/store/claymore.log', 'a')

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
            'key': input('Enter wolfram-alpha key (optional)')
        },
        'count': 0
    }
    json.dump(config, open('cogs/store/config.json', 'w'), indent = 4)

bot = commands.Bot(
    command_prefix = commands.when_mentioned_or(config['discord']['prefix']),
    activity = discord.Game(name = config['discord']['activity']),
    owner_id = int(config['discord']['owner'])
)

__version__ = '0.3.8'

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

ignored_errors = [
    commands.errors.CheckFailure,
    commands.errors.CommandNotFound
]

@bot.event
async def on_command_error(ctx, exception):
    if any(isinstance(exception, err) for err in ignored_errors):
        return

    if isinstance(exception, commands.errors.MissingRequiredArgument):
        embed = quick_embed(ctx, title = 'Incorrect command usage', description = f'When using command {ctx.command.name}')
        embed.add_field(name = 'The correct usage is', value = ctx.command.signature)
        return await ctx.send(embed = embed)

    elif isinstance(exception, commands.CommandInvokeError):
        if 'Cannot connect to host' in str(exception.original):#there must be a better way of checking error types
            return await ctx.send('My internet connection to that site has been blocked')

    elif isinstance(exception, commands.errors.CommandOnCooldown):
        return await ctx.send(exception)

    traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

@bot.after_invoke
async def after_any_command(ctx):
    logs.write('{0.author.name}#{0.author.id} invoked command {0.invoked_with}\n'.format(ctx))
    logs.flush()

if __name__ == '__main__':
    for cog in glob('cogs/*.py'): #skip __init__ as its not a cog

        if cog in ['cogs/__init__.py']:
            continue

        try:
            bot.load_extension(cog.replace('/', '.')[:-3])#turn cogs/file.py info cogs.file
        except Exception as e:
            print(f'{cog} failed to load becuase: {e}')

os.makedirs('cogs/store/backup/', exist_ok = True)

#backup all the config files
for storefile in glob('cogs/store/*.json'):
    copyfile(storefile, 'cogs/store/backup/' + os.path.basename(storefile))
    print(f'Backed up {storefile}')

#no point catching exceptions here
bot.run(config['discord']['token'])
