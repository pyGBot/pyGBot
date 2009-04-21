##
##    Calculate - a plugin for pyGBot
##    Copyright (C) 2008 Alex Soborov
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

from math import *

from pyGBot import log
from pyGBot.BasePlugin import BasePlugin

class Calculate(BasePlugin):
    __plugintype__ = "active"
    
    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        self.activeGame = False
        self.output = True

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
        if message.lower().startswith(self.bot.nickname.lower()) and message.find("calculate") != -1:
            try:
                #Restricted to simple math
                #calculate = eval(message.lower().split("calculate")[1].replace("^", "**"), {"__builtins__": {}})
                #Unrestricted
                calculate = eval(message.lower().split("calculate")[1].replace("^", "**"))
                
                # If I can, I want to allow math module functions, but nothing else. I'm not sure how to do that right now, but I'm testing what I can.
                #calculate = eval(message.lower().split("calculate")[1].replace("^", "**"), {"math": {}})
                # ALMOST WORKS- attempting math.function() returns "dict has no attribute "function"
                
                self.bot.pubout(channel, "The answer is %g." % calculate)
            except NameError:
                self.bot.pubout(channel, "Are you trying to do something you shouldn't?")
            except SyntaxError:
                self.bot.pubout(channel, "You did something wrong.")
            except ZeroDivisionError:
                self.bot.pubout(channel, "YOU'RE GOING TO DESTROY THE UNIVERSE YOU IDIOT! NO WAY IN HELL AM I DOING THAT!")

    def msg_action(self, channel, user, message):
        pass

    def msg_private(self, user, message):
        if message.lower().startswith("calculate"):
            try:
                calculate = eval(message.lower().split("calculate")[1].replace("^", "**"), {"__builtins__": {}})
                self.bot.privout(user, "The answer is %g." % calculate)
            except NameError:
                self.bot.privout(user, "Are you trying to do something you shouldn't?")
            except SyntaxError:
                self.bot.privout(user, "You did something wrong.")
            except ZeroDivisionError:
                self.bot.privout(user, "YOU'RE GOING TO DESTROY THE UNIVERSE YOU IDIOT! NO WAY IN HELL AM I DOING THAT!")

    def msg_notice(self, user, message):
        if message.lower().startswith("calculate"):
            try:
                calculate = eval(message.lower().split("calculate")[1].replace("^", "**"), {"__builtins__": {}})
                self.bot.noteout(user, "The answer is %g." % calculate)
            except NameError:
                self.bot.noteout(user, "Are you trying to do something you shouldn't?")
            except SyntaxError:
                self.bot.noteout(user, "You did something wrong.")
            except ZeroDivisionError:
                self.bot.noteout(user, "YOU'RE GOING TO DESTROY THE UNIVERSE YOU IDIOT! NO WAY IN HELL AM I DOING THAT!")


    def channel_names(self, channel, nameslist):
        pass
