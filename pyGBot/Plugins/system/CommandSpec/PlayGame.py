##
##    pyGBot - Versatile IRC Bot
##    Copyright (C) 2008 Morgan Lokhorst-Blight, Alex Soborov
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

from pyGBot.Plugins.system.Commands import BaseCommand
from pyGBot.Plugins.system.Auth import AuthLevels as AL

class PlayGame(BaseCommand):
    level = AL.User
    def __init__(self, bot, channel, user, args):
        args = args.split()
        if channel == user or channel == None:
            bot.noteout(user,"This command must be run in a channel.")
            return

        if len(args) == 0:
            bot.pubout(channel, 'Please specify a game. use the list command to see what I can play.')
            return
            
        for p in bot.activeplugins[channel]:
            if p.startswith('games.'):
                bot.pubout(channel, 'There is a game already active. Use the stop command to deactivate it.')
                return

        pluginname = 'games.' + args[0].capitalize()

        if not bot.loadPlugin(pluginname, channel):
            bot.pubout(channel, "Error loading %s" % args[0].capitalize())
            return

        if bot.activatePlugin(pluginname, channel):
            bot.pubout(channel, "%s started." % args[0].capitalize())
        else:
            bot.pubout(channel, "Error activating %s" % args[0].capitalize())
