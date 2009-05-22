##
##    Commands - a plugin for pyGBot
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
from pyGBot.BasePlugin import BasePlugin

from pyGBot.Plugins.system.Auth import AuthLevels as AL

class BaseCommand:
    """Static base class for one-line commands.
    Derive this class to create specific commands.
    """
    level = AL.User
    def __init__(self, bot, channel, user, args):
        pass

class Commands(BasePlugin):
    __plugintype__ = "active"

    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        if self.bot.plugins.has_key('system.Auth') == False:
            raise StandardError('Unable to load Auth plugin. Please ensure it is loaded first.')

        if options.has_key('prefix'):
            self.cmdprefix = options['prefix']
        else:
            self.cmdprefix = '^'
        self.commands = {}
        
        for friendlyname, commandname in options.iteritems():
            if not friendlyname.startswith('_'):
                log.logger.info("Importing command " + commandname + " with friendly name " + friendlyname)
                command = __import__("pyGBot.Plugins.system.CommandSpec." + commandname, fromlist = [commandname])
                self.commands[friendlyname] = getattr(command, commandname)
            
    def pubout(self, channel, message):
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
        if message.startswith(self.cmdprefix):
            self.processMessage(channel, user, message[len(self.cmdprefix):])

    def msg_action(self, channel, user, message):
        pass

    def msg_private(self, user, message):
        if message.startswith(self.cmdprefix):
            self.processMessage(None, user, message[len(self.cmdprefix):])

    def msg_notice(self, user, message):
        pass

    # MESSAGE PROCESSING
    def processMessage(self, channel, user, message):
        elems = message.split(' ', 1)
        command = elems[0]
        if len(elems) > 1:
            arg = elems[1]
        else:
            arg = ""

        get_userlevel = self.bot.plugins['system.Auth'].get_userlevel

        if self.commands.has_key(command) == False:
            self.bot.noteout(user, 'Command not recognised: %s' % command)
        elif get_userlevel(user) < self.commands[command].level:
            self.bot.noteout(user, 'Insufficient access level for command: ' + command + ' Required level: ' + str(self.commands[command].level) + ' Your level: ' + str(get_userlevel(user)))
        else:
            self.commands[command](self.bot, channel, user, arg)
