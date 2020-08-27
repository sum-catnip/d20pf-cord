# d21cord
tabletop rpg dice parsing and rolling utility bot
[invite me!](https://discord.com/api/oauth2/authorize?client_id=747425300211826748&permissions=2048&scope=bot)

# supported commands:

## pf
parses a pathfinder (e1) attack string and rolls all attack and damage rolls for you.
- crits are applied automatically
- nat1s are also applied
- attacks are rolled in order
- formatting highlights the most important parts

sample input ([source](https://www.d20pfsrd.com/bestiary/monster-listings/outsiders/devil/devils-unique/devil-lucifer-prince-of-darkness-tohc)):
> =pf Huge +6 trident +71/+66/+61/+56 (3d6+28), bite +62 (2d8+7 plus 1d8 acid), sting +62 (2d8+7 plus poison) or 2 claws +64 (2d6+14 plus 1d8 acid), bite +64 (2d8+14 plus 1d8 acid), sting +62 (2d8+7 plus poison)

![pf command output](scrots/pf.png)

## ez
parses a string for dice rolls and runs a calculation with the dice results.
- each dice is displayed seperately
- each roll is also displayed seperately
- 1s and 20s are highlighted
- diceroll results are highlighted in the final formular

sample input
> =ez ((5d20 +32) *2 - 3d8)

![ez command output](scrots/ez.png)

## pf2
parses a pathfinder (e2) attack string and rolls all attack and damage rolls for you.
- crits are applied automatically
- nat1s are also applied
- attacks are rolled in order
- formatting highlights the most important parts
- multiple attacks are seperated with `;`
- multi attack penalty and agility weapons are accounted for

sample input ([source](https://2e.aonprd.com/Monsters.aspx?ID=526)):
> =pf2 jaws +29 [+24/+19] (reach 10 feet), Damage 3d12+13 piercing plus Improved Grab

![pf2 command output](scrots/pf2.png)

multiple attacks sample input (any amount of attacks is possible):
> =pf2 jaws +29 [+24/+19] (reach 10 feet), Damage 3d12+13 piercing plus Improved Grab; horn +27 [+22/+17] (deadly d8, reach 15 feet), Damage 3d8+13 piercing

pf2.d20pfsrd format is also supported:
> =pf2 longsword +28 (magical, reach 10 feet, versatile P), Damage 2d8+15 slashing; fist +25 (agile, reach 10 feet, nonlethal), Damage 3d8+13 bludgeoning

# TODO
- ~~undo attack roll ordering and dmg accumulation~~
- stop being an idiot
- parse negative attack bonus
- ~~clean up the messy calculation code~~
- ~~sort output by attack role~~
- ~~display 1's~~
- ~~add-up current dmg (except for 1's)~~
- roll extras if they're are rollable
- ~~use markown memes in output (mainly bold)~~
- ~~parse pathfinder2 stuff and maybe dnd~~
- ~~dice calculator command with dice templating, showing dice results seperately~~
- maybe scrape testcases from d20pfsrd.com
