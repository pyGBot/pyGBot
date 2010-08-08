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

from datetime import datetime

from elixir import *

metadata.bind = "sqlite:///seen.sqlite"

SeenEventTypes = dict(map(reversed,enumerate("Join Part Quit Kick Nick Say Do".split())))

class SeenEvent(Entity):
    user = Field(Unicode(30), primary_key=True)
    channel = Field(Unicode(100), primary_key=True)
    type = Field(Unicode(8))
    message = Field(UnicodeText)
    timestamp = Field(DateTime, primary_key=True)
    
    def __repr__(self):
        return ('<SeenEvent %s %s %s>' % (self.user, self.channel, self.timestamp)).encode('ascii','replace')

setup_all()
create_all()


################################################################################
## 
## Plugin
## 
################################################################################
from pyGBot.BasePlugin import BasePlugin


class Seen(BasePlugin):
    def __init__(self, bot, options):
        self.bot = bot
        self.active = False

    def activate(self, channel=None):
        """
        Called when the plugin is activated.
        """
	self.active = True
        return True

    def deactivate(self, channel=None):
        """
        Called when the plugin is deactivated.
        """
        self.active = False
        return True

    def get_latest(self, username, channel=None):
        if channel is None:
            try:
                return SeenEvent.query.filter_by(user=unicode(username)).order_by("timestamp DESC")[0]
            except IndexError:
                raise IndexError("I'm sorry, I haven't seen that user.")
        else:
            try:
                return SeenEvent.query.filter_by(user=unicode(username),channel=unicode(channel)).order_by("timestamp DESC")[0]
            except IndexError:
                raise IndexError("I'm sorry, I haven't seen that user on that channel.")

    # Event handlers for other users
    def user_join(self, channel, username):
        if self.active:
            SeenEvent(user=unicode(username), channel=unicode(channel), type=u'Join', timestamp=datetime.now())
            session.commit()

    def user_part(self, channel, username):
        if self.active:
            SeenEvent(user=unicode(username), channel=unicode(channel), type=u'Part', timestamp=datetime.now())
            session.commit()

    def user_kicked(self, channel, username, kicker, message=""):
        if self.active:
            SeenEvent(user=unicode(username), channel=unicode(channel), type=u'Kick', timestamp=datetime.now(), message=unicode(message))
            session.commit()

    def user_quit(self, username, reason=""):
        if self.active:
            SeenEvent(user=unicode(username), channel=u'', type=u'Quit', timestamp=datetime.now(), message=unicode(reason))
            session.commit()

    def user_nickchange(self, username, newname):
        if self.active:
            SeenEvent(user=unicode(username), channel=u'', type=u'NickFrom', timestamp=datetime.now(), message=u'%s -> %s' % (username, newname))
            SeenEvent(user=unicode(newname), channel=u'', type=u'NickTo', timestamp=datetime.now(), message=u'%s -> %s' % (username, newname))
            session.commit()

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
        if self.active:
            SeenEvent(user=unicode(user), channel=unicode(channel), type=u'Say', timestamp=datetime.now(), message=unicode(message))
            session.commit()

    def msg_action(self, channel, user, message):
        if self.active:
            SeenEvent(user=unicode(user), channel=unicode(channel), type=u'Do', timestamp=datetime.now(), message=unicode(message))
            session.commit()

    def msg_private(self, user, message):
        pass

    def msg_notice(self, user, message):
        pass

    def channel_names(self, channel, nameslist):
        pass

    def timer_tick(self):
        pass
