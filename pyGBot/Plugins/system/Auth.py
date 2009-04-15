##
##    Auth - a plugin for pyGBot
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

import hashlib

from pyGBot import log
from pyGBot.BasePlugin import BasePlugin
from contrib.configobj import ConfigObj

class AuthLevels:
    User = 0
    Mod = 100
    Admin = 200

class User:
    def __init__(self, host, level = AuthLevels.User):
        self.nick = host.split('!', 1)[0]
        #self.host = host.split('!', 1)[1]
        self.level = level

class Auth(BasePlugin):
    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        self.users = {}
        self.conf = ConfigObj("users.ini")
    
    def get_userlevel(self, user):
        if self.users.has_key(user):
            return self.users[user].level
        else:
            newuser = User(user)
            self.users[user] = newuser
            return newuser.level
    
    def set_userlevel(self, user, level):
        if self.users.has_key(user):
            self.users[user].level = level
        else:
            newuser = User(user)
            newuser.level = level
            self.users[user] = newuser
    
    # Event handlers for other users
    def user_join(self, channel, username):
        pass

    def user_part(self, channel, username):
        pass

    def user_quit(self, user, reason=""):
        if self.users.has_key(user):
            del self.users[user]

    def user_nickchange(self, channel, username, newname):
        if self.users.has_key(username):
            self.users[newname] = self.users[username]
            del self.users[username]
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
        pass

    def msg_action(self, channel, user, message):
        pass

    def msg_private(self, user, message):
        if message.lower().startswith('auth'):
            cmd, uname, password = message.rsplit(' ',2)
            if self.get_passhash(uname) == hashlib.sha1(password + 'pygb0t').hexdigest():
                authlevel = self.get_authlevel(uname)
                if authlevel != None:
                    self.set_userlevel(user, self.get_authlevel(uname))
                    self.bot.noteout(user, 'Successfully authed.')
                    log.logger.info('Auth: Authorised user %s at level %d.' % (user, authlevel))
                else:
                    self.bot.noteout(user, 'Invalid user level.')
                    log.logger.info('Auth: Invalid user level for user %s' % user)
            else:
                self.bot.noteout(user, 'Incorrect user name or password.')

    def msg_notice(self, user, message):
        pass

    def channel_names(self, channel, nameslist):
        log.logger.info("Users on #" + channel + ": " + ', '.join(nameslist))

    def get_passhash(self, uname):
        if self.conf.has_key(uname) and self.conf[uname].has_key('passhash'):
            return self.conf[uname]['passhash']
    
    def get_authlevel(self, uname):
        if self.conf.has_key(uname) and self.conf[uname].has_key('userlevel'):
            if hasattr(AuthLevels, self.conf[uname]['userlevel']):
                return getattr(AuthLevels, self.conf[uname]['userlevel'])
            else:
                return None
        else:
            return None
 
