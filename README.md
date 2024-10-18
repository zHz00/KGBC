# KGBC: Kittens Game Buildings Calculator

## What is it?

First, you must know, what is Kittens Game. If you do not, please refer to https://kittensgame.com/ui/ .

In this game every building cost you more and more resources. I was tired to make Excel tables and I decided to make utility that will show cost of any amount of any building in the game.

Also, it show total amount of resources needed to build N buildings in a row, for example, wood needed to build 3rd, 4th and 5th Log Houses.

This program show every building in the game, so you will be spoiled if you use it. In this README file I intentionally blurred most of screenshots so unspoiled player will see only minor spoiler from first several hours of playthrough.

## Interface

This is text mode application written with curses library. Interface is similar to original KG, but have different function. You can use it both with keyboard and mouse. Thanks to curses library, every button is clickable.

First, you must go to Workshop tab and select desired discounts:

![Discounts list](help/Workshop.png)

Then you select building on any tab. Bonfire tab is the first one you'll see:

![Bonfire tab](help/Bonfire.png)

Then you see a table of resources, needed to create buildings from 1 to 20:

![Table with no selection](help/Table1.png)

You can scroll it, or you can select several buildings (only subsequent buildings are allowed) to see total cost:

![Table with selection](help/Table2.png)

## System requirements

-- Linux or Windows\\
-- Python 3.8 32-bit\\
-- windows-curses for Windows. Linux already have curses package preinstalled.\\
-- esprima (optional). If you don't have that, you can use program as normal, but you can't rebuild database.

Program have PyInstaller binaries, so you can just download it and run.

## License

MIT. See LICENSE file for details.