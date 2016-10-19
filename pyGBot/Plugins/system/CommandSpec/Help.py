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

class Help(BaseCommand):
    level = AL.User
    def __init__(self, bot, channel, user, args):
        bot.noteout(user, 'Commands available:')
        bot.noteout(user, 'list: Lists games to play.')
        bot.noteout(user, 'start <gamename>: Starts a game.')
        bot.noteout(user, 'stop <gamename>: Stops a game.')
        bot.noteout(user, 'join <channel>: Joins a channel.')
        bot.noteout(user, 'part <channel>: Parts a channel.')
        bot.noteout(user, 'say <channel> <message>: Says <message> on <channel>.')
        bot.noteout(user, 'do <channel> <action>: Performs <action> in <channel> (the /me command).')
        bot.noteout(user, 'msg <user> <message>: Sends <user> a message.')        
        bot.noteout(user, 'statsroll: Generates a DnD-style Stats set.')
        bot.noteout(user, 'help: This help.')
