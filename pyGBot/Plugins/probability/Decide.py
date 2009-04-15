##
##    Decide - a plugin for pyGBot
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

from pyGBot import log
from random import choice
from pyGBot.BasePlugin import BasePlugin

class Decide(BasePlugin):
    __plugintype__ = "active"
    
    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        self.activeGame = False
        self.output = True
        
    def decideFunction(self, message):
        decide = message[14:]
        decide = decide.split(", ")
        
        if decide[0].find(" and ") <> -1:
            decide = decide[0].partition(" and ")
            decide = [decide[0], decide[2]]
            decide[0] = decide[0].rstrip(" ")
            decide[1] = decide[1].lstrip(" ")
            decide[1] = decide[1].rstrip(".")
        else:
            decide[len(decide) - 1] = decide[len(decide) - 1][4:].rstrip(".")
            
        return decide

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

    def user_nickchange(self, channel, username, newname):
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
        if message.lower().startswith(self.bot.nickname.lower() + ", decide between "):
            self.bot.pubout(channel, "I choose: %s." % choice(self.decideFunction(message[len(self.bot.nickname + ", "):])))
            
    def msg_action(self, channel, user, message):
        pass

    def msg_private(self, user, message):
        if message.lower().startswith("decide between "):
            self.bot.privout(user, "I choose: %s." % choice(self.decideFunction(message)))

    def msg_notice(self, user, message):
        if message.lower().startswith("decide between "):
            self.bot.noteout(user, "I choose: %s." % choice(self.decideFunction(message)))

    def channel_names(self, channel, nameslist):
        pass
