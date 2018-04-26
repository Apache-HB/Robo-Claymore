import json

import sys
import os

import discord

#for embed checking
import urllib
from mimetypes import MimeTypes

#keep this file as minimal as possible

def style_embed(ctx, title: str, description: str='', color: int=None):
    if color is None:
        try: color = ctx.guild.me.color
        except AttributeError: color = Store.default_color
    embed=discord.Embed(title=title, description=description,color=color)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    return embed


def pyout(message: str):
    if not Store.silent: 
        print(message)
    return Store.silent
    
def qlog(message: str):
    f = open('cogs/store/direct.log', 'a')
    f.write(message)
    f.close()

def add_guild(guild):
    pass

class Store:

    total_messages = 0

    current_system = ''

    silent = False

    default_color = 0xe00b3c

    frames = []

    config = json.load(open('cogs/store/config.json'))

    whitelist = json.load(open('cogs/store/whitelist.json'))

    blacklist = json.load(open('cogs/store/blacklist.json'))

    
