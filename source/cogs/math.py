import discord
from discord.ext import commands
from .store import pyout

import mathutils
import math

class Math:
    def __init__(self, bot):
        self.bot = bot
        print('Cog {} loaded'.format(self.__class__.__name__))

    short = "Mathmatical calculations"
    description = "For executing supported math calculations"
    hidden = True

    #@commands.command(name="")

def setup(bot):
    bot.add_cog(Math(bot))