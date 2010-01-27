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
    def __init__(self, bot, channel, user, args):        bot.pubout(channel, 'Commands available:')        bot.pubout(channel, 'list: Lists games to play.')
        bot.pubout(channel, 'start <gamename>: Starts a game.')                bot.pubout(channel, 'stop <gamename>: Stops a game.')
        bot.pubout(channel, 'join <channel>: Joins a channel.')
        bot.pubout(channel, 'part <channel>: Parts a channel.')
        bot.pubout(channel, 'say <channel> <message>: Says <message> on <channel>.')
        bot.pubout(channel, 'do <channel> <action>: Performs <action> in <channel> (the /me command).')
        bot.pubout(channel, 'msg <user> <message>: Sends <user> a message.')        
        bot.pubout(channel, 'statsroll: Generates a DnD-style Stats set.')
        bot.pubout(channel, 'help: This help.')
