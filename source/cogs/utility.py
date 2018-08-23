import dis
import json
import platform
import random
from datetime import datetime
from inspect import getsource
from xml.dom.minidom import parseString

import discord
from aiowolfram import Wolfram
from bs4 import BeautifulSoup as bs
from discord.ext import commands
from fuzzywuzzy import process
from pyfiglet import figlet_format

from .utils import zalgo
from .utils.checks import can_override
from .utils.networking import hastebin, hastebin_error, tinyurl, url_request
from .utils.shortcuts import embedable, quick_embed, try_file

# stolen from appuselfbot
# https://github.com/appu1232/Discord-Selfbot
emoji_dict = {
    'a': ['🇦 ', '🅰', '🍙', '🔼', '4⃣'],
    'b': ['🇧 ', '🅱', '8⃣'],
    'c': ['🇨 ', '©', '🗜'],
    'd': ['🇩 ', '↩'],
    'e': ['🇪 ', '3⃣', '📧', '💶'],
    'f': ['🇫 ', '🎏'],
    'g': ['🇬 ', '🗜', '6⃣', '9⃣', '⛽'],
    'h': ['🇭 ', '♓'],
    'i': ['🇮 ', 'ℹ', '🚹', '1⃣'],
    'j': ['🇯 ', '🗾'],
    'k': ['🇰 ', '🎋'],
    'l': ['🇱 ', '1⃣', '🇮', '👢', '💷'],
    'm': ['🇲 ', 'Ⓜ', '📉'],
    'n': ['🇳 ', '♑', '🎵'],
    'o': ['🇴 ', '🅾', '0⃣', '⭕', '🔘', '⏺', '⚪', '⚫', '🔵', '🔴', '💫'],
    'p': ['🇵 ', '🅿'],
    'q': ['🇶 ', '♌'],
    'r': ['🇷 ', '®'],
    's': ['🇸 ', '💲', '5⃣', '⚡', '💰', '💵'],
    't': ['🇹 ', '✝', '➕', '🎚', '🌴', '7⃣'],
    'u': ['🇺 ', '⛎', '🐉'],
    'v': ['🇻 ', '♈', '☑'],
    'w': ['🇼 ', '〰', '📈'],
    'x': ['🇽 ', '❎', '✖', '❌', '⚒'],
    'y': ['🇾 ', '✌', '💴'],
    'z': ['🇿 ', '2⃣'],
    '0': ['0⃣ ', '🅾', '0⃣', '⭕', '🔘', '⏺', '⚪', '⚫', '🔵', '🔴', '💫'],
    '1': ['1⃣ ', '🇮'],
    '2': ['2⃣ ', '🇿'],
    '3': ['3⃣ '],
    '4': ['4⃣ '],
    '5': ['5⃣ ', '🇸', '💲', '⚡'],
    '6': ['6⃣ '],
    '7': ['7⃣ '],
    '8': ['8⃣ ', '🎱', '🇧', '🅱'],
    '9': ['9⃣ '],
    '?': ['❓ '],
    '!': ['❗ ', '❕', '⚠', '❣'],
    ' ': ['   '],
    '\n': ['\n']
}

inverted_dict = {
    'a': 'ɐ',
    'b': 'q',
    'c': 'ɔ',
    'd': 'p',
    'e': 'ǝ',
    'f': 'ɟ',
    'g': 'ƃ',
    'h': 'ɥ',
    'i': 'ᴉ',
    'j': 'ɾ',
    'k': 'ʞ',
    'l': 'l',
    'm': 'ɯ',
    'n': 'u',
    'o': 'o',
    'p': 'd',
    'q': 'b',
    'r': 'ɹ',
    's': 's',
    't': 'ʇ',
    'u': 'n',
    'v': 'ʌ',
    'w': 'ʍ',
    'x': 'x',
    'y': 'ʎ',
    'z': 'z',
    ' ': ' ',
    '\n': '\n'
}

# wikia fandom wikis
WIKIA_STANDARD_URL = 'http://{sub_wikia}.wikia.com/wiki/{page}'
WIKIPEDIA_API_URL = 'http://en.wikipedia.org/w/api.php'

USER_AGENT = '{} (https://github.com/Apache-HB/Robo-Claymore)'

class Utility:
    def __init__(self, bot):
        self.bot = bot
        #TODO this is probably better in a dictionary
        self.config = json.load(try_file('cogs/store/config.json'))
        self.tags = json.load(try_file('cogs/store/tags.json', content = '{}'))
        self.quotes = json.load(try_file('cogs/store/quotes.json', content = '{}'))
        self.wolfram = Wolfram(self.config['wolfram']['key'])
        print(f'cog {self.__class__.__name__} loaded')

    #TODO get this to actually work and return an article
    @commands.command(name = "wikia", hidden = True)
    async def _wikia(self, ctx, sub_wiki: str, query: str):
        ret = json.loads(
            await url_request(
                url = 'http://{}.wikia.com/api/v1/Articles/Details?'.format(sub_wiki),
                params = {
                    'format': 'json',
                    'titles': search.lower()
                },
                headers = {
                    'User-Agent': USER_AGENT.format('Wikia')
                }
            )
        )
        print(json.dumps(ret, indent=4))
        await ctx.send('soon™')
        # print(search(sub_wiki, query))

    @commands.command(
        name = "bytecode",
        aliases = ['byte'],
        description = "extract the bytecode from a command and transform it into python Mnemonics",
        brief = "convert commands to bytecode"
    )
    async def _byte(self, ctx, name: str):
        command = self.bot.get_command(name)
        if command is None:
            return await ctx.send('That command does not exist')
        code = dis.Bytecode(command.callback)
        ret = ''
        for instr in code:
            ret += str(instr) + '\n'
        try:
            await ctx.send(ret)
        except discord.errors.HTTPException:
            await ctx.send(embed = await hastebin_error(ctx, ret))

    @commands.command(
        name = "zalgo",
        description = """The Nezperdian hive-mind of chaos. Zalgo.
He who Waits Behind The Wall.
ZALGO!""",
        brief = "To invoke the hive-mind representing chaos."
    )
    async def _zalgo(self, ctx, *, text: str = 'zalgo 50'):
        text = text.split(' ')
        try:
            intensity = int(text[-1])
        except Exception:
            intensity = 50
            text = ' '.join(text)
        else:
            text = ' '.join(text[:-1])

        if not 1 <= intensity <= 1000:
            return await ctx.send('Intensity must be between 1 and 1000')

        ret = await zalgo(text, intensity)

        try:
            await ctx.send(ret)
        except Exception:
            await ctx.send(embed = await hastebin_error(ctx, content = ret))

    @commands.command(
        name = "flip",
        description = "flip text upside down",
        brief = "flip text"
    )
    async def _flip(self, ctx, *, text: str):
        ret = ''
        for char in text:
            try: ret += inverted_dict[char.lower()]
            except KeyError: ret += char

        return await ctx.send(ret)

    @commands.command(
        name = "staggercase",
        description = "stagger the case of a phrase",
        brief = "StAgGeRcAsE"
    )
    async def _staggercase(self, ctx, *, text: str):
        ret = ''
        upper = True
        for char in text:
            ret += char.upper() if upper else char.lower()
            upper = not upper

        await ctx.send(ret)

    @commands.command(
        name = "tinyurl",
        description = "create a tinyurl link from a big url",
        brief = "use tinyurl"
    )
    async def _tinyurl(self, ctx, *, url: str):
        await ctx.send(await tinyurl(url))

    @commands.command(
        name = "hastebin",
        description = "upload content to hastebin to display it nicely",
        brief = "use hastebin"
    )
    async def _hastebin(self, ctx, *, content: str):
        await ctx.send(await hastebin(content))

    @commands.command(
        name = "hash",
        description = "generate a hascode from some text",
        brief = "-670075742651522359"
    )
    async def _hash(self, ctx, *, text: str):
        await ctx.send(hash(text))

    @commands.command(
        name = "reverse",
        description = "reverse the direction of the input text",
        brief = "esrever"
    )
    async def _reverse(self, ctx, *, text: str):
        await ctx.send(text[::-1])

    @commands.command(
        name = "swapcase",
        description = "swap the case of the input text",
        brief = "SWAPCASE"
    )
    async def _swapcase(self, ctx, *, text: str):
        await ctx.send(text.swapcase())

    @commands.command(
        name = "randomcase",
        description = "make the case of every character random",
        brief = "RaNDoMCaSe"
    )
    async def _randomcase(self, ctx, *, text: str):
        await ctx.send(''.join(random.choice((str.upper, str.lower))(x) for x in text))

    @commands.command(
        name = "invite",
        description = "Get an invite like to my owners discord and an invite for me",
        brief = "bring me with you"
    )
    async def _invite(self, ctx):
        ret = ''
        ret += 'Invite me with this link\n'
        ret += '<https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8>\n'.format(self.bot.user.id)
        ret += 'and join my owners discord server here\n'
        ret += 'https://discord.gg/y3uSzCK'
        await ctx.send(ret)

    @commands.command(
        name = "remindme",
        aliases = ['reminder', 'remind']
    )
    async def _remindme(self, ctx, hours: int, *, message: str):
        pass

    @commands.command(
        name = "expand",
        description = "expand text using figlet",
        brief = "expnad dong"
    )
    async def _expand(self, ctx, *, text: str = 'dong'):
        ret = figlet_format(text,
            font = random.choice(['big', 'starwars', 'block', 'bubble', 'cards', 'catwalk'])
        )

        if not len(ret) <= 1800:
            return await ctx.send(embed = await hastebin_error(ctx, ret))

        await ctx.send('```' + ret + '```')

    @commands.command(
        name = "emoji",
        aliases = ['emojify'],
        description = "convert text to its emoji form",
        brief = "the emoji movie, but its text"
    )
    async def _emoji(self, ctx, *, text: str = 'Bottom text'):

        ret = ''
        for a in text:
            try:
                ret += emoji_dict[a][0]
            except KeyError:
                ret += a

        if not len(ret) <= 1800:
            return await ctx.send(embed = await hastebin_error(ctx, ret))

        await ctx.send(ret)

    @commands.command(
        name = "binary",
        description = "convert text to its binary form",
        brief = "1001"
    )
    async def _binary(self, ctx, *, text: str):

        ret = ' '.join(format(ord(x), 'b') for x in text)

        if not len(ret) <= 1800:
            return await ctx.send(embed = await hastebin_error(ctx, ret))

        await ctx.send(ret)

    @commands.command(
        name = "ascii",
        description = "convert text to a list of ascii values",
        brief = "[97, 115, 99, 105, 105]"
    )
    async def _ascii(self, ctx, *, text: str):

        ret = ''.join(str([ord(c) for c in text]))

        if not len(ret) <= 1800:
            return await ctx.send(embed = await hastebin_error(ctx, ret))

        await ctx.send(ret)

    @commands.command(
        name = "square",
        description = "make the text square",
        brief = "[]"
    )
    async def _square(self, ctx, *, text: str):

        ret = text + '\n'
        for letter in text[1:]:
            ret += letter + '\n'

        if not len(ret) <= 1800:
            return await ctx.send(embed = await hastebin_error(ctx, ret))

        await ctx.send(ret)

    @commands.command(
        name = "source",
        description = "fetch the source code for any command, or get the link to my github page",
        brief = "hole lotta nerd shit"
    )
    async def _source(self, ctx, *, name: str = None):

        if name is None:
            return await ctx.send('https://github.com/Apache-HB/Robo-Claymore')

        func = ctx.bot.get_command(name)

        if func is None:
            return await ctx.send(f'No command called ``{name}`` found')

        if func.cog_name == 'Owner':
            return await ctx.send('Nice try fucko')

        ret = getsource(func.callback)

        if not len(ret) <= 1800:
            return await ctx.send(embed = await hastebin_error(ctx, ret))

        await ctx.send('```py\n' + ret.replace('`', '\`') + '```')

    @commands.command(
        name = "urban",
        description = "search the urbandisctionary for a definition",
        brief = "the most reliable definition"
    )
    async def _urban(self, ctx, *, search: str = None):

        url = 'http://api.urbandictionary.com/v0/random'

        if not search is None:
            url = 'http://api.urbandictionary.com/v0/define?term=' + search

        ret = json.loads(await url_request(url = url))

        if not ret['list']:
            return await ctx.send(f'Nothing about {search} found')

        post = random.choice(ret['list'])

        embed = quick_embed(ctx, title = f'Definition of {post["word"]}', description = f'Written by {post["author"]}')
        embed.add_field(name = 'Description', value = post['definition'])
        embed.add_field(name = 'Example', value = post['example'])
        embed.add_field(name = 'Permalink', value = post['permalink'])
        embed.set_footer(text = 'Votes: {}/{}'.format(post['thumbs_up'], post['thumbs_down']))

        await ctx.send(embed = embed)

    @commands.command(
        name = "userinfo",
        description = "get information about a user",
        brief = "who is this"
    )
    async def _userinfo(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        embed = quick_embed(ctx,
        title = 'Information about {0.name}#{0.discriminator}'.format(user),
        description = f'User ID: {user.id}')

        embed.set_thumbnail(url = user.avatar_url)

        now = datetime.now()

        if ctx.guild is not None:
            diffrence = now - user.joined_at
            embed.add_field(name = f'Time spent in {ctx.guild.name}',
            value = 'First joined at {}, thats over {} days ago'.format(
                user.joined_at.date(),
                diffrence.days
            ), inline = False)

        diffrence = now - user.created_at
        embed.add_field(name = 'Time spent on discord',
        value = 'First joined at {}, thats over {} days ago'.format(
            user.created_at.date(),
            diffrence.days
        ), inline = False)

        if ctx.guild is not None:
            roles = []
            for role in user.roles:
                roles.append(role.name)
            embed.add_field(name = 'Roles', value = ', '.join(roles))

        await ctx.send(embed = embed)

    @commands.command(
        name = "selfinfo",
        description = "get information about yourself (or just use userinfo without a user)",
        brief = "what about me?"
    )
    async def _selfinfo(self, ctx):
        await ctx.invoke(self.bot.get_command('userinfo'))

    @commands.command(
        name = "serverinfo",
        description = "get information about a server",
        brief = "what about us?"
    )
    @commands.guild_only()
    async def _serverinfo(self, ctx):
        embed = quick_embed(ctx, title = f'Server information about {ctx.guild.name}', description = f'ID: {ctx.guild.id}')
        now = datetime.now()
        diffrence = now - ctx.guild.created_at
        embed.add_field(name = 'Created at',
        value = '{}, thats over {} days ago'.format(
            ctx.guild.created_at.date(), diffrence.days
        ),inline = False)
        embed.add_field(name = 'User Count', value = len(ctx.guild.members))
        embed.add_field(name = 'Owner', value = ctx.guild.owner.name)
        embed.add_field(name = 'Text channels', value = len(ctx.guild.text_channels))
        embed.add_field(name = 'Voice channels', value = len(ctx.guild.voice_channels))
        embed.set_thumbnail(url = ctx.guild.icon_url)
        await ctx.send(embed = embed)

    @commands.command(
        name = "botinfo",
        description = "get information about me, the bot",
        brief = "what about wall-e?"
    )
    async def _botinfo(self, ctx):
        embed = quick_embed(ctx, title = f'Info about me, {self.bot.user.name}')
        embed.add_field(name = 'Working directory', value = dir_path)
        embed.set_thumbnail(url = self.bot.user.avatar_url)
        embed.add_field(name = 'discord.py version', value = discord.__version__)
        embed.add_field(name = 'bot name and id',
        value=f"Name: {self.bot.user.id}, ID: {self.bot.user.name}")
        embed.add_field(name = 'Architecture', value = platform.machine())
        embed.add_field(name = 'Version', value = platform.version())
        embed.add_field(name = 'Platform', value = platform.platform())
        embed.add_field(name = 'Processor', value = platform.processor())
        await ctx.send(embed = embed)

    @commands.command(
        name = "wolfram",
        description = "search wolfram alpha for the awnser to a question",
        brief = "not firefox"
    )
    async def _wolfram(self, ctx, *, question: str):
        try:
            resp = await self.wolfram.query(question)
        except LookupError:
            return await ctx.send('Nothing was found')

        embed = quick_embed(ctx, title = 'All possible awnsers from wolfram')

        ret = ''
        for pod in resp.pods:
            ret += pod.title + '\n'
            for subpod in pod.subpods:
                ret += '    ' + subpod.title + ': ' + subpod.raw_json['plaintext'] + '\n'
        embed.add_field(name = 'All possible awnsers', value = ret)
        await ctx.send(embed = embed)

    @commands.command(
        name = "reddit",
        description = "search reddit for a subreddit and post from it",
        brief = "leddit"
    )
    async def _reddit(self, ctx, target: str = 'all', search: str = 'new', index: int = 1):
        if not 0 <= index <= 25:
            return await ctx.send('Index must be between 0 and 25')

        # so i dont have to lower the search each time
        search = search.lower()
        if 'n' in search:
            search = 'new'
        elif 'h' in search:
            search = 'hot'
        elif 't' in search:
            search = 'top'
        else:
            return await ctx.send('Search mode must be new, top or hot')

        to_get = 'https://www.reddit.com/r/{}/{}.json?t=all'.format(target.lower(), search)

        j = json.loads(await url_request(url = to_get))

        if not j['data']['children']:
            return await ctx.send('No subreddit found')

        try: post = j['data']['children'][index]
        except IndexError: return await ctx.send('There is no post with that index')

        if await can_override(ctx):#TODO fix this
            if post['data']['over_18'] and not ctx.channel.is_nsfw():
                return await ctx.send('That post is nsfw, and must be requested in an nsfw channel')

        embed = quick_embed(ctx, title = f'Post from {target}',
            description = 'Posted by {}'.format(post['data']['author']))

        embed.add_field(name = 'Link', value = await tinyurl(post['data']['url']))

        embed.add_field(name = 'Title', value = post['data']['title'])
        embed.add_field(name = 'Votes', value = '{} Upvotes & {} Downvotes'.format(
                post['data']['ups'], post['data']['downs']))

        if not post['data']['selftext'] == '':
            embed.add_field(name = 'Selftext',
            value = post['data']['selftext'][:250] + (post['data']['selftext'][250:] and '...'))

        if embedable(post['data']['url']):
            embed.set_image(url = post['data']['url'])

        return await ctx.send(embed = embed)

    @commands.command(
        name = "avatar",
        description = "get someones highres avatar",
        brief = "why do you want this?"
    )
    async def _avatar(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        await ctx.send(user.avatar_url)

    @commands.group(invoke_without_command = True)
    async def prettyprint(self, ctx):
        embed = quick_embed(ctx, title = 'All the things I can prettyprint', description = 'Not that xml will ever be pretty anyway')
        b = []
        for a in self.prettyprint.walk_commands():
            if a.name not in b:
                embed.add_field(name = a.name, value = a.brief)
            b.append(a.name)
        await ctx.send(embed = embed)

    @prettyprint.command(
        name = "xml",
        description = "prettyprint and format xml",
        brief = "xml can't really be pretty"
    )
    async def _prettyprint_xml(self, ctx, *, text: str):
        try:
            ret = parseString(text)
        except Exception:
            return await ctx.send('Cannot prettyprint malformed xml')

        await ctx.send('```xml\n' + ret.toprettyxml() + '```')

    @prettyprint.command(
        name = "json",
        description = "prettyprint and format json",
        brief = "json can be pretty"
    )
    async def _prettyprint_json(self, ctx, *, text: str):
        try:
            ret = json.loads(text)
        except json.JSONDecodeError:
            return await ctx.send('Cannot prettyprint malformed json')

        await ctx.send('```json\n' + json.dumps(ret, indent = 4).replace('`', '\`') + '```')

    @prettyprint.command(
        name = "html",
        description = "prettyprint and format html",
        brief = "my favourite programming language"
    )
    async def _prettyprint_html(self, ctx, *, text: str):
        try:
            ret = bs(text, 'html.parser').prettify()
        except Exception:
            return await ctx.send('Cannot prettyprint malformed html')

        await ctx.send('```html\n' + ret.replace('`', '\`') + '```')



    def get_server_tag(self, server: int):
        for (serverid, tags) in self.tags.items():
            if int(serverid) == server:
                return tags

    @commands.group(invoke_without_command = True)
    @commands.guild_only()
    async def tag(self, ctx, name: str = None):
        tags = self.get_server_tag(ctx.guild.id)
        if not tags:
            return await ctx.send('this server has no tags')

        if name is None:
            _, ret = random.choice(list(tags.items()))
            return await ctx.send(ret)

        try:
            await ctx.send(tags[name.lower()])
        except KeyError:
            await ctx.send(f'no tag called {name} found')

    @tag.command(name = "add")
    @commands.guild_only()
    async def _tag_add(self, ctx, name: str, *, content: str):
        for (server, tags) in self.tags.items():
            if int(server) == ctx.guild.id:
                tags[name.lower()] = content
                return await ctx.send(f'added(or overwrote) the tag ``{name}``')

    @tag.command(name = "remove")
    @commands.guild_only()
    async def _tag_remove(self, ctx, name: str):
        for (server, tags) in self.tags.items():
            if int(server) == ctx.guild.id:
                try:
                    del tags[name.lower()]
                    return await ctx.send(f'removed the tag ``{name}``')
                except KeyError:
                    return await ctx.send(f'no tag called ``{name}``')

    @tag.command(name = "list")
    @commands.guild_only()
    async def _tag_list(self, ctx):
        pass

    @tag.before_invoke
    @_tag_add.before_invoke
    @_tag_remove.before_invoke
    @_tag_list.before_invoke
    async def _tag_before(self, ctx):
        if self.get_server_tag(ctx.guild.id) is None:
            self.tags[str(ctx.guild.id)] = {}

    @_tag_add.after_invoke
    @_tag_remove.after_invoke
    async def _tag_after(self, ctx):
        json.dump(self.tags, open('cogs/store/tags.json', 'w'), indent = 4)


    def get_server_quotes(self, server: int):
        for (serverid, quotes) in self.quotes.items():
            if int(serverid) == server:
                return quotes

    @commands.group(invoke_without_command = True)
    @commands.guild_only()
    async def quote(self, ctx, index: int = None):
        quotes = self.get_server_quotes(ctx.guild.id)
        if not quotes:
            return await ctx.send('no öätś')
        if index is None:
            return await ctx.send(random.choice(quotes))

        try:
            await ctx.send(quotes[index])
        except IndexError:
            await ctx.send(f'no quote with an index of ``{index}``')

    @quote.command(name = "add")
    @commands.guild_only()
    async def _quote_add(self, ctx, *, content: str):
        for (server, quotes) in self.quotes.items():
            if int(server) == ctx.guild.id:
                quotes.append(content)
                return await ctx.send(f'added quote with an index of {len(quotes)-1}')

    @quote.command(name = "remove")
    @commands.guild_only()
    async def _quote_remove(self, ctx, index: int):
        for (server, quotes) in self.quotes.items():
            if int(server) == ctx.guild.id:
                try:
                    quotes.pop(index)
                    return await ctx.send(f'removed quote at index {index}')
                except IndexError:
                    return await ctx.send(f'no quote found at index {index}')

    @quote.command(name = "list")
    @commands.guild_only()
    async def _quote_list(self, ctx):
        for (server, quotes) in self.quotes.items():
            if int(server) == ctx.guild.id:
                pass

    @_quote_add.before_invoke
    @_quote_remove.before_invoke
    @_quote_list.before_invoke
    @quote.before_invoke
    async def _quote_before(self, ctx):
        for (server, quotes) in self.quotes.items():
            if int(server) == ctx.guild.id:
                return
        self.quotes[str(ctx.guild.id)] = []

    @_quote_add.after_invoke
    @_quote_remove.after_invoke
    async def _quote_after(self, ctx):
        json.dump(self.quotes, open('cogs/store/quotes.json', 'w'), indent = 4)

def setup(bot):
    util = Utility(bot)
    bot.add_cog(util)
    if util.config['wolfram']['key'] == '':
        bot.remove_command('wolfram')
