from __future__ import annotations

from parsers import pf

import sys

import discord
from discord.ext import commands
from discord.ext.commands import Context


bot = commands.Bot(command_prefix='d21 ')


@bot.event
async def on_ready():
    print(f'{bot.user.name} connected!')


@bot.command(name='pf')
async def pf_cmd(ctx: Context, *arg):
    string = ' '.join(arg)
    rolls = pf.Roll.parse(string)

    embed = discord.Embed()
    embed.set_footer(text=string)

    # unwrap the roll attack parts in one flatmap
    for roll, part, d20, res in ((r, p, d20, res) for r in rolls for p, d20, res in r.atk.roll()):
        atkbuf = f'{roll.atk} {part} = ({d20}) {part} = **{res}**'
        if   roll.dmg.iscrit(d20): atkbuf = f'__{atkbuf} <crit>__'
        elif d20 == 1            : atkbuf = f'~~{atkbuf} <nat1>~~'

        dmg = list(roll.dmg.roll())
        total = sum(dmg) + roll.dmg.bonus

        # 2d8 +14 = (4, 8) +14
        dmgbuf = f'{roll.dmg} = _({", ".join((str(x) for x in dmg))})_ +{roll.dmg.bonus}'
        if roll.dmg.iscrit(d20): 
            dmgbuf = f'{dmgbuf} *{roll.dmg.crit_mod}'
            total *= roll.dmg.crit_mod

        dmgbuf = f'{dmgbuf} = **{total}**'
        if roll.dmg.extra: dmgbuf = f'{dmgbuf} _+ {roll.dmg.extra}_'

        embed.add_field(name=atkbuf, value=dmgbuf, inline=False)
    await ctx.send(embed=embed)


if len(sys.argv) != 2: raise SystemExit('usage: python <d21.py> <bot token>')
bot.run(sys.argv[1])
