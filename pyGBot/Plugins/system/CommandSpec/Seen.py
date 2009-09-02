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

from pyGBot import log
from pyGBot.Plugins.system.Commands import BaseCommand
from pyGBot.Plugins.system.Auth import AuthLevels as AL

def pubout(bot):
    def _out(target, message):
        bot.pubout(target, unicode(message).encode('ascii','replace'))
    return _out

def privout(bot):
    def _out(target, message):
        bot.privout(target, unicode(message).encode('ascii','replace'))
    return _out 

class Seen(BaseCommand):
    level = AL.User

    def __init__(self, bot, channel, user, args):
        if channel is None:
            out = privout(bot)
            target = user
        else:
            out = pubout(bot)
            target = channel

        args = args.strip().split()
        if not args:
            out(target, 'Command usage: seen <user> [channel]')
            return

        username = args[0]
        try:
            channel = args[1]
        except IndexError:
            channel = None

        try:
            event = bot.plugins['features.Seen'].get_latest(username, channel)
        except IndexError, e:
            out(target, e)
            return

        outmessage = "The user, %s, was last seen " % event.user
        if event.channel:
            outmessage += "on channel %s " % event.channel
        else:
            outmessage += "on this network "

        lastseen = datetime.now() - event.timestamp

        days = lastseen.days
        hours = lastseen.seconds / 3600
        minutes = (lastseen.seconds % 3600) / 60
        seconds = lastseen.seconds % 60

        timemessage = []
        if days != 0:
            timemessage.append("%i days" % days)
        if hours != 0:
            timemessage.append("%i hours" % hours)
        if minutes != 0:
            timemessage.append("%i minutes" % minutes)
        if seconds != 0:
            timemessage.append("%i seconds" % seconds)

        if len(outmessage) > 0:
            outmessage += ", ".join(timemessage) + " ago, "
        else:
            outmessage += "just now, "

        if event.type == "Say":
            outmessage += "saying: <%s> %s" % (event.user, event.message)
        elif event.type == "Do":
            outmessage += "performing the action: * %s %s" % (event.user, event.message)
        elif event.type == "Msg":
            outmessage += "sending me a private message."
        elif event.type == "Part":
            outmessage += "parting the channel."
        elif event.type == "Join":
            outmessage += "joining the channel."
        elif event.type == "Quit":
            outmessage += "quitting with the message: %s" % event.message
        elif event.type == "Kick":
            outmessage += "getting kicked %s" % event.message
        elif event.type == "NickTo":
            outmessage += "changing nick to %s." % event.message
        elif event.type == "NickFrom":
            outmessage += "changing nick from %s." % event.message
        out(target, outmessage)

