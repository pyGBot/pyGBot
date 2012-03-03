pyGBot 0.3.0
============

Licence, copyright and attribution
----------------------------------
    pyGBot - Versatile IRC Bot
    Copyright (C) 2008 Morgan Lokhorst-Blight, Alex Soborov, Paul Rotering

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Based on pyTBot, (c) 2007 Paul Rotering
http://www.ircpoker.com
Licensed under GPLv2

Uses ConfigObj, (c) 2008 Michael Foord and Nicola Larosa
http://www.voidspace.org.uk/python/configobj.html
Licensed under modified (3 clause) BSD License

Uses "C# Events in Python", (c) 2005 Zoran Isailovski
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/410686
Licensed under MIT License

Simple Disclaimer:
THIS IS AN ALPHA RELEASE. It it provided AS-IS, with no warranty or support.
If it breaks your computer, it's not our fault.

Requirements
------------
* Python >= 2.5
* Twisted >= 2.0 (including twisted.words)
* pyOpenSSL (only when enabling SSL)

Getting Started
---------------
1. Decompress the pyGBot archive.
2. Rename `pyGBot.ini.default` to `pyGBot.ini`.
3. Rename `users.ini.default` to `users.ini`.
4. Open `pyGBot.ini` and modify the values. These are all of your bot's
configuration options. The main options you're interested in to get the bot up
and running are `host`, `port`, `nick` and `channel`.
5. Execute `runpyGBot.py`.

Configuring the Auth System
---------------------------
Some commands are limited to authorized users; this prevents just anyone from
telling pyGBot to (for example) join or leave a channel. pyGBot has an auth
system to control user login and access in order to use moderator- or
administrator-level commands. To configure it, you have to do 2 things: set the
auth mode in pyGBot.ini, and add users.

1.  pyGBot.ini

    pyGBot has two possible auth modes:
    
    *   `pygbot`: This mode uses its own username/password system stored in
        `users.ini`.
    *   `nickserv`: This mode identifies users by checking to see if they're
        identified with NickServ, and then checking if they're in `users.ini`
        to determine their access level (user, moderator or admin). This is
        designed for the standard atheme NickServ service.
    
    In order to configure the mode:
    
    1.  Open `pyGBot.ini`.
    2.  Under the section `[Plugins.system.Auth]`, change the `authtype` value
        to either `pygbot` or `nickserv`. (Don't add quotation marks around the
        value).
    3.  If the `[Plugins.system.Auth]` section or `authtype` value don't exist
        in the file, create them at the end of the file before doing step #2.

2.  Adding users
    
    By default, no users are configured with the auth system. To add users:
    
    1.  Run `hashpw.py`.
    2.  Enter the details it asks for. In `pygbot` auth mode, the username and
        password are needed for users to log in. In `nickserv` mode, the
        username is used to check if a person is identified with NickServ using
        the same _nick_ as the username you enter (password is _not_ used, but
        set it to something secure anyway in case you switch to `pygbot` mode).
    3.  If you ever need to remove a user from the system, open `users.ini` and
        delete the section corresponding to that user.

Customising with Included or Downloaded Plugins
-----------------------------------------------
pyGBot is highly customisable using plugins. Several plugins are included but
not enabled, and you can write or download your own plugins.

If you downloaded a plugin and want to install it:

1.  Put all the plugin's files into a directory under the `pyGBot/Plugins` 
    directory. (Note: If your plugin package contains a `Plugin` directory
    already, you're probably supposed to move archive's contents to `pyGBot`
    and let it merge the directories together. However, note that we take no
    responsibility if it overwrites pyGBot's own files or plugins and does
    something bad!)
2.  Follow the directions for configuring a plugin, below.

To configure a plugin that's included with pyGBot or one you just downloaded
and installed:

1.  Open `pyGBot.ini`.
2.  Find the `[Plugins]` section. Let's say your plugin's file is in
    `pyGBot/Plugins/example/ExPlugin.py`; then add the line `example.ExPlugin =`
    to the file (put nothing to the right of the equation sign).
3.  If you want the plugin to automatically activate when you start pyGBot, add
    the same line to the `[Plugins.system.Startup]`.
4.  If the plugin has some custom commands that work with the system.Commands
    plugin (i.e. it adds files to `pyGBot/Plugins/system/CommandSpec`), then
    you can bind those commands to the names used by IRC users in the
    `[Plugins.system.Commands]` section. Let's say one file is `DoStuff.py`
    and you want IRC users to type `^stuff` to activate the command, add the
    line `stuff = DoStuff`. (The `^` prefix can be changed).

Specific plugins may give more specific information about installing and
configuring. For the included plugins, their configuration is often commented
in the `pyGBot.ini` file, and sometimes explained in the comments (comments
start with #).

Writing Plugins
---------------
Detailed documentation on writing plugins is not available (yet! It's coming!).
You can take a look at `pyGBot/BasePlugin.py`, as well as existing plugins in
the `pyGBot/Plugins` directory to see how things are done. What follows is a
brief description of the plugin system and a few pointers.

Every plugin must be a class that subclasses `BasePlugin`. You should override
the methods in `BasePlugin` in order to intercept various IRC events, such as
receiving a message in a channel. When a plugin is loaded by pyGBot, the plugin
class is instantiated _once_ (calling `\_\_init\_\_()` in the process), and the
plugin instance's methods are called whenever the associated IRC event occurs.

For pyGBot's API, take a look at the first few methods (above `loadPlugins()`) 
in the class `GBot` of `pyGBot/core.py`, along with Twisted's documentation for
the irc.IRCClient class (which GBot subclasses). If methods exist to do the
same thing in both `GBot` and Twisted, use the `GBot` version. Logging 
facilities are provided via the `log.logger` object(pyGBot's log) and `log.chat`
object (IRC chat log), which are both instances of Python's built-in `logging`
module. (Do `from pyGBot import log` to use them). You can always take a look
at other plugins for examples on using the API.

Note that pyGBot will always pass messages to plugins as `unicode` strings,
_not_ 8-bit `str` strings (refer to the Python 2.x manual). pyGBot can handle
both `unicode` and `str` strings going back out (for example, when sending
a message to a channel).

Command System
--------------
The `system.Commands` plugin provides a set of commands (extensible, of course!)
which are single-line calls made by users to enact some immediate response or
action. The existing ones are primarily related to controlling the bot (join or
part channels, send public message, etc.), but any single-line command could
conceivably be implemented here. A few examples of other commands are the ones
used to play games, the `Seen` command (for the `features.Seen` plugin) and the
`Wiki` command (for the `reference.Wiki` plugin).

To write your own, start by taking a look at the `BaseCommand` class in
`pyGBot/Plugins/system/Commands.py` and at the existing commands in
`pyGBot/Plugins/system/CommandSpec`. Like Plugins, Commands need to be a class
that subclasses `BaseCommand`; but unlike Plugins, command classes don't have a
persistent instance: when an IRC user calls on a command, the command class
is instantiated, its `__init__()` method is called with the command parameters,
and then the instance is discarded.

You can easily write commands that act as a wrapper for a plugin. Doing so
avoids the need to check every incoming message yourself to find out if it's
intended for your plugin, and makes it easy for users of your plugin to change
the name IRC users use to call the command (see the `[Plugins.system.Commands]`
section of `pyGBot.ini`).

Website
--------
http://pygbot.github.com

Please use the issue tracker on the homepage to report any problems with the
software. For assistance, visit `#pyGBot` on the foonetic IRC network 
(irc.foonetic.net).

Enjoy!
- The pyGBot team
