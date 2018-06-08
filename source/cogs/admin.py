import discord
from discord.ext import commands
from .store import can_override


class Admin:
    def __init__(self, bot):
        self.bot = bot
        print('Cog {} loaded'.format(self.__class__.__name__))

    def can_kick():
        async def predicate(ctx):
            if not ctx.author.permissions_in(ctx.channel).kick_members or not can_override(ctx):
                await ctx.send('You dont have the permission to kick')
                return False
            return True
        return commands.check(predicate)

    def can_ban():
        async def predicate(ctx):
            if not ctx.author.permissions_in(ctx.channel).ban_members or not can_override(ctx):
                await ctx.send('You dont have the permission to ban')
                return False
            return True
        return commands.check(predicate)

    def manage_messages():
        async def predicate(ctx):
            if not ctx.author.permissions_in(ctx.channel).manage_messages or not can_override(ctx):
                await ctx.send('You dont have the permission to delete messages')
                return False
            return True
        return commands.check(predicate)

    def manage_nicknames():
        async def predicate(ctx):
            if not ctx.author.permissions_in(ctx.channel).manage_nicknames or not can_override(ctx):
                await ctx.send('You dont have the permission to manage nicknames')
                return False
            return True
        return commands.check(predicate)

    @commands.command(name = "kick")
    @commands.guild_only()
    @can_kick()
    async def _kick(self, ctx, user: discord.Member):
        if not can_override(ctx, user):
            return await ctx.send('I Dont want to kick that user')

        if user.id == self.bot.user.id:
            return await ctx.send('I wont kick myself')

        if user.id == ctx.author.id:
            return await ctx.send('I wont let you kick yourself')

        if user.permissions_in(ctx.channel).administrator:
            await ctx.send('I wont ban admins')

        try:
            await user.kick()
        except discord.errors.Forbidden:
            await ctx.send('I dont have the correct permissions to kick him')
        else:
            await ctx.send('So long sucker')

    @commands.command(name = "ban", aliases = ['yeet'])
    @commands.guild_only()
    @can_ban()
    async def _ban(self, ctx, user: discord.Member):
        if not can_override(ctx, user):
            return await ctx.send('I Dont want to ban that user')

        if user.id == self.bot.user.id:
            return await ctx.send('I wont kick myself')

        if user.id == ctx.author.id:
            return await ctx.send('I wont let you kick yourself')

        if user.permissions_in(ctx.channel).administrator:
            await ctx.send('I wont ban admins')

        try:
            await user.ban()
        except discord.errors.Forbidden:
            await ctx.send('I dont have the correct permissions to ban that user')
        else:
            await ctx.send('And their gone')

    @commands.command(name = "softban")
    @commands.guild_only()
    @can_kick()
    async def _softban(self, ctx, user: discord.Member):
        if not can_override(ctx, user):
            return await ctx.send('I Dont want to softban that user')

        if user.id == self.bot.user.id:
            return await ctx.send('I wont kick myself')

        if user.id == ctx.author.id:
            return await ctx.send('I wont let you kick yourself')

        if user.permissions_in(ctx.channel).administrator:
            await ctx.send('I wont ban admins')

        try:
            await user.ban()
            await asyncio.sleep(15)
            await user.unban()
            await user.send(await ctx.channel.create_invite(max_uses = 1))
        except discord.errors.Forbidden:
            await ctx.send('I dont have the permissions to do that')
        else:
            await ctx.send('their gone now')

    @commands.command(name = "clean")
    @commands.guild_only()
    @manage_messages()
    async def _clean(self, ctx, amount: int = 5):
        if not 5 <= amount <= 100:
            return await ctx.send('Amount must be between 5 and 100')

        try:
            await ctx.channel.purge(limit = amount)
        except discord.errors.Forbidden:
            await ctx.send('I dont have the permissions to delete messages')
        else:
            await ctx.send('{} messages have been purged'.format(amount))

    @commands.command(name = "massnick")
    @commands.guild_only()
    @manage_nicknames()
    async def _massnick(self, ctx, *, nickname: str):
        if not 2 <= len(nickname) <= 32:
            return await ctx.send('Nickname length must be between 2 and 32 characters')

        a = 0

        for member in ctx.guild.members:
            try:
                await member.edit(nick = nickname)
                a+=1
            except Exception:
                pass

        await ctx.send('massnicked {} users'.format(a))

def setup(bot):
    bot.add_cog(Admin(bot))