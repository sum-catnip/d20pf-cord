# d21cord
tabletop rpg dice parsing and rolling utility bot

# supported commands:

## pf
parses a pathfinder (e1) attack string and rolls all attack and damage rolls for you.
- crits are applied automatically
- nat1s are also applied
- output is sorted by attackroll
- for each attack the accumulated damage is displayed

All you have to do is find the last attack that hits and read the damage.
Attack extras (like grab or +1d8 acid) are displayed but not added to the damage due to possible immunities/res/vulns.

sample input ([source](https://www.d20pfsrd.com/bestiary/monster-listings/outsiders/devil/devils-unique/devil-lucifer-prince-of-darkness-tohc)):
> d21 pf Huge +6 trident +71/+66/+61/+56 (3d6+28), bite +62 (2d8+7 plus 1d8 acid), sting +62 (2d8+7 plus poison) or 2 claws +64 (2d6+14 plus 1d8 acid), bite +64 (2d8+14 plus 1d8 acid), sting +62 (2d8+7 plus poison)

![monster command output](scrots/monster.png)


# TODO
- undo attack roll ordering and dmg accumulation
- stop being an idiot
- parse negative attack bonus
- ~~clean up the messy calculation code~~
- ~~sort output by attack role~~
- ~~display 1's~~
- ~~add-up current dmg (except for 1's)~~
- roll extras if they're are rollable
- ~~use markown memes in output (mainly bold)~~
- parse pathfinder2 stuff and maybe dnd
- dice calculator command with dice templating, showing dice results seperately
- parse player attacks?
- maybe scrape testcases from d20pfsrd.com