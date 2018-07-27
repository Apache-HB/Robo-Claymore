from discord.ext import commands
import discord
from .store import quick_embed, url_request
import time
import json
import random

titanfall_pilot_variables = {
    'pilots': [
        'Grapple',
        'Pulse Blade',
        'Stim',
        'A-Wall',
        'Phase Shift',
        'Holo Pilot',
        'Cloak'
    ],
    'grenades': [
        'Frag Grenade',
        'Arc Grenade',
        'Fire Star',
        'Gravity Star',
        'Electric Smoke',
        'Satchel Charge'
    ],
    'primary': [
        'R201',
        'R101',
        'Hemlock',
        'G2A5',
        'Flatline',
        'Alternator',
        'CAR',
        'R-97',
        'Volt',
        'L-STAR',
        'Spitfire',
        'Devotion',
        'Double Take',
        'Kraber',
        'DMR',
        'EVA-8',
        'Mastiff',
        'Cold War',
        'EPG',
        'Softball',
        'SMR'
    ],
    'secondary': [
        'RE .45',
        'Hammond P2016',
        'Wingman Elite',
        'Mozambique',
        'Wingman B3',
    ],
    'anti_titan': [
        'Charge Rifle',
        'MGL',
        'Thunderbolt',
        'Archer'
    ],
    'perk_slot_a': [
        'Power Cell',
        'Fast Regen',
        'Ordinance Expert',
        'Phase Embark'
    ],
    'perk_slot_b': [
        'Wall Hang',
        'Kill Report',
        'Hover',
        'Low Profile'
    ]
}

class Games:
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.frames = None#used for warframe cache
        print('cog {} loaded'.format(self.__class__.__name__))

    @classmethod
    def polarity_converter(self, text: str):
        return text.replace('<:madurai:319586146499690496>', 'Maduri').replace('<:naramon:319586146478850048>', 'Naramon').replace('<:vazarin:319586146269003778>', 'Varazin')

    @commands.group(invoke_without_command = True)
    async def warframe(self, ctx):
        embed = quick_embed(ctx, title = 'All the subcommands for warframe')
        b = []
        for a in self.warframe.walk_commands():
            if a.name not in b:
                embed.add_field(name = a.name, value = a.brief)
            b.append(a.name)
        await ctx.send(embed = embed)

    @warframe.command(name = "weaponinfo")
    async def _warframe_weaponinfo(self, ctx, *, name: str):
        ret = await url_request(url = 'https://api.warframestat.us/weapons/search/{}'.format(name.lower()))

        if not ret:
            return await ctx.send('{} was not found in the warframe database'.format(name))

        embed = quick_embed(ctx, title = 'Information about {}'.format(name), description = 'Taken from the official warframe database')

        a = []
        for weapon in ret:
            a.append(weapon['name'])
        if a:
            embed.add_field(name = 'Variants', value = ', '.join(a))
        embed.add_field(name = 'Name', value = ret[0]['name'])
        embed.add_field(name = 'More info', value = ret[0]['url'])
        embed.add_field(name = 'Minimum mastery rank', value = ret[0]['mr'])
        embed.add_field(name = 'Type', value = ret[0]['type'])

        try:
            embed.add_field(name = 'Base damage',
            value = 'A total of {} damage comprised of {} slash, {} puncture and {} impact'.format(
                ret[0]['damage'],
                ret[0]['slash'],
                ret[0]['puncture'],
                ret[0]['impact']
            ))
        except KeyError:
            embed.add_field(name = 'Base damage', value = ret[0]['damage'])

        if ret[0]['type'] == 'Melee':
            if ret[0]['polarities']:
                embed.add_field(name = 'Default polarities', value = ', '.join(ret[0]['polarities']))
                embed.add_field(name = 'Attack speed', value = ret[0]['speed'])
                embed.add_field(name = 'Slide attack damage', value = ret[0]['slide'])
                embed.add_field(name = 'Slam attack damage', value = ret[0]['jump'])
                embed.add_field(name = 'Wall attack damage', value = ret[0]['wall'])
                embed.add_field(name = 'Channeling efficiency', value = ret[0]['channeling'])
                embed.add_field(name = 'Default stance polarity', value = ret[0]['stancePolarity'])

        elif ret[0]['type'] in ['Primary', 'Secondary']:
            try: embed.add_field(name='Noise level', value=ret[0]['noise'])
            except KeyError: pass

            try: embed.add_field(name='Firerate', value=ret[0]['speed'])
            except KeyError: pass

            try: embed.add_field(name='Accuracy', value=ret[0]['accuracy'])
            except KeyError:pass

            try: embed.add_field(name='Maximum ammo capacity', value=ret[0]['ammo'])
            except KeyError: pass

            embed.add_field(name='Magazine capacity', value=ret[0]['magazine'])
            embed.add_field(name='Reload speed', value=ret[0]['reload'])
            embed.add_field(name='Projectile type', value=ret[0]['projectile'])
            embed.add_field(name='Trigger type', value=ret[0]['trigger'])

            try: embed.add_field(name='Flight speed', value=ret[0]['flight'])
            except KeyError:pass

        embed.add_field(name = 'Critical chance', value = ret[0]['crit_chance'])
        embed.add_field(name = 'Critical damage multiplier', value = ret[0]['crit_mult'])
        embed.add_field(name = 'Status chance', value = ret[0]['status_chance'])
        embed.add_field(name = 'Riven disposition', value = ret[0]['riven_disposition'])
        embed.set_thumbnail(url = ret[0]['thumbnail'])

        await ctx.send(embed = embed)

    @warframe.command(name = "dropinfo")
    async def _warframe_dropinfo(self, ctx, *, name: str):
        ret = json.loads(await url_request(url = 'https://api.warframestat.us/drops/search/{}'.format(name.lower())))
        if not ret:
            return await ctx.send('{} was not found in the warframe database'.format(name))

        embed = quick_embed(ctx, title = 'Information about {}'.format(name), description = 'Taken from the warframe database')

        for location in ret[:25]:
            embed.add_field(name = 'Item {} drops from {}'.format(location['item'], location['place']),
            value = 'Rarity of {}% & a drop chance of {}%'.format(location['rarity'], location['chance']))

        await ctx.send(embed = embed)

    @warframe.command(name = "frameinfo")
    async def _warframe_frameinfo(self, ctx, *, name: str):
        if self.frames is None:
            self.frames = json.loads(await url_request(url = 'https://api.warframestat.us/warframes'))

        for frame in self.frames:
            if name.lower() in frame['regex']:

                try: colour = frame['color']
                except KeyError: colour = 0x023cfc

                embed = quick_embed(ctx, title = frame['name'], description = frame['url'], colour = colour)

                embed.add_field(name = 'min/max health', value = frame['health'])
                embed.add_field(name = 'min/max shields', value = frame['shield'])
                embed.add_field(name = 'Base armor', value = frame['armor'])
                embed.add_field(name = 'min/max power', value = frame['power'])
                embed.add_field(name = 'sprint speed', value = frame['speed'])

                try: embed.add_field(name = 'More info', value = frame['info'])
                except KeyError: pass

                if not frame['aura'] == '':
                    embed.add_field(name = 'Default aura polarity', value = self.polarity_converter(frame['aura']))

                embed.add_field(name = 'Default polarities', value = self.polarity_converter(', '.join(frame['polarities'])))

                try: embed.add_field(name = 'In game description', value = frame['description'])
                except KeyError: pass

                try: embed.add_field(name = 'Main drop location', value = frame['location'])
                except KeyError: pass

                try: embed.set_thumbnail(url = frame['thumbnail'])
                except KeyError: pass

                return await ctx.send(embed = embed)

        await ctx.send('No frame called {} found'.format(name))

    @warframe.command(name = "sortie")
    async def _warframe_sortie(self, ctx):
        ret = json.loads(await url_request(url = 'https://api.warframestat.us/pc/sortie'))

        embed = quick_embed(ctx, title = 'Todays sortie', description = 'From the official warframe database')

        for index, value in enumerate(ret['variants'], start = 1):

            embed.add_field(name = 'Mission {}'.format(index),
            value = 'Mission type: {}\nModifier: {}\nLocation: {}'.format(
                value['missionType'],
                value['modifier'],
                value['node']
            ), inline = False)

        embed.set_footer(text = 'Sortie for {}'.format(time.time()))

        return await ctx.send(embed = embed)

    @warframe.command(name = "alert")
    async def _warframe_alert(self, ctx):
        ret = json.loads(await url_request(url = 'https://api.warframestat.us/pc/alerts'))

        embed = quick_embed(ctx, title = 'Currently running sorties', description = 'Taken from the warframe web api')

        for index, alert in enumerate(ret):
            embed.add_field(name = 'Alert {}'.format(index),
            value = 'Location {}\nMission type: {}\nFaction: {}\nRewards: {}\nExpires in: {}'.format(
                alert['mission']['node'],
                alert['mission']['type'],
                alert['mission']['faction'],
                alert['mission']['reward']['asString'],
                alert['eta']
            ), inline = False)

        await ctx.send(embed = embed)

    @warframe.command(name = "baro")
    async def _warframe_baro(self, ctx):
        ret = json.loads(await url_request(url = 'https://api.warframestat.us/pc/voidTrader'))

        embed = quick_embed(ctx, title = 'BaroKi\'teer')

        if not ret['active']:
            embed.add_field(name = 'Is currently away in the void',
            value = 'He will be back in {}'.format(ret['startString']))

            return await ctx.send(embed = embed)

        embed.add_field(name = 'Location', value = ret['location'])
        embed.add_field(name = 'Current inventory', value = ', '.join(ret['inventory']))

        await ctx.send(embed = embed)

    @warframe.command(name = "darvo")
    async def _warframe_darvo(self, ctx):
        ret = json.laods(await url_request(url = 'https://api.warframestat.us/pc/dailyDeals'))

        embed = quick_embed(ctx, title = 'Current Darvo deal',
        description = 'Could I interest you in some half price life support')

        embed.add_field(name = 'Item', value = ret[0]['item'])
        embed.add_field(name = 'Discount',
        vlaue = 'Original price: {}\nPercentage discount: {}\nCurrent price: {}'.format(
            ret[0]['originalPrice'],
            ret[0]['discount'],
            ret[0]['salePrice']
        ))

        embed.add_field(name = 'Amount sold', value = str(ret[0]['sold']))
        embed.add_field(name = 'Time left', value = ret[0]['eta'])

        await ctx.send(embed = embed)

    @warframe.command(name = "cetustime")
    async def _warframe_cetustime(self, ctx):
        ret = json.loads(await url_request(url = 'https://api.warframestat.us/pc/cetusCycle'))

        embed = quick_embed(ctx, title = 'Current time on cetus',
        description = 'Taken from the warframe web api')

        embed.add_field(name = 'Time', value = ret['isDay'])
        embed.add_field(name = 'Cycle ID', value = ret['id'])
        embed.add_field(name = 'Time left', value = ret['timeLeft'])
        embed.add_field(name = 'Quick info', value = ret['shortString'])

        await ctx.send(embed = embed)

    @commands.group(invoke_without_command = True)
    async def titanfall(self, ctx):
        embed = quick_embed(ctx, title = 'All the subcommands for titanfall')
        b = []
        for a in self.titanfall.walk_commands():
            if a.name not in b:
                embed.add_field(name = a.name, value = a.brief)
            b.append(a.name)
        await ctx.send(embed = embed)

    @titanfall.command(name = "randompilot")
    async def _titanfall_randompilot(self, ctx):
        ret = '{} Here is a random loadout```diff\n'.format(ctx.author.mention)

        ret += '+ Pilot: ' + random.choice(titanfall_pilot_variables['pilots']) + '\n'
        ret += '- Grenade: ' + random.choice(titanfall_pilot_variables['grenades']) + '\n'
        ret += '+ Primary: ' + random.choice(titanfall_pilot_variables['primary']) + '\n'
        ret += '- Secondary: ' + random.choice(titanfall_pilot_variables['secondary']) + '\n'
        ret += '+ Anti Titan: ' + random.choice(titanfall_pilot_variables['anti_titan']) + '\n'
        ret += '- First Perk: ' + random.choice(titanfall_pilot_variables['perk_slot_a']) + '\n'
        ret += '+ Second Perk: ' + random.choice(titanfall_pilot_variables['perk_slot_b']) + '\n'
        ret += '\n```'
        await ctx.send(ret)

    @titanfall.command(name = "randomtitan", brief = "soon™")
    async def _titanfall_randomtitan(self, ctx):
        await ctx.send('soon™')

    @titanfall.command(name = "randomloadout", brief = "soon™")
    async def _titanfall_randomloadout(self, ctx):
        await ctx.send('soon™')

    tttreacts = {
        'accept': '✅',
        '1': '1⃣',
        '2': '2⃣',
        '3': '3⃣',
        '4': '4⃣',
        '5': '5⃣',
        '6': '6⃣',
        '7': '7⃣',
        '8': '8⃣',
        '9': '9⃣'
    }

    tttgames = []

    tttxomap = {
        0: None,
        1: 'X',
        2: 'O'
    }

    ttttemplate = '''```
{host} Is playing against {opp}
Current board
+---+---+---+
| {a} | {b} | {c} |
+---+---+---+
| {d} | {e} | {f} |
+---+---+---+
| {g} | {h} | {i} |
+---+---+---+
It is currently {current}'s turn```
    '''

    def tttmessage(self, match, first, second, current):
        board = match['status']
        return self.ttttemplate.format(
            host = first,
            opp = second,
            current = str(current) + (' (host)' if match['current'] == 1 else ' (opponent)'),
            a = self.tttxomap[board[0][0]] if self.tttxomap[board[0][0]] else 1,
            b = self.tttxomap[board[0][1]] if self.tttxomap[board[0][1]] else 2,
            c = self.tttxomap[board[0][2]] if self.tttxomap[board[0][2]] else 3,
            d = self.tttxomap[board[1][0]] if self.tttxomap[board[1][0]] else 4,
            e = self.tttxomap[board[1][1]] if self.tttxomap[board[1][1]] else 5,
            f = self.tttxomap[board[1][2]] if self.tttxomap[board[1][2]] else 6,
            g = self.tttxomap[board[2][0]] if self.tttxomap[board[2][0]] else 7,
            h = self.tttxomap[board[2][1]] if self.tttxomap[board[2][1]] else 8,
            i = self.tttxomap[board[2][2]] if self.tttxomap[board[2][2]] else 9
        )

    @classmethod
    def check_winner(self, game):
        for player in range(1, 3):

            for row in range(3):
                if all(a == player for a in game['status'][row]):
                    return player #horisontal checking

            for col in range(3):
                if all(a[col] == player for a in game['status']):
                    return player #vertical checking

            if game['status'][0][0] == player and game['status'][1][1] == player and game['status'][2][2] == player:
                return player

            if game['status'][0][2] == player and game['status'][1][1] == player and game['status'][2][0] == player:
                return player
            #lazy way of checking diagonals

        if game['turns'] > 10:
            return 0

        return 3

    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        guild = discord.utils.get(self.bot.guilds, id = payload.guild_id)
        channel = discord.utils.get(guild.channels, id = payload.channel_id)

        react = payload.emoji
        idx = 0
        if str(react) == self.tttreacts['accept']:
            for index, each in enumerate(self.tttgames):
                idx = index
                if each['id'] == payload.message_id:
                    if each['opp'] is None:
                        continue
                    elif each['opp'] != payload.user_id:
                        return
                    elif each['accepted']:
                        return
                    elif each['host'] == payload.user_id:
                        return

            self.tttgames[idx]['opp'] = payload.user_id
            self.tttgames[idx]['accepted'] = True
            message = await channel.get_message(self.tttgames[idx]['id'])

            for key, val in self.tttreacts.items():
                if key == 'accept':
                    continue
                await message.add_reaction(val)


        for match in self.tttgames:
            if payload.user_id in [match['opp'], match['host']]:
                game = match
                break
            game = None

        if not self.tttgames:
            game = None

        if game is None:
            return

        if game['current'] == 1 and payload.user_id not in  game['host']:
            return
        elif game['current'] == 2 and payload.user_id != game['opp']:
            return

        for key, val in self.tttreacts.items():
            if key == 'accept':#HACK remove this and find a nice pythonic way to skip first pair
                continue

            if str(react) == val:
                a = int(key)

                key_table = {
                    1: [0,0],
                    2: [0,1],
                    3: [0,2],
                    4: [1,0],
                    5: [1,1],
                    6: [1,2],
                    7: [2,0],
                    8: [2,1],
                    9: [2,2]
                }

                if game['status'][key_table[a][0]][key_table[a][1]] == 0:
                    game['status'][key_table[a][0]][key_table[a][1]] = game['current']
                else:
                    return

        message = await channel.get_message(game['id'])

        host = discord.utils.get(guild.members, id = game['host'])
        opp = discord.utils.get(guild.members, id = game['opp'])

        #flip turns from host to opp
        game['current'] = 1 if game['current'] == 2 else 2
        game['turns'] += 1

        victor = self.check_winner(game)
        #if 1 then host wins
        #if 2 then opp wins
        #if 0 then draw
        #if 3 then continue playing

        if victor == 1:
            await message.edit(content = 'host wins')
            self.tttgames.remove(game)
        elif victor == 2:
            await message.edit(content = 'opponent wins')
            self.tttgames.remove(game)
        elif victor == 0:
            await message.edit(content = 'draw')
            self.tttgames.remove(game)
        else:
            await message.edit(content = self.tttmessage(game, host, opp, host if payload.user_id == game['host'] else opp))

    @commands.command(name = "tictactoe", aliases = ['ttt'])
    async def _tictactoe(self, ctx, opponent: discord.Member = None):
        for each in self.tttgames:
            if each['host'] == ctx.author.id:
                return await ctx.send('you already have an outstanding match')

        if opponent is None:
            message = await ctx.send('{} would like to play tic tac toe with someone\n react to accept'.format(ctx.author.mention))

        else:
            message = await ctx.send('{} would like to face {} in a game of tictactoe\nreact to accept'.format(
                ctx.author.mention,
                opponent.mention))

        self.tttgames.append({
            'id': message.id,
            'host': ctx.author.id,
            'opp': opponent,
            'accepted': False,
            'turns': 0,
            'current': 1, #1 is host 2 is opp
            'status': [
                [0,0,0],
                [0,0,0],
                [0,0,0]
            ]
        })

        await message.add_reaction(self.tttreacts['accept'])

    cfgames = []

    cfmap = {
        0: ':black_circle:',
        1: ':red_circle:',
        2: ':large_blue_circle:'
    }

    cfreacts = {
        'accept': '✅',
        '1': '🇦',
        '2': '🇧',
        '3': '🇨',
        '4': '🇩',
        '5': '🇪',
        '6': '🇫',
        '7': '🇬'
    }

    @commands.command(name = "connect4")
    async def _connectfour(self, ctx, opponent: discord.Member = None):
        for each in self.cfgames:
            if each['host'] == ctx.author.id:
                return await ctx.send('You already have an outstanding match')

        if opponent is None:
            message = await ctx.send('{} would like to play a game of connect 4\nreact to accept'.format(
                ctx.author.mention
            ))
        else:
            message = await ctx.send('{} would like to play challenge {} in a game of connect 4\nreact to accept'.format(
                ctx.author.mention,
                opponent.mention
            ))

        self.cfgames.append({
                'id': message.id,
                'host': ctx.author.id,
                'opp': opponent.id if opponent else None,
                'accepted': False,
                'turns': 0,
                'current': 1,
                'status': [
                    [],
                    [],
                    [],
                    [],
                    [],
                    [],
                ]
            })

def setup(bot):
    bot.add_cog(Games(bot))
