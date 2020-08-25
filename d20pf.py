from __future__ import annotations

import re
import sys
from random import randint
from typing import Tuple, Generator, Optional, Sequence, List, Iterator
from dataclasses import dataclass

import discord
from discord.ext import commands
from discord.ext.commands import Context


re_roll = re.compile(r'\s*(?P<atk>.*?\S)\s*\((?P<dmg>.*?)\)\s*(?:\,|and|or)?')
re_atk = re.compile(r'(?P<count>\d+)?\s*(?P<name>.*?)\s*(?P<atk>(?:\+\d+/?)+)$')
re_atkpart = re.compile(r'\+(?P<val>\d+)')
re_dmg = re.compile(r'(?P<quant>\d+)d(?P<dice>\d+)(?:\+(?P<bonus>\d+))?(?:/(?:(?P<crit_from>\d+)[–-](?P<crit_to>\d+)))?(?:/[×x*](?P<crit_mod>\d+))?\s*(?:plus\s*(?P<extra>.*))?')


@dataclass
class AtkPart:
    bonus: int


    @classmethod
    def parse(cls, count: int, string: str) -> Generator[AtkPart, None, None]:
        for _ in range(count):
            for a in re_atkpart.findall(string): yield cls(int(a))


    def __repr__(self): return f'+{self.bonus}'


    def roll(self) -> Tuple[int, int]:
        d20 = randint(1, 20)
        return (d20, d20 + self.bonus)


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


    def __repr__(self): return self.name


    def roll(self) -> Generator[Tuple[AtkPart, int, int], None, None]:
        """returns the atkpart, rolled d20 and d20 + bonus"""
        for p in self.parts:
            d, r = p.roll()
            yield (p, d, r)


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


    def __repr__(self):
        return f'{self.quantity}d{self.dice} +{self.bonus}'


    def roll(self) -> Iterator[int]:
        return (randint(1, self.dice) for _ in range(self.quantity))


    def iscrit(self, roll: int) -> bool:
        return self.crit_from <= roll <= self.crit_to


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


def format_atk(roll: Roll, d20: int, part: AtkPart, res: int) -> str:
    atkbuf = f'{roll.atk} {part} = ({d20}) {part} = **{res}**'
    if   roll.dmg.iscrit(d20): atkbuf = f'__{atkbuf} <crit>__'
    elif d20 == 1            : atkbuf = f'~~{atkbuf} <nat1>~~'
    return atkbuf


@bot.command()
async def pf(ctx: Context, *arg):
    string = ' '.join(arg)
    rolls = Roll.parse(string)

    embed = discord.Embed()
    embed.set_footer(text=string)

    dmg_curr = 0

    # unwrap the roll attack parts in one flatmap
    rolled = ((r, p, d20, res) for r in rolls for p, d20, res in r.atk.roll())
    for roll, part, d20, res in sorted(rolled, key=lambda x: x[3], reverse=True):
        dmg = list(roll.dmg.roll())
        total = sum(dmg) + roll.dmg.bonus

        # 2d8 +14 = (4, 8) +14
        dmgbuf = f'{roll.dmg} = _({", ".join((str(x) for x in dmg))})_ +{roll.dmg.bonus}'
        if roll.dmg.iscrit(d20): 
            dmgbuf = f'{dmgbuf} *{roll.dmg.crit_mod}'
            total *= roll.dmg.crit_mod

        dmgbuf = f'{dmgbuf} = **{total}**'
        if roll.dmg.extra: dmgbuf = f'{dmgbuf} _+ {roll.dmg.extra}_'

        if not d20 == 1:
            dmg_curr += total
            dmgbuf = f'{dmgbuf} | **Σ {dmg_curr}**'

        embed.add_field(name=format_atk(roll, d20, part, res), value=dmgbuf, inline=False)
    await ctx.send(embed=embed)


if len(sys.argv) != 2: raise SystemExit('usage: python <d20pf.py> <bot token>')
bot.run(sys.argv[1])