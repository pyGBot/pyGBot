##
##    pyGBot - Versatile IRC Bot
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

from pyGBot import log
from pyGBot.BasePlugin import BasePlugin
import logging

class Log2channel(BasePlugin):
    def __init__(self, bot, options):
        BasePlugin.__init__(bot, options)
        
        try:
            self.channel = options['channel']
        except KeyError:
            log.logger.error("Log2channel: No log channel specified")
        
        self.format = logging.Formatter('%(asctime)s: %(levelname)s %(message)s')
        self.handler = None
        self.active = False
        

    def activate(self, channel=None):
        """ Called when the plugin is activated. Adds a channel handler to the
        logger. """
        self.active = True
        self.bot.join(self.channel)
        return True

    def deactivate(self, channel=None):
        """ Called when the plugin is deactivated. Removes the channel handler
        from the logger. """
        removeChannelHandler()
        self.active = False
        return True

    # Event handlers for this bot
    def bot_connect(self):
        """ Called upon connecting to the server. Join the log channel. """
        if self.active:
            self.bot.join(self.channel)

    def bot_join(self, channel):
        """ Called upon joining a channel. If joining the log channel, add a
        channel handler to the logging object. """
        if self.active and channel == self.channel:
            self.addChannelHandler()

    def bot_part(self, channel):
        """ Called upon parting a channel. If parting the log channel, remove
        the channel handler from the logging object. """
        if self.active and channel == self.channel:
            self.removeChannelHandler()

    def bot_kicked(self, channel, kicker="", reason=""):
        """ Called upon being kicked from a channel. If kicked from the log
        channel, remove the channel handler from the logging object and attempt
        to rejoin. """
        if self.active and channel == self.channel:
            self.removeChannelHandler()
            self.bot.join(self.channel)

    def bot_disconnect(self):
        """ Called upon disconnecting from the server. Remove the channel
        handler from the logging object. """
        self.removeChannelHandler()
    
    # Log handler manipulation
    def addChannelHandler():
        """ Adds an IRC channel handler to the bot logging object. """
        
        if self.handler != None:
            self.removeChannelHandler()
        
        channelStream = ChannelStream(self.bot, self.channel)
        self.handler = logging.StreamHandler(channelStream)
        self.handler.setFormatter(self.format)
        self.handler.setLevel(logging.INFO) # never log debug messages in channel
        log.logger.addHandler(self.handler)
    
    def removeChannelHandler():
        """ Removes the currently registered IRC channel handler from the bot
        logging object. """
        
        if self.handler != None:
            log.logger.removeHandler(self.handler)
            self.handler = None

class ChannelStream
    """ A minimalistic file-like class for use with logging.StreamHandler for
    logging to an IRC channel. """
    
    def __init__(self, bot, channel)
        """ Store the bot object and channel name. """
        self.client = bot
        self.channel = channel
        
    def write(self, msg)
        """ Write a string to the stream. This outputs to the channel. """
        self.client.pubout(self.channel, msg)
    
    def flush(self)
        """ Flush buffer. For ChannelStream, this has no effect. """
        pass
