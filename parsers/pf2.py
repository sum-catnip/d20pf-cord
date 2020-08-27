from __future__ import annotations

import re
from random import randint
from typing import Tuple, Generator, Iterator, List, Optional
from dataclasses import dataclass


re_roll = re.compile(r'(?P<atk>.*?),\s*Damage\s*(?P<dmg>[^;]*)(?:;\s*)?')
re_atk = re.compile(r'(?P<name>.*?)\s*\+(?P<bonus>\d+)\s*(?:\[\+(?P<multi1>\d+)/\+(?P<multi2>\d+)\])?\s*(?:\((?P<extra>.*?)\))?')
re_dmg = re.compile(r'(?:(?P<quant>\d+)d(?P<dice>\d+))?(?:\+(?P<bonus>\d+))?\s*(?P<type>.*?)(?:\s+(?:and|or|\+|plus)|$)\s*')


@dataclass
class AtkExtra:
    bonus: str

    @classmethod
    def parse(cls, string: str) -> List[AtkExtra]:
        return [AtkExtra(x) for x in string.split(',')]

    def __repr__(self): return self.bonus


@dataclass
class Atk:
    name:  str
    bonus: int
    multi1: int
    multi2: int
    extra: List[AtkExtra]

    @classmethod
    def parse(cls, string: str) -> Atk:
        match = re_atk.match(string)
        if not match: raise ValueError(f'invalid format in attack: [{string}]')

        extra = AtkExtra.parse(match.group('extra') or '')
        bonus = int(match.group('bonus'))

        multi1 = 5
        multi2 = 10
        if 'agile' in map(str, extra):
            multi1 = 4
            multi2 = 8

        if match.group('multi1'): multi1 = bonus - int(match.group('multi1'))
        if match.group('multi2'): multi2 = bonus - int(match.group('multi2'))

        return cls(match.group('name'),
                   int(match.group('bonus')),
                   multi1, multi2, extra)

    def __repr__(self): return f'{self.name} +{self.bonus}'

    def roll(self, atki) -> Tuple[int, int, int]:
        """returns rolled d20, multi attack penalty and the final result"""
        d20 = randint(1, 20)
        penalty = 0
        if atki > 0: penalty = self.multi1
        if atki > 1: penalty = self.multi2
        return (d20, penalty, d20 + self.bonus - penalty)


@dataclass
class Dmg:
    quantity:  int
    dice:      int
    bonus:     int
    type:      Optional[str]

    @classmethod
    def parse(cls, string: str) -> Generator[Dmg, None, None]:
        for match in re_dmg.finditer(string):
            yield Dmg(int(match.group('quant') or 0),
                      int(match.group('dice')  or 0),
                      int(match.group('bonus') or 0),
                          match.group('type'))

    def __repr__(self):
        if self.quantity: return f'{self.quantity}d{self.dice} +{self.bonus}'
        if self.type:     return f'{self.type}'
        else: return ''

    def roll(self) -> Iterator[int]:
        return (randint(1, self.dice) for _ in range(self.quantity))


@dataclass
class Roll:
    atk: Atk
    dmg: Generator[Dmg, None, None]

    @classmethod
    def parse(cls, string: str) -> Generator[Roll, None, None]:
        for atk, dmg in re_roll.findall(string):
            yield Roll(Atk.parse(atk), Dmg.parse(dmg))
