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

twistedversion = '1'
try:
    from twisted import __version__ as twistedversion
except ImportError:
    #assume a pre-2.0 version of Twisted
    from twisted.protocols import irc

if int(twistedversion[0]) >= 2:
    from twisted.words.protocols import irc

from twisted.internet import reactor, protocol

import sys
import time
import threading

from contrib.configobj import ConfigObj, ConfigObjError

from pyGBot import log
from pyGBot.PluginEvents import PluginEvents

class GBot(irc.IRCClient):
    ''' An IRC Texas Holdem tournament  dealer'''

    def pubout(self, channel, msg):
        self.say(channel=channel, message=msg)
        
        # strip color codes
        log.chatlog.info('[PUB->%s]%s' % (channel, stripcolors(msg)))

    def privout(self, user, msg):
        self.msg(user=user, message=msg)
        
        # strip color codes
        log.chatlog.info('[PRV->%s]%s' % (user, stripcolors(msg)))

    def noteout(self, user, msg):
        self.notice(user=user, message=msg)

        # strip color codes
        log.chatlog.info('[NTE->%s]%s' % (user, stripcolors(msg)))

    def actout(self,channel, msg):
        self.me(channel=channel, action=msg)

        # strip color codes
        log.chatlog.info('[ACT->%s]%s' % (channel, stripcolors(msg)))

    def loadPlugins(self, conf):
        if conf.has_key('Plugins') == False:
            return

        pluginnames = conf['Plugins'].keys()
        for name in pluginnames:
            modname, classname = name.split('.')
            plugin = self.loadPluginFromFile(modname, classname, conf)

            self.plugins[name] = plugin

    def loadPluginFromFile(self, pluginmodule, pluginname, conf):
        log.logger.info("Loading plugin " + pluginname)

        if conf.has_key('Plugins.' + pluginmodule + '.' + pluginname):
            options = conf['Plugins.' + pluginmodule + '.' + pluginname]
        else:
            options = []

        exec "from Plugins." + pluginmodule + "." + pluginname + " import " + pluginname
        exec "plugin = " + pluginname + "(self, options)"
        return plugin

    def activatePlugin(self, pluginname, channel=None):
        if self.plugins.has_key(pluginname) == False:
            log.logger.info('Error: Unable to activate plugin ' + pluginname)
            return

        log.logger.info("Activating %s" % pluginname)
        plugin = self.plugins[pluginname]

        if plugin.activate(channel) == False:
            log.logger.info('Error: Plugin %s returned false on activation.' % pluginname)
            return False

        for eventname in self.events.__events__:
            log.logger.debug("Testing for event handler " + eventname)
            if hasattr(plugin, eventname) == True:
                log.logger.debug("Adding event handler " + eventname + " from plugin " + pluginname)
                event = getattr(self.events, eventname)
                event += getattr(plugin, eventname)

        self.activeplugins.append(pluginname)
        return True

    def deactivatePlugin(self, pluginname, channel=None):
        if self.plugins.has_key(pluginname) == False:
            log.logger.info('Error: Unable to deactivate plugin ' + pluginname)
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
            log.logger.info('Error: Plugin %s returned false on deactivation.' % pluginname)
            return False
        else:
            self.activeplugins.remove(pluginname)
            return True

    def __init__(self):
        try:
            conf = ConfigObj('pyGBot.ini')
        except IOError, msg:
            print "Cant open config file: ", msg
            sys.exit(1)

        try:
            print "Opening log file..."
            log.addScreenHandler(log.logger, log.formatter)
            log.addLogFileHandler(log.logger,conf['IRC']['logfile'],log.formatter)
        except IOError, msg:
            print "Unable to open log file: ", msg
            print "Defaulting to local."
            log.addLogFileHandler(log.logger,'pyGBot.log',log.formatter)
        except KeyError:
            print "No log file config found. Defaulting to local."
            log.addLogFileHandler(log.logger,'pyGBot.log',log.formatter)

        try:
            print "Opening log file..."
            log.addLogFileHandler(log.chatlog,conf['IRC']['chatlogfile'],log.cformat)
        except IOError, msg:
            print "Unable to open log file: ", msg
            print "Defaulting to local."
            log.addLogFileHandler(log.chatlog,'chat.log',log.cformat)
        except KeyError:
            print "No log file config found. Defaulting to local."
            log.addLogFileHandler(log.chatlog,'chat.log',log.cformat)

        if conf.has_key('IRC') == False:
            print "Config file does not contain IRC connection information"
            sys.exit(1)


        if conf['IRC'].has_key('nick'):
            self.nickname = conf['IRC']['nick']
        if conf['IRC'].has_key('idpass'):
            self.idpass = conf['IRC']['idpass']
        if conf['IRC'].has_key('idnick'):
            self.idnick = conf['IRC']['idnick']

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
        self.loadPlugins(conf)
        self.activatePlugin('system.Startup')

        self.versionEnv = sys.platform

    #### connection callbacks
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        log.logger.info("[connected at %s]" %\
                        time.asctime(time.localtime(time.time())))

        # Call Event Handler
        self.events.bot_connect()

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        log.logger.info("[disconnected at %s:%s]" %\
              (time.asctime(time.localtime(time.time())), reason))

        # Call Event Handler
        self.events.bot_disconnect()


    #### event callbacks
    def signedOn(self):
        """Called when bot has succesfully signed on to server.
        """
        self.join(self.factory.channel)

    def regNickServ(self):
        if hasattr(self, 'opernick') and hasattr(self, 'operpass'):
            self.sendLine('OPER %s %s' % (self.opernick, self.operpass))
        
        # Identify to nickserv
        if hasattr(self, 'idnick') and hasattr(self, 'idpass'):
            self.privout('%s' % (self.idnick,), 'identify %s' % (self.idpass,))


    def joined(self, channel):
        """This will get called when the bot joins the channel.
        """
        log.logger.info('[I have joined %s]' % (channel,))
        self.channels.append(channel)

        # Set modes
        if hasattr(self, 'plusmodes'):
            self.mode(channel, True, self.plusmodes)
        if hasattr(self, 'minusmodes'):
            self.mode(channel, False, self.minusmodes)
            
        # Call Event Handler
        self.events.bot_join(channel)

    def left(self, channel):
        if channel in self.channels:
            self.channels.remove(channel)

    def kickedFrom(self, channel, kicker, message):
        if channel in self.channels:
            self.channels.remove(channel)

        self.events.bot_kicked(channel, kicker, message)

    def noticed(self, user, channel, msg):
        """This will get called when the bot receives a NOTICE.
        """
        user = user.split('!', 1)[0]
        log.chatlog.info('[NTE<-]<%s> %s' % (user, msg))

        # Call Event Handler
        self.events.msg_notice(user, msg)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message.
        """
        user = user.split('!', 1)[0]

        # Private message to me
        if channel.upper() == self.nickname.upper():
            if msg.startswith('auth'):
                outmsg = msg.split(' ')
                outmsg[2] = '*' * 8
                outmsg = ' '.join(outmsg)
                log.chatlog.info('[PRV<-]<%s> %s' % (user, outmsg))
            else:
                log.chatlog.info('[PRV<-]<%s> %s' % (user, msg))
            # Call Event Handler
            self.events.msg_private(user, msg)

        # Public message
        else:
            log.chatlog.info('[PUB<-]<%s> %s' % (user, msg))
            # Call Event Handler
            self.events.msg_channel(channel, user, msg)

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action.
        """
        user = user.split('!', 1)[0]
        log.chatlog.info('* %s %s' % (user, msg))

        # Call Event Handler
        self.events.msg_action(channel, user, msg)

    def userJoined(self, user, channel):
        """Called when I see another user joining a channel.
        """
        user = user.split('!', 1)[0]
        log.chatlog.info('%s joined %s' % (user, channel))

        # Call Event Handler
        self.events.user_join(channel, user)

    def userLeft(self, user, channel):
        """Called when I see another user leaving a channel.
        """
        user = user.split('!', 1)[0]
        log.chatlog.info('%s has left %s' % (user, channel))

        # Call Event Handler
        self.events.user_part(channel, user)

    def userKicked(self, user, channel, kicker, message):
        """Called when I see another user get kicked.
        """
        user = user.split('!', 1)[0]
        log.chatlog.info('%s was kicked from %s by %s (reason: %s)' % (user, channel, kicker, message))

        self.events.user_kicked(channel, user, kicker, message)

    def userQuit(self, user, quitMessage):
        """Called when I see another user disconnect from the network.
        """
        user = user.split('!', 1)[0]
        log.chatlog.info("%s has quit" % (user))

        # Call Event Handler
        self.events.user_quit(user, quitMessage)

    def userRenamed(self, oldname, newname):
        """A user changed their name from oldname to newname.
        """
        log.chatlog.info('%s is now known as %s' % (oldname, newname))

        # Call Event Handler
        self.events.user_nickchange(oldname, newname)

    def cprivmsg(self, chan, user, message):

        fmt = "CPRIVMSG %s %s :%%s" % (user, chan)
        self.sendLine(fmt % (message,))

    def cnotice(self, chan, user, message):

        fmt = "CNOTICE %s %s :%%s" % (user, chan)
        self.sendLine(fmt % (message,))

class GBotFactory(protocol.ClientFactory):
    """A factory for tbots.

    A new protocol instance will be created each time we connect to the server.
    """

    # the class of the protocol to build when new connection is made
    protocol = GBot

    def __init__(self, channel, filename):
        self.channel = channel
        self.filename = filename

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""

        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        log.logger.critical('connection failed: %s', (str(reason),))
        reactor.stop()

def stripcolors(inmsg):

    # strip color codes
    inmsg = inmsg.replace("\x02\x0301,00", '')
    inmsg = inmsg.replace("\x02\x0302,00", '')
    inmsg = inmsg.replace("\x02\x0303,00", '')
    inmsg = inmsg.replace("\x02\x0304,00", '')
    inmsg = inmsg.replace("\x0F", '')
    return inmsg


def run():
    try:
        conf = ConfigObj('pyGBot.ini')
    except IOError, msg:
        print "Cant open config file: ", msg
        sys.exit(1)

    if conf.has_key('IRC') == False:
        print "Config file does not contain IRC connection information"
        sys.exit(1)

    try:
        channel = conf['IRC']['channel']
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

    print "Initialising Factory..."
    # create factory protocol and application
    fact = GBotFactory(channel, 'UNUSED')

    print "Connecting..."

    try:
        # connect factory to this host and port
        if localaddr and localport:
            reactor.connectTCP(host, port, fact, bindAddress=(localaddr, localport))
        else:
            reactor.connectTCP(host, port, fact)

        # run bot
        reactor.run()
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise


