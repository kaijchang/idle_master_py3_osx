Idle Master (Python branch)
===========

This program will determine which of your Steam games still have Steam Trading Card drops remaining, and will go through each application to simulate you being “in-game” so that cards will drop.  It will check periodically to see if the game you’re idling has card drops remaining.  When only one drop remains, it will start checking more frequently.  When the game you’re idling has no more cards, it’ll move on to the next game.  When no more cards are available, the program will terminate.

This fork focuses on compatibility with python3 and OSX.

The primary goal of the fork is to provide a simpler, more readable, extensible, and customizable python wrapper for Idle Master because the original wrapper isn't maintained, so it's still on python2 and doesn't work with Steam's new cookie system.

For the latest Windows version of Idle Master, [click here](https://github.com/jshackles/idle_master).

Requirements
-------

This application requires Steam to be open and for you to be logged in.

Setup
-------

Please read the included Setup Instructions.pdf file for detailed setup instructions and frequently asked questions.

Authors
-------

Optimized and rewritten for python3 and OSX by kajchang

jshackles and Stumpokapow

steam-idle was writen in C# using Steamworks.NET and CSteamworks by Riley Labrecque

License
-------

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation.  A copy of the GNU General Public License can be found at [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).  For your convenience, a copy of this license is included.