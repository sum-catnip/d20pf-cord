from __future__ import annotations

import re
from random import randint
from typing import Tuple, Generator, Optional, Sequence, List, Iterator
from dataclasses import dataclass


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
