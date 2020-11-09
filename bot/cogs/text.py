from discord.channel import TextChannel
from claymore.utils import PagedEmbed
from typing import Union
from discord.ext.commands.core import group, guild_only, has_permissions
from discord import Emoji
from claymore.utils import wheel
from discord.ext.commands import command

class Text(wheel(desc = 'automatic messages')):
    def __init__(self, bot):
        super().__init__(bot)

        @bot.listen()
        async def on_message(message):
            if message.author.bot:
                return

            reacts = await self.db.reacts.find_one({ 'id': message.guild.id })

            for text, emotes in (reacts or {}).items():
                if 'id' in text:
                    continue

                if text in message.content:
                    for emote in emotes:
                        await message.add_reaction(emote)

        @bot.listen()
        async def on_member_join(member):
            if member.bot:
                return

            message = await self.db.welcome.find_one({ 'id': member.guild.id })
            if not message or not message['msg']:
                return

            await member.guild.get_channel(message['channel']).send(message['msg'].replace('$user', member.mention))

        @bot.listen()
        async def on_member_remove(member):
            if member.bot:
                return

            message = await self.db.leave.find_one({ 'id': member.guild.id })
            if not message or not message['msg']:
                return

            await member.guild.get_channel(message['channel']).send(message['msg'].replace('$user', member.mention))

    @group(
        invoke_without_command = True,
        brief = 'list all reacts',
        help = """
        // list all current autoreacts for the server
        &reacts
        """
    )
    @guild_only()
    async def reacts(self, ctx):
        async def fail():
            await ctx.send(embed = ctx.embed('no autoreacts', 'add autoreacts using `reacts add`'))

        current = await self.db.reacts.find_one({ 'id': ctx.guild.id })
        if not current:
            return await fail()

        embed = PagedEmbed('all embeds', f'`{len(current)}` total phrases')

        for phrase, emotes in current.items():
            if 'id' in phrase:
                continue

            embed.add_field(phrase, ', '.join(emotes))

        if not embed.fields:
            return await fail()

        await ctx.page_embeds(embed)

    @reacts.command(
        brief = 'add an autoreact',
        help = """
        // add a reaction for duck
        &reacts add :duck: duck

        // now every message that contains the word "duck"
        // will be reacted to with a :duck: emote
        """
    )
    async def add(self, ctx, emote: str, *, text: str):
        await self.db.reacts.update_one(
            { 'id': ctx.guild.id },
            { '$set': { 'id': ctx.guild.id }, '$addToSet': { text: emote } },
            upsert = True
        )
        await ctx.send(f'will now react to `{text}` with `{emote}`')

    @reacts.command(
        brief = 'remove an autoreact',
        aliases = [ 'delete' ],
        help = """
        // delete an autoreact based on text
        &reacts remove hello

        // any reacts associated with "hello" have been removed
        """
    )
    async def remove(self, ctx, *, text: str):
        await self.db.reacts.update_one(
            { 'id': ctx.guild.id },
            { '$set': { 'id': ctx.guild.id }, '$unset': { text: 1 } },
            upsert = True
        )
        await ctx.send(f'removed all autoreacts for `{text}`')


    @command(
        brief = 'set a welcome message',
        help = """
        // set a welcome message
        &welcome hello $user

        // $user is replaced with a user mention
        // will now post "hello @user" when a user joins
        """
    )
    @guild_only()
    async def welcome(self, ctx, *, msg: str = None):
        await self.db.welcome.update_one(
            { 'id': ctx.guild.id },
            { '$set': { 'id': ctx.guild.id, 'msg': msg, 'channel': ctx.channel.id } },
            upsert = True
        )
        await ctx.send(f'set the welcome message to `{msg}`')

    @command(
        name = 'welcome-channel',
        brief = 'set welcome message channel',
        help = """
        // set the welcome channel
        &welcome-channel #channel

        // when a user joins a welcome message will be posted in #channel 
        """
    )
    @guild_only()
    async def welcome_channel(self, ctx, chan: TextChannel = None):
        channel = chan or ctx.channel
        await self.db.welcome.update_one(
            { 'id': ctx.guild.id },
            { '$set': { 'id': ctx.guild.id, 'channel': channel.id } }
        )
        await ctx.send(f'set the welcome channel to `{channel.name}`')


    @command(
        brief = 'set a leaving message',
        help = """
        // set a leaving message
        &leave goodbye $user

        // $user is replaced with a user mention
        // will now post "goodbye @user" when a user leaves
        """
    )
    @guild_only()
    async def leave(self, ctx, *, msg: str = None):
        await self.db.leave.update_one(
            { 'id': ctx.guild.id },
            { '$set': { 'id': ctx.guild.id, 'msg': msg, 'channel': ctx.channel.id } },
            upsert = True
        )
        await ctx.send(f'set the leave message to `{msg}`')

    @command(
        name = 'leave-channel',
        brief = 'set leave message channel',
        help = """
        // set leave message channel
        &leave-channel #channel

        // when a user leaves #channel will be notified
        """
    )
    @guild_only()
    async def leave_channel(self, ctx, chan: TextChannel):
        channel = chan or ctx.channel
        await self.db.leave.update_one(
            { 'id': ctx.guild.id },
            { '$set': { 'id': ctx.guild.id, 'channel': channel.id } }
        )
        await ctx.send(f'set the leave channel to `{channel.name}`')


def setup(bot):
    bot.add_cog(Text(bot))
