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
        bot.replyout(channel, user, 'Commands available:')
        bot.replyout(channel, user, 'list: Lists games to play.')
        bot.replyout(channel, user, 'start <gamename>: Starts a game.')
        bot.replyout(channel, user, 'stop <gamename>: Stops a game.')
        bot.replyout(channel, user, 'join <channel>: Joins a channel.')
        bot.replyout(channel, user, 'part <channel>: Parts a channel.')
        bot.replyout(channel, user, 'say <channel> <message>: Says <message> on <channel>.')
        bot.replyout(channel, user, 'do <channel> <action>: Performs <action> in <channel> (the /me command).')
        bot.replyout(channel, user, 'msg <user> <message>: Sends <user> a message.')        
        bot.replyout(channel, user, 'statsroll: Generates a DnD-style Stats set.')
        bot.replyout(channel, user, 'help: This help.')
