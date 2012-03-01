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

# pyGBot imports
from contrib.configobj import ConfigObj, ConfigObjError

from pyGBot import log
from pyGBot.PluginEvents import PluginEvents

# Twisted imports
twistedversion = '1'
try:
    from twisted import __version__ as twistedversion
except ImportError:
    #assume a pre-2.0 version of Twisted
    from twisted.protocols import irc
twistedmajor = int(twistedversion.split('.')[0])

# Standard library imports
import sys
import time
import threading

if twistedmajor >= 2:
    from twisted.words.protocols import irc

from twisted.internet import reactor, protocol, task

class GBot(irc.IRCClient):
    ''' No longer just an IRC Texas Holdem tournament dealer'''

    ############################################################################
    # Public Plugin API Methods
    ############################################################################
    def pubout(self, channel, msg):
        """ Send a message to a channel. """
        msgOut = encodeOut(msg)
        channelOut = encodeOut(channel)
        self.say(channel=channelOut, message=msgOut)
        
        # strip color codes
        log.chatlog.info('[PUB->%s]%s' % (channelOut, stripcolors(msgOut)))

    def privout(self, user, msg):
        """ Send a message to a user. """
        msgOut = encodeOut(msg)
        userOut = encodeOut(user)
        self.msg(user=userOut, message=msgOut)
        
        # strip color codes
        log.chatlog.info('[PRV->%s]%s' % (userOut, stripcolors(msgOut)))

    def replyout(self, channel, user, msg):
        """ Send a reply. If channel is None, the reply is sent to the user;
        otherwise, it is sent to the channel. Use this in plugins or commands
        when an incoming message can be either from a channel or a user and the
        outgoing message should be resent to the source. """
        
        msgOut = encodeOut(msg)
        userOut = encodeOut(user)
        channelOut = encodeOut(channel)
        if (channel is None):
            self.privout(userOut, msgOut)
        else:
            self.pubout(channelOut, msgOut)

    def noteout(self, user, msg):
        """ Send a notice to a user. """
        msgOut = encodeOut(msg)
        userOut = encodeOut(user)
        self.notice(user=userOut, message=msgOut)

        # strip color codes
        log.chatlog.info('[NTE->%s]%s' % (userOut, stripcolors(msgOut)))
        
    def invite(self, user, channel):
        """ Send a channel invite to a user. """
        userOut = encodeOut(user)
        channelOut = encodeOut(channel)
        self.sendLine("INVITE %s %s" % (userOut, channelOut))
        
        log.chatlog.info('[INVITE->%s] %s' % (userOut, channelOut))
        
    def join(self, channel, key=None):
        """ Join a channel. """
        if key:
            keyOut = encodeOut(key)
            irc.IRCClient.join(channelOut, keyOut)
        else:
            irc.IRCClient.join(channelOut)

    def actout(self,channel, msg):
        """ Send an action (/me) to a channel. """
        msgOut = encodeOut(msg)
        channelOut = encodeOut(channel)
        self.me(channel=channelOut, action=msgOut)

        # strip color codes
        log.chatlog.info('[ACT->%s]%s' % (channelOut, stripcolors(msgOut)))

    def modestring(self, target, modestring):
        """ Set a mode string on a user or channel. """
        self.sendLine("MODE %s %s" % (target, modestring))

        log.chatlog.info('[MODE] %s %s' % (target, modestring))

    def cprivmsg(self, channel, user, message):
        """ Send a CPRIVMSG. This allows channel ops to bypass server flood
        limits when messaging users in their channel. """
        msgOut = encodeOut(msg)
        userOut = encodeOut(user)
        channelOut = encodeOut(channel)
        fmt = "CPRIVMSG %s %s :%%s" % (userOut, channelOut)
        self.sendLine(fmt % (message,))

    def cnotice(self, channel, user, message):
        """ Send a CNOTICE. This allows channel ops to bypass server flood
        limits when sending a notice to users in their channel. """
        msgOut = encodeOut(msg)
        userOut = encodeOut(user)
        channelOut = encodeOut(channel)
        fmt = "CNOTICE %s %s :%%s" % (userOut, channelOut)
        self.sendLine(fmt % (messageOut,))

    ############################################################################
    # Plugin Handling Methods
    ############################################################################
    def loadPlugins(self, conf):
        """ (private) Load all registered plugins. """
        if conf.has_key('Plugins') == False:
            return

        pluginnames = conf['Plugins'].keys()
        for name in pluginnames:
            modname, classname = name.split('.')
            plugin = self.loadPluginFromFile(modname, classname, conf)

            self.plugins[name] = plugin

    def loadPluginFromFile(self, pluginmodule, pluginname, conf):
        """ (private) Load a plugin from its file and initialise it. """
        log.logger.info("Loading plugin %s", pluginname)

        if conf.has_key('Plugins.' + pluginmodule + '.' + pluginname):
            options = conf['Plugins.' + pluginmodule + '.' + pluginname]
        else:
            options = []

        # imports and returns the Plugins.{pluginmodule}.{pluginname} module object
        plugins_modobj = __import__('Plugins.{0}.{1}'.format(pluginmodule, pluginname),
                                    fromlist=[pluginname])
        # get the class object and then instantiate it
        plugin_class = getattr(plugin_modobj, pluginname)
        plugin = plugin_class(self, options)
        return plugin

    def activatePlugin(self, pluginname, channel=None):
        """ (private) Activate a loaded plugin. """
        if self.plugins.has_key(pluginname) == False:
            log.logger.error('Unable to activate plugin %s: plugin not loaded.', pluginname)
            return

        log.logger.info("Activating %s", pluginname)
        plugin = self.plugins[pluginname]

        if plugin.activate(channel) == False:
            log.logger.error('Plugin %s returned false on activation.', pluginname)
            return False

        for eventname in self.events.__events__:
            log.logger.debug("Testing for event handler %s", eventname)
            if hasattr(plugin, eventname) == True:
                log.logger.debug("Adding event handler %s from plugin %s.", eventname, pluginname)
                event = getattr(self.events, eventname)
                event += getattr(plugin, eventname)

        self.activeplugins.append(pluginname)
        return True

    def deactivatePlugin(self, pluginname, channel=None):
        """ (private) Deactivates a loaded plugin. """
        if self.plugins.has_key(pluginname) == False:
            log.logger.error('Unable to deactivate plugin ' + pluginname)
            return        

        log.logger.info("Deactivating %s" % pluginname)
        plugin = self.plugins[pluginname]

        for eventname in self.events.__events__:
            log.logger.debug("Testing for event handler " + eventname)
            if hasattr(plugin, eventname) == True:
                log.logger.debug("Removing event handler " + eventname + " from plugin " + pluginname)
                event = getattr(self.events, eventname)
                event -= getattr(plugin, eventname)

        if plugin.deactivate(channel) == False:
            log.logger.error('Plugin %s returned false on deactivation.' % pluginname)
            return False
        else:
            self.activeplugins.remove(pluginname)
            return True

    def __init__(self):
        """ Initialise GBot: load IRC connection info from the configuration,
        load plugins from the configuration, activate startup plugins, and
        initialise the plugin timer task."""
        # to delineate each launch in log file
        log.logger.info("Starting pyGBot...")

        log.logger.info("Loading config file...")
        try:
            conf = ConfigObj('pyGBot.ini')
        except IOError, msg:
            print "Cannot open config file: ", msg
            sys.exit(1)

        if conf.has_key('IRC') == False:
            print "Config file does not contain IRC connection information."
            sys.exit(1)

        if conf['IRC'].has_key('nick'):
            self.nickname = conf['IRC']['nick']
        if conf['IRC'].has_key('idpass'):
            self.idpass = conf['IRC']['idpass']
        if conf['IRC'].has_key('idnick'):
            self.idnick = conf['IRC']['idnick']

        if conf['IRC'].has_key('realname'):
            self.realname = conf['IRC']['realname']
        if conf['IRC'].has_key('usermodes'):
            self.usermodes = conf['IRC']['usermodes']

        if conf['IRC'].has_key('opernick'):
            self.opernick = conf['IRC']['opernick']
        if conf['IRC'].has_key('operpass'):
            self.operpass = conf['IRC']['operpass']

        if conf['IRC'].has_key('ircpass'):
            self.password = conf['IRC']['ircpass']
        if conf['IRC'].has_key('minusmodes'):
            self.minusmodes = conf['IRC']['minusmodes']
        if conf['IRC'].has_key('plusmodes'):
            self.plusmodes = conf['IRC']['plusmodes']

        if conf['IRC'].has_key('flooddelay'):
            self.lineRate = float(conf['IRC']['flooddelay'])

        if conf.has_key('version'):
            if conf['version'].has_key('name'):
                self.versionName = conf['version']['name']
            if conf['version'].has_key('number'):
                self.versionNum = conf['version']['number']

        self.whois = []

        self.channelusers = {}
        self.channels = []

        self.events = PluginEvents()

        self.plugins = {}
        self.activeplugins = []
        
        log.logger.info("Loading plugins...")
        self.loadPlugins(conf)
        
        log.logger.info("Activating startup plugins...")
        self.activatePlugin('system.Startup')

        self.timertask = task.LoopingCall(self.events.timer_tick)

        self.versionEnv = sys.platform

    ############################################################################
    # Connection Callbacks
    ############################################################################
    def connectionMade(self):
        """ Called when a connection is made. """
        irc.IRCClient.connectionMade(self)
        log.logger.info("[connected at %s]" %\
                        time.asctime(time.localtime(time.time())))

        self.timertask.start(1.0) # 1-second timer granularity

        # Call Event Handler
        self.events.bot_connect()

    def connectionLost(self, reason):
        """ Called when a connection is shut down. """
        irc.IRCClient.connectionLost(self, reason)
        log.logger.info("[disconnected at %s:%s]" %\
              (time.asctime(time.localtime(time.time())), reason))

        self.timertask.stop()

        # Call Event Handler
        self.events.bot_disconnect()

    ############################################################################
    # Event Callbacks
    ############################################################################
    def signedOn(self):
        """ Called when the bot has succesfully signed on to the server. """
        self.regNickServ()
        
        self.modestring(self.nickname, self.usermodes)
        
        for channel in self.factory.channel:
            self.join(channel)

    def regNickServ(self):
        """ (private) Identify with NickServ from the configuration info. """
        if hasattr(self, 'opernick') and hasattr(self, 'operpass'):
            self.sendLine('OPER %s %s' % (self.opernick, self.operpass))
        
        # Identify to nickserv
        if hasattr(self, 'idnick') and hasattr(self, 'idpass'):
            self.privout('%s' % (self.idnick,), 'identify %s' % (self.idpass,))


    def joined(self, channel):
        """ Called when the bot joins a channel. """
        log.logger.info('[I have joined %s]' % (channel,))
        self.channels.append(channel)

        # Set modes
        if hasattr(self, 'plusmodes'):
            self.mode(channel, True, self.plusmodes)
        if hasattr(self, 'minusmodes'):
            self.mode(channel, False, self.minusmodes)
        
        # Call Event Handler
        channelIn = decodeIn(channel)
        self.events.bot_join(channelIn)

    def left(self, channel):
        """ Called when the bot leaves a channel. """
        if channel in self.channels:
            self.channels.remove(channel)

    def kickedFrom(self, channel, kicker, message):
        """ Called when the bot is kicked from a channel. """
        if channel in self.channels:
            self.channels.remove(channel)

        channelIn = decodeIn(channel)
        kickerIn = decodeIn(kicker)
        messageIn = decodeIn(message)
        self.events.bot_kicked(channelIn, kickerIn, messageIn)

    def noticed(self, user, channel, msg):
        """ Called when the bot receives a NOTICE. """
        user = user.split('!', 1)[0]
        userIn = decodeIn(user)
        channelIn = decodeIn(channel)
        msgIn = decodeIn(msg)
        log.chatlog.info('[NTE<-]<%s> %s' % (user, msg))

        # Call Event Handler
        self.events.msg_notice(userIn, msgIn)

    def privmsg(self, user, channel, msg):
        """ Called when the bot receives a message (from channel or user). """
        user = user.split('!', 1)[0]
        userIn = decodeIn(user)
        channelIn = decodeIn(channel)
        msgIn = decodeIn(msg)

        # Private message to me
        if channel.upper() == self.nickname.upper():
            # If auth msg has password, censor it for logging
            if msgIn.startswith('auth'):
                msgNoPwd = msgIn.split(' ')
                if len(msgNoPwd) > 2:
                    msgNoPwd[2] = '*' * 8
                msgNoPwd = ' '.join(msgNoPwd)
                log.chatlog.info('[PRV<-]<%s> %s' % (user, msgNoPwd))
            else:
                log.chatlog.info('[PRV<-]<%s> %s' % (user, msg))
            # Call Event Handler
            self.events.msg_private(userIn, msgIn)

        # Public message
        else:
            log.chatlog.info('[PUB<-]<%s> %s' % (user, msg))
            # Call Event Handler
            self.events.msg_channel(channelIn, userIn, msgIn)

    def action(self, user, channel, msg):
        """ Called when the bot sees someone do an action (/me). """
        user = user.split('!', 1)[0]
        userIn = decodeIn(user)
        channelIn = decodeIn(channel)
        msgIn = decodeIn(msg)
        log.chatlog.info('* %s %s' % (user, msg))

        # Call Event Handler
        self.events.msg_action(channelIn, userIn, msgIn)

    def topicUpdated(self, user, channel, newTopic):
        """ Called when the bot sees the channel topic change. """
        user = user.split('!', 1)[0]
        userIn = decodeIn(user)
        channelIn = decodeIn(channel)
        newTopicIn = decodeIn(newTopic)
        log.chatlog.info('Topic for %s set by %s: %s' % (channel, user, newTopic))

        # Call Event Handler
        self.events.channel_topic(channelIn, userIn, newTopicIn)

    def userJoined(self, user, channel):
        """Called when the bot sees a user joining a channel. """
        user = user.split('!', 1)[0]
        userIn = decodeIn(user)
        channelIn = decodeIn(channel)
        log.chatlog.info('%s joined %s' % (user, channel))

        # Call Event Handler
        self.events.user_join(channelIn, userIn)

    def userLeft(self, user, channel):
        """Called when the bot sees a user leaving a channel. """
        user = user.split('!', 1)[0]
        userIn = decodeIn(user)
        channelIn = decodeIn(channel)
        log.chatlog.info('%s has left %s' % (user, channel))

        # Call Event Handler
        self.events.user_part(channelIn, userIn)

    def userKicked(self, user, channel, kicker, message):
        """ Called when the bot sees a user get kicked. """
        user = user.split('!', 1)[0]
        userIn = decodeIn(user)
        channelIn = decodeIn(channel)
        kickerIn = decodeIn(kicker)
        messageIn = decodeIn(message)
        
        log.chatlog.info('%s was kicked from %s by %s (reason: %s)' % (user, channel, kicker, message))

        self.events.user_kicked(channelIn, userIn, kickerIn, messageIn)

    def userQuit(self, user, quitMessage):
        """ Called when the bot sees a user disconnect from the network. """
        user = user.split('!', 1)[0]
        userIn = decodeIn(user)
        quitMsgIn = decodeIn(quitMessage)
        
        log.chatlog.info("%s has quit [%s]" % (user, quitMessage))
        
        # Call Event Handler
        self.events.user_quit(userIn, quitMsgIn)

    def userRenamed(self, oldname, newname):
        """Called when the bot sees a user change their nickname from oldname to
        newname. """
        oldnameIn = decodeIn(oldname)
        newnameIn = decodeIn(newname)
        log.chatlog.info('%s is now known as %s' % (oldname, newname))
        # Call Event Handler
        self.events.user_nickchange(oldnameIn, newnameIn)

class GBotFactory(protocol.ClientFactory):
    """A factory for tbots.

    A new protocol instance is created each time we connect to the server.
    """

    # the class of the protocol to build when new connection is made
    protocol = GBot

    def __init__(self, channel, filename):
        self.channel = channel
        self.filename = filename
        conf = ConfigObj('pyGBot.ini')
        
        # Open GBot log
        try:
            print "Opening pyGBot log file..."
            log.addScreenHandler(log.logger, log.formatter)
            log.addLogFileHandler(log.logger,conf['IRC']['logfile'], log.formatter)
        except IOError, msg:
            print "Unable to open log file: ", msg
            print "Defaulting to 'pyGBot.log'."
            log.addLogFileHandler(log.logger,'pyGBot.log', log.formatter)
        except KeyError:
            print "No log file specified in config. Defaulting to 'pyGBot.log'."
            log.addLogFileHandler(log.logger,'pyGBot.log', log.formatter)
        
        # set logging level
        try:
            if conf['IRC']['loglevel'].lower() == 'debug':
                log.logger.setLevel(logging.DEBUG)
            else if conf['IRC']['loglevel'].lower() == 'warning':
                log.logger.setLevel(logging.WARNING)
            # otherwise use the default level of INFO
        except KeyError:
            pass # no 'loglevel' key? use default level of INFO
        
        # open chat log
        try:
            print "Opening chat log file..."
            log.addLogFileHandler(log.chatlog,conf['IRC']['chatlogfile'], log.cformat)
        except IOError, msg:
            print "Unable to open log file: ", msg
            print "Defaulting to 'chat.log'."
            log.addLogFileHandler(log.chatlog,'chat.log', log.cformat)
        except KeyError:
            print "No log file config found. Defaulting to 'chat.log'."
            log.addLogFileHandler(log.chatlog,'chat.log', log.cformat)

    def clientConnectionLost(self, connector, reason):
        """ Called when a client's connection is shut down. Attempts to
        reconnect to the server. """

        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        """ Called when a client's connection fails. Log the error and exit. """
        log.logger.critical('connection failed: %s', (str(reason),))
        reactor.stop()

def stripcolors(inmsg):
    """ Strip color codes from a string. """
    log.logger.warning("DEPRECATED: pyGBot.stripcolors() is deprecated. Use StringUtils.stripFormatting() to strip IRC formatting from a string.")
    # TODO: Fix this and move this to stringutils
    inmsg = inmsg.replace("\x02\x0301,00", '')
    inmsg = inmsg.replace("\x02\x0302,00", '')
    inmsg = inmsg.replace("\x02\x0303,00", '')
    inmsg = inmsg.replace("\x02\x0304,00", '')
    inmsg = inmsg.replace("\x0F", '')
    return inmsg


def encodeOut(msg):
    """ Encode output text as a UTF-8 byte-string, replacing any invalid
    characters with '?'. If the msg argument is not a unicode string, return
    the argument. This allows correct output of Unicode characters. """
    # TODO: move to string utils, add backwards-compat call here
    if isinstance(msg, unicode):
        encMsg = msg.encode('utf-8', 'replace')
    else:
        encMsg = msg
    return encMsg

def decodeIn(msg):
    """ Decode input text as UTF-8, replacing any invalid characters with '?',
    and return a unicode string. If the msg argument is already a unicode
    string, return the argument. This allows plugins to correctly receive and
    handle unicode-type strings internally. """
    # TODO: move to string utils, add backwards-compat call here
    if isinstance(msg, unicode):
        decMsg = msg
    else:
        decMsg = msg.decode('utf-8', 'replace')
    return decMsg


def run():
    """ Run GBot. Called from the pyGBot bootstrap script. """
    try:
        conf = ConfigObj('pyGBot.ini')
    except IOError, msg:
        print "Cannot open config file: ", msg
        sys.exit(1)

    if conf.has_key('IRC') == False:
        print "Config file does not contain IRC connection information."
        sys.exit(1)

    try:
        channel = conf['IRC']['channel'].split(" ")
        host = conf['IRC']['host']
        port = int(conf['IRC']['port'])
    except ConfigObjError:
        print "Required IRC connection info missing or invalid."
        sys.exit(1)

    localport = None
    localaddr = None

    if conf['IRC'].has_key('localport'):
        localport = int(conf['IRC']['localport'])
    if conf['IRC'].has_key('localaddr'):
        localaddr = conf['IRC']['localaddr']
        
    # hacked in SSL config option
    sslconnect = False
    if conf['IRC'].has_key('ssl'):
        if conf['IRC']['ssl'].lower() == "true":
            sslconnect = True
            from twisted.internet import ssl

    print "Initialising Factory..."
    # create factory protocol and application
    fact = GBotFactory(channel, 'UNUSED')
    # "Doctor, how does SSL work?" "I HAVE NO IDEA!"
    if sslconnect:
        cfact = ssl.ClientContextFactory()

    print "Connecting..."

    try:
        # connect factory to this host and port
        # now with SSL hack!
        if sslconnect:
            if localaddr and localport:
                reactor.connectSSL(host, port, fact, cfact, bindAddress=(localaddr, localport))
            else:
                reactor.connectSSL(host, port, fact, cfact)
        else:
            if localaddr and localport:
                reactor.connectTCP(host, port, fact, bindAddress=(localaddr, localport))
            else:
                reactor.connectTCP(host, port, fact)

        # run bot
        reactor.run()
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
