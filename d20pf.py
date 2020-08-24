from __future__ import annotations

import re
import sys
from random import randint
from typing import Tuple, Generator, Optional, Sequence
from dataclasses import dataclass

import discord
from discord.ext import commands
from discord.ext.commands import Context


re_roll = re.compile(r'\s*(?P<atk>.*?\S)\s*\((?P<dmg>.*?)\)\s*(?:\,|and|or)?')
re_atk = re.compile(r'(?P<count>\d+)?\s*(?P<name>.*?)\s*(?P<atk>(?:\+\d+/?)+)$')
re_atkpart = re.compile(r'\+(?P<val>\d+)')
re_dmg = re.compile(r'(?P<quant>\d+)d(?P<dice>\d)(?:\+(?P<bonus>\d+))?(?:/(?:(?P<crit_from>\d+)[–-](?P<crit_to>\d+)))?(?:/[×x*](?P<crit_mod>\d+))?\s*(?:plus\s*(?P<extra>.*))?')


@dataclass
class AtkPart:
    bonus: int


    @classmethod
    def parse(cls, count: int, string: str) -> Generator[AtkPart, None, None]:
        for _ in range(count):
            for a in re_atkpart.findall(string): yield cls(int(a))


@dataclass
class Atk:
    name:  str
    parts: Generator[AtkPart, None, None]


    @classmethod
    def parse(cls, string: str) -> Atk:
        match = re_atk.match(string)
        if not match: raise ValueError(f'invalid format in attack: [{string}]')
        parts = AtkPart.parse(int(match.group('count') or 1), match.group('atk'))
        return cls(match.group('name'), parts)


@dataclass
class Dmg:
    quantity:  int
    dice:      int
    bonus:     int
    crit_from: int
    crit_to:   int
    crit_mod:  int
    extra:     Optional[str]


    @classmethod
    def parse(cls, string: str) -> Dmg:
        match = re_dmg.match(string)
        if not match: raise ValueError(f'invalid format in dmg: [{string}]')
        return Dmg(int(match.group('quant')),
                   int(match.group('dice')),
                   int(match.group('bonus')     or 0),
                   int(match.group('crit_from') or 20),
                   int(match.group('crit_to')   or 20),
                   int(match.group('crit_mod')  or 2),
                       match.group('extra'))


@dataclass
class Roll:
    atk: Atk
    dmg: Dmg


    @classmethod
    def parse(cls, string: str) -> Generator[Roll, None, None]:
        for atk, dmg in re_roll.findall(string):
            yield Roll(Atk.parse(atk), Dmg.parse(dmg))


bot = commands.Bot(command_prefix='d20pf ')


@bot.event
async def on_ready():
    print(f'{bot.user.name} connected!')


@bot.command()
async def monster(ctx: Context, *arg):
    string = ' '.join(arg)
    rolls = Roll.parse(string)

    embed = discord.Embed()
    embed.set_footer(text=string)

    for roll in rolls:
        for part in roll.atk.parts:
            d20 = randint(1, 20)
            crit = roll.dmg.crit_from <= d20 <= roll.dmg.crit_to
            res = d20 + part.bonus
            atkstr = f'{roll.atk.name} +{part.bonus} = [{d20}] + {part.bonus} = {res}'
            if crit: atkstr += ' | <crit>'
            
            dmg = roll.dmg
            dmgstr = f'{dmg.quantity}d{dmg.dice} + {dmg.bonus}'
            if crit: dmgstr += f' * {dmg.crit_mod}'
            dmgstr += ' = ['

            res = dmg.bonus
            for i in range(1, dmg.quantity +1):
                dn = randint(1, dmg.dice)
                res += dn
                dmgstr += f'{dn}'
                if i < dmg.quantity: dmgstr += ', '

            dmgstr += f'] + {dmg.bonus}'
            if crit:
                dmgstr += f' * {dmg.crit_mod}'
                res *= dmg.crit_mod

            dmgstr += f' = {res}'
            if dmg.extra: dmgstr += f' | plus {dmg.extra}'

            embed.add_field(name=atkstr, value=dmgstr, inline=False)
    await ctx.send(embed=embed)


if len(sys.argv) != 2: raise SystemExit('usage: python <d20pf.py> <bot token>')
bot.run(sys.argv[1])