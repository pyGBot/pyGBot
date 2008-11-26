##
##    Poker - a plugin for pyGBot, based on pyTBot
##    Copyright (C) 2008 Morgan Lokhorst-Blight, Alex Soborov, Paul Rotering
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

import log
from BasePlugin import BasePlugin

from .pokerfiles.tourney import Tourney
from .pokerfiles.command import Command

class Poker(BasePlugin):
    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        self.tourney = []

    def pubout(self, msg):
        self.bot.pubout(self.channel, msg)

    def privout(self, user, msg):
        self.bot.privout(user, msg)

    def noteout(self, user, msg):
        self.bot.noteout(user, msg)

    def activate(self, channel=None):
        if channel == None:
            log.logger.info("Can't activate poker game without channel")
            return False
        else:
            self.channel = channel
            self.tourney = Tourney(self.pubout, self.privout, self.noteout)
            return True

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
        self.processmessage(user, message)

    def msg_action(self, channel, user, message):
        pass

    def msg_private(self, user, message):
        self.processmessage(user, message)

    def msg_notice(self, user, message):
        pass

    def channel_names(self, channel, nameslist):
        pass

    def processmessage(self, user, message):
        fulluser = user
        user = user.split('!', 1)[0]
        
        l = message.strip().split()

        if len(l) > 1 and l[0] == 'p':

            cmd = Command(user, l, fulluser)
            if cmd.arg == 'ERROR':
                self.privout(user,'Bad or missing argument')
            else:
                log.logger.debug('Tourneybot:%s' % cmd)

                #FIXME: This should never be seen here as handflag is
                #dependent on the game.
                if cmd.handsflag:
                    self.tourney.handsflag = True
                else:
                    self.tourney.handsflag = False

                self.tourney.incmd(cmd)
