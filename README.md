Idle Master (Python branch)
===========

This program will determine which of your Steam games still have Steam Trading Card drops remaining, and will go through each application to simulate you being “in-game” so that cards will drop.  It will check periodically to see if the game you’re idling has card drops remaining.  When only one drop remains, it will start checking more frequently.  When the game you’re idling has no more cards, it’ll move on to the next game.  When no more cards are available, the program will terminate.

This fork focuses on compatibility with python3 and OSX.

The primary goal of the fork is to provide a simpler, more readable, extensible, and customizable python wrapper for Idle Master because the original wrapper isn't maintained, so it's still on python2 and doesn't work with Steam's new cookie system.

For the latest Windows version of Idle Master, [click here](https://github.com/jshackles/idle_master).

Requirements
-------

This application requires the Steam desktop application to be open and for you to be logged in. 

It will also require you to be logged in semi-recently on `steamcommunity.com` so it can read the cookies from the browser. It may also ask for an administrator password if it doesn't yet have access to your browser's storage.

Finally, you will need to install python dependencies with `pip3 install -r requirements.txt`.

Config
-------

The configuration is read from `settings.json`.

```json
{
  "sort": "",
  "delayPerCard": 5,
  "blacklist": [
  ]
}
```

`sort` (optional) - If specified, sorts the order in which the games are idled. Possible sort types are `mostcards`, which idles the games with the most card drops available first, and `leastcards`, which does the opposite.

`delayPerCard` - Amount of time per card, in minutes, to wait between querying for how many card drops are remaining for the game. For example, if the `delayPerCard` is set to `5`, it will check every twenty minutes if there are four card drops remaining.

`blacklist` - List of steam app ids to ignore (to not idle). For example, to ignore Torchlight II, you would look at the steam store url: `https://store.steampowered.com/app/200710/Torchlight_II/`, and put the id `200710` into the blacklist.

Authors
-------

Optimized and rewritten for python3 and OSX by kajchang

jshackles and Stumpokapow

steam-idle was writen in C# using Steamworks.NET and CSteamworks by Riley Labrecque

License
-------

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation.  A copy of the GNU General Public License can be found at [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).  For your convenience, a copy of this license is included.