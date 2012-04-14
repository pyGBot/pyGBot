##
##    Plugins.system.Log2channel - Log-to-Channel Plugin
##    Author: Marc-Alexandre Chan <laogeodritt AT arenthil DOT net>
##    Date: 1 March 2012
##

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
from pyGBot.core import CHANNEL_PREFIXES
from pyGBot.BasePlugin import BasePlugin
from twisted.internet import reactor
import logging

class Log2channel(BasePlugin):
    """ This plugin allows pyGBot to log to a channel. This can be useful, for
    example, to allow users or ops to monitor changes that users in the main
    channel make to a factoid database. This obeys the loglevel property, but
    will never log debug messages to the channel even at loglevel = debug.

    Configuration options (pyGBot.ini):
    [Plugins.system.Log2channel]
    channel: channel to log to. Do NOT include the # character in front.
    loglevel: 'warning' or 'info', same effect as loglevel in [IRC]. If the
        loglevel option in [IRC] is less verbose than the one here, that one is
        used instead.
    logformat: The log format string. See the fmt arg of the logging.Formatter
        constructor in the Python docs. Default: "%(asctime)s: %(levelname)s
        %(message)s"
    dateformat: The date/time format used for "%(asctime)s" in the logformat.
        Uses the strftime syntax. Default: "%H:%M:%S"
    """

    # default settings
    logformat  = '%(asctime)s: %(levelname)s %(message)s'
    dateformat = '%H:%M:%S'

    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)

        # Get channel
        try:
            if options['channel'][0] not in CHANNEL_PREFIXES:
                self.channel = '#' + options['channel']
            else:
                self.channel = options['channel']
        except KeyError, IndexError:
            self.channel = None
            log.logger.error("Log2channel: No log channel specified")

        # Set log level (never more verbose than logging.INFO)
        try:
            if options['loglevel'].lower() == 'warning':
                self.loglevel = logging.WARNING
            else:
                self.loglevel = logging.INFO
        except KeyError:
            self.loglevel = logging.INFO

        # Get the formatting strings from config
        if 'logformat' in options:
            self.logformat = options['logformat']
        if 'dateformat' in options:
            self.dateformat = options['dateformat']

        self.format = logging.Formatter(self.logformat, self.dateformat)
        self._handler = None
        self._active = False

    def activate(self, channel=None):
        """ Called when the plugin is activated. Adds a channel handler to the
        logger. """
        if self.channel:
            self._active = True
            return True
        else:
            return False

    def deactivate(self, channel=None):
        """ Called when the plugin is deactivated. Removes the channel handler
        from the logger. """
        removeChannelHandler()
        self._active = False
        return True

    # Event handlers for this bot
    def bot_connect(self):
        """ Called upon connecting to the server. Join the log channel. """
        if self._active:
            self.bot.join(self.channel)

    def bot_join(self, channel):
        """ Called upon joining a channel. If joining the log channel, add a
        channel handler to the logging object. """
        if self._active and channel == self.channel:
            self.addChannelHandler()

    def bot_part(self, channel):
        """ Called upon parting a channel. If parting the log channel, remove
        the channel handler from the logging object. """
        if self._active and channel == self.channel:
            self.removeChannelHandler()

    def bot_kicked(self, channel, kicker="", reason=""):
        """ Called upon being kicked from a channel. If kicked from the log
        channel, remove the channel handler from the logging object and attempt
        to rejoin. """
        if self._active and channel == self.channel:
            self.removeChannelHandler()
            self.bot.join(self.channel)

    def bot_disconnect(self):
        """ Called upon disconnecting from the server. Remove the channel
        handler from the logging object. """
        self.removeChannelHandler()

    # Log handler manipulation
    def addChannelHandler(self):
        """ Adds an IRC channel handler to the bot logging object. """

        if self._handler != None:
            self.removeChannelHandler()

        channelStream = ChannelStream(self.bot, self.channel)
        self._handler = logging.StreamHandler(channelStream)
        self._handler.setFormatter(self.format)
        self._handler.setLevel(self.loglevel)
        log.logger.addHandler(self._handler)

    def removeChannelHandler(self):
        """ Removes the currently registered IRC channel handler from the bot
        logging object. """

        if self._handler != None:
            log.logger.removeHandler(self._handler)
            self._handler = None

class ChannelStream:
    """ A minimalistic file-like class for use with logging.StreamHandler for
    logging to an IRC channel. Implements queuing and delayed sending to
    prevent proper bot messages from being delayed by a large number of log
    messages (worst-case: bot messages will alternate with log messages). """

    # Amount of delay before the first log msg in queue (factor of bot.lineRate)
    _initialDelayFactor = 2
    # Amount of delay for subsequent log msg in queue (factor of bot.lineRate)
    _serialDelayFactor = 1

    def __init__(self, bot, channel):
        """ Store the bot object and channel name. """
        self.client = bot
        self.channel = channel

        self._queue = []
        self._queueEmptying = False
        self._initialDelay = self._initialDelayFactor * self.client.lineRate
        self._serialDelay  = self._serialDelayFactor * self.client.lineRate

    def write(self, msg):
        """ Write a string to the stream. This outputs to the channel. """
        # rm newlines - sends as multiple msgs
        msg = msg.replace('\n', ' ').strip()

        if not self.client.lineRate:
            self.client.pubout(self.channel, msg)
        else:
            self._queuePush(msg)
            self._queueSchedule()

    def flush(self):
        """ Flush buffer. For ChannelStream, this has no effect. """
        pass

    def _queuePush(self, msg):
        """ Pushes a message onto the queue. """
        self._queue.append(msg)

    def _queueSchedule(self):
        """ Schedule the next message to send from the queue. """
        if self._queue:
            if self._queueEmptying:
                # schedule only if existing call has already been executed
                if not self._queueEmptying.active():
                    reactor.callLater(self._serialDelay, self._queueSend)
            else:
                reactor.callLater(self._initialDelay, self._queueSend)
        else:
            self._queueEmptying = None

    def _queueSend(self):
        """ Output the next message to the channel and schedules the
        subsequent message to send from the queue. """
        if self._queue:
            self.client.pubout(self.channel, self._queue.pop(0))
        self._queueSchedule()