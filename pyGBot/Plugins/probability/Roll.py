##
##    Roll - a plugin for pyGBot
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

class Roll(BasePlugin):
    __plugintype__ = "active"
    
    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        self.activeGame = False
        self.output = True
        self.modbreak = re.compile('([\+\-\*\/%^].*)')
        
    def rollDice(self, message):
        param = message.partition("roll")[2].split()[0].rstrip(",.?").lower()
     
        sections = self.modbreak.split(param, 1)[:2]
        numdice, numsides = sections[0].split('d')
     
        numdice = int(numdice)
        if numdice > 75:
            return None, None, None, None, 1
     
        if numsides != 'f':
            numsides = int(numsides)
            if numsides > 10000:
                return None, None, None, None, 2
 
        if len(sections) > 1:
            mod = sections[1].replace("^", "**")
        else:
            mod = ''
 
        if numsides == 'f':
            bottom = -1
            top = 1
        else:
            bottom = 1
            top = numsides
 
        stack = []
        for i in range(0, numdice):
            stack.append(random.randint(bottom, top))
 
        subtotal = sum(stack)
 
        exec 'modtotal = subtotal %s' % mod
 
        rolls = ', '.join(map(str,stack))
 
        return rolls, subtotal, modtotal, mod, 0

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
        if message.lower().startswith(self.bot.nickname.lower()) and message.find(" roll ") != -1:
            rolls, subtotal, modtotal, mod, status = self.rollDice(message)
            
            if status == 0:
                if mod != '':
                    mod = mod.replace("**", "^")
                    self.bot.pubout(channel, "Rolled %s for a subtotal of %d. With modifiers of %s, the total is %d" % (rolls, subtotal, mod, modtotal))
                else:
                    self.bot.pubout(channel, "Rolled " + rolls + " for a total of %i." % modtotal)
            elif status == 1:
                self.bot.pubout(channel, "That's too many dice! I won't roll more than 75 at once.")
            elif status == 2:
                self.bot.pubout(channel, "Why would you ever need dice with that many sides? I'm not rolling this.")

    def msg_action(self, channel, user, message):
        pass

    def msg_private(self, user, message):
        if message.lower().startswith("roll "):
            rolls, subtotal, modtotal, mod, status = self.rollDice(message)
            
            if status == 0:
                if mod != '':
                    mod = mod.replace("**", "^")
                    self.bot.privout(user, "Rolled %s for a subtotal of %d. With modifiers of %s, the total is %d" % (rolls, subtotal, mod, modtotal))
                else:
                    self.bot.privout(user, "Rolled " + rolls + " for a total of %i." % modtotal)
            elif status == 1:
                self.bot.privout(user, "That's too many dice! I won't roll more than 75 at once.")
            elif status == 2:
                self.bot.privout(user, "Why would you ever need dice with that many sides? I'm not rolling this.")

    def msg_notice(self, user, message):
        if message.lower().startswith("roll "):
            rolls, subtotal, modtotal, mod, status = self.rollDice(message)
            
            if status == 0:
                if mod != '':
                    mod = mod.replace("**", "^")
                    self.bot.noteout(user, "Rolled %s for a subtotal of %d. With modifiers of %s, the total is %d" % (rolls, subtotal, mod, modtotal))
                else:
                    self.bot.noteout(user, "Rolled " + rolls + " for a total of %i." % modtotal)
            elif status == 1:
                self.bot.noteout(user, "That's too many dice! I won't roll more than 75 at once.")
            elif status == 2:
                self.bot.noteout(user, "Why would you ever need dice with that many sides? I'm not rolling this.")

    def channel_names(self, channel, nameslist):
        pass
