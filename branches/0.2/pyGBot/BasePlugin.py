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

################################################################################
## 
## Plugin
## 
################################################################################

class BasePlugin:
    def __init__(self, bot, options):
        self.bot = bot

    def activate(self, channel=None):
        """
        Called when the plugin is activated.
        """
        return True

    def deactivate(self, channel=None):
        """
        Called when the plugin is deactivated.
        """
        return True

    # Event handlers for other users
    def user_join(self, channel, username):
        pass

    def user_part(self, channel, username):
        pass

    def user_kicked(self, channel, username, kicker, message=""):
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

    def bot_part(self, channel):
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
        pass

    def msg_notice(self, user, message):
        pass

    def channel_names(self, channel, nameslist):
        pass

    def timer_tick(self):
        pass
