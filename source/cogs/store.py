import json
import configparser

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
    
def add_guild(guild):
    pass

class Store:

    current_system = ''

    silent = False

    default_color = 0xe00b3c

    config = configparser.ConfigParser()
    config.read('./store/config.cfg')

    
