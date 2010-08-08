##
##    DnDStatsRoll - a plugin for pyGBot
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

import random
import re

from pyGBot import log
from pyGBot.BasePlugin import BasePlugin

class DnDStatsRoll(BasePlugin):
    __plugintype__ = "active"
    
    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        self.activeGame = False
        self.output = True
        self.modbreak = re.compile('([\+\-\*\/%^].*)')
        
    def rollStats(self):
        """ Roll up a standard 6x4d6 (drop lowest) D&D Stats roll."""
        rolls = [[random.randint(1,6) for i in range(0,4)] for j in range(0,6)]

        # Drop lowest of each 4d6 set and sum to produce 6 stat values
        stats = [sum(sorted(x)[1:]) for x in rolls] 
 
        return rolls, stats

    def pubout(self, channel, message):
        if self.output == True:
            self.bot.pubout(channel, message)

    # Event handlers for other users
    def user_join(self, channel, username):
        pass

    def user_part(self, channel, username):
        pass

    def user_quit(self, username, reason=""):
        pass

    def user_nickchange(self, username, newname):
        pass

    # Event handlers for this bot
    def bot_connect(self):
        pass

    def bot_join(self, channel):
        pass

    def bot_kicked(self, channel, kicker="", reason=""):
        pass

    def bot_disconnect(self):
        pass


    # Event handlers for incoming messages
    def msg_channel(self, channel, user, message):
        if message.lower().startswith(self.bot.nickname.lower()) and message.lower().find("statsroll") != -1:
            rolls, stats = self.rollStats()
                
            if message.lower().find("verbose") != -1:
                self.bot.pubout(channel, str(rolls))
            self.bot.pubout(channel, "Stats are: %s." % ', '.join(map(str, stats)))
            

    def msg_action(self, channel, user, message):
        pass

    def msg_private(self, user, message):
        if message.lower().startswith("statsroll"):
            rolls, stats = self.rollStats()
            

    def msg_notice(self, user, message):
        if message.lower().startswith("statsroll"):
            rolls, stats = self.rollStats()
            

    def channel_names(self, channel, nameslist):
        pass
