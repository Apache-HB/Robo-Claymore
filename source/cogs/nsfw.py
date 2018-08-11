from discord.ext import commands
from .store import tinyurl, embedable, quick_embed, url_request

from defusedxml.ElementTree import fromstring
import json
import random

class Nsfw:
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        print('cog {} loaded'.format(self.__class__.__name__))

    @commands.command(
        name = "e621",
        description = "search for an image from e621",
        brief = "degenerate"
    )
    async def _e_six_two_one(self, ctx, *, tags: str = None):

        if tags is None:
            url = 'https://e621.net/post/index.json?limit=25'

        else:
            url = 'https://e621.net/post/index.json?tags={}&limit=25'.format(tags)

        headers = {
            'User-Agent': 'RoboClaymore (by ApacheActual#6945 on discord)'
        }

        ret = json.loads(await url_request(url = url, headers = headers))

        if not ret:
            return await ctx.send('Nothing with tags {} found'.format(tags))

        post = random.choice(ret)

        embed = quick_embed(ctx, title = 'A post from e621')
        embed.add_field(name = 'Image source', value = await tinyurl(post['file_url']))

        if embedable(post['file_url']):
            embed.set_image(url = post['file_url'])

        await ctx.send(embed = embed)

    rule34_api = 'https://rule34.xxx/index.php?page=dapi&s=post&q=index&tags={}'

    @commands.command(
        name = "rule34",
        aliases = ['r34'],
        description = "search for an image from rule34.xxx",
        brief = "pip install aiorule34"
    )
    async def _rule34(self, ctx, *, tags: str):
        root = fromstring(await url_request(url = self.rule34_api.format(tags)))

        if not root:
            return await ctx.send('Nothing with tags {} found'.format(tags))

        post = random.choice(root)

        info = post.attrib

        tags = info['tags']
        file_url = info['file_url']

        embed = quick_embed(ctx, title = 'A post from rule34.xxx')
        embed.add_field(name = 'Image source', value = await tinyurl(file_url))

        if embedable(file_url):
            embed.set_image(url = file_url)

        await ctx.send(embed = embed)

    gelbooru_api = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags={}'

    @commands.command(
        name = "gelbooru",
        aliases = ['gel', 'gb'],
        description = "search for an image in gelbooru",
        brief = "the only nice booru api out there"
    )
    async def _gelbooru(self, ctx, *, tags: str):
        try:
            ret = json.loads(await url_request(url = self.gelbooru_api.format(tags)))
        except ValueError:
            return await ctx.send('Nothing with tags {} found'.format(tags))

        post = random.choice(ret)

        embed = quick_embed(ctx, title = 'A post from gelbooru.com')
        embed.add_field(name = 'Image source', value = await tinyurl(post['file_url']))

        if embedable(post['file_url']):
            embed.set_image(url = post['file_url'])

        return await ctx.send(embed = embed)

    @commands.command(
        name = "danbooru",
        aliases = ['dan', 'db'],
        description = "search for an image in danbooru",
        brief = "the closest to a SFW booru"
    )
    async def _danbooru(self, ctx, *, tags: str = None):
        if tags is None:
            url = 'https://danbooru.donmai.us/posts.json?random=true'

        else:
            url = 'https://danbooru.donmai.us/posts.json?limit=50?tags=\"{}\"'.format(tags.split(' '))

        ret = json.loads(await url_request(url = url))

        if not ret:
            return await ctx.send('Nothing found')

        post = random.choice(ret)

        embed = quick_embed(ctx, title = 'An image from danbooru')
        embed.add_field(name = 'Image source', value = await tinyurl(post['large_file_url']))

        if embedable(post['large_file_url']):
            embed.set_image(url = post['large_file_url'])

        return await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Nsfw(bot))
