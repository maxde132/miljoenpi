miljoenpi
=========

A videogame system for the Pi Pico, Pimoroni GFX Pack, and the Pimoroni Qw/ST Gamepad.

Overview
--------

MiljoenPi boots into a simple launcher (main.py) that lets the user browse and run any Python game script stored in the Pico’s root directory (/).

- Use the Qw/ST Gamepad to navigate and launch games
- Press "r" to reset any game
- High scores are saved automatically to scores.json
- Press the physical RESET button on the back of the GFX Pack to return to the welcome screen

Hardware Setup
--------------

1. Attach the Raspberry Pi Pico to the Pimoroni GFX Pack
2. Connect the Qw/ST cable from the GFX Pack to the Pimoroni Gamepad
3. Flash the Pirate-brand MicroPython firmware onto your Pico
4. Copy all scripts to the Pico’s root directory:
   - main.py and qwstpad.py must be named exactly
   - qwstpad.py could be in a /lib folder if you prefer
   - Other game scripts can be named however you like

Game Scripts
------------

- All games are based on buttonexamples.py
- Games restart when "r" is pressed
- Backlight control is built in
- You can create your own games or modify existing ones by following the input and display patterns used in the examples

File Overview
-------------

- main.py           — Launcher interface
- qwstpad.py        — Gamepad input handler
- scores.json       — Stores high scores
- buttonexamples.py — Template for building new games
- *.py              — Your custom games

Adding Your Own Games
---------------------

Just drop your .py files into the Pico’s root directory. As long as they follow the input conventions and use "r" to reset, they’ll work seamlessly with the launcher.
