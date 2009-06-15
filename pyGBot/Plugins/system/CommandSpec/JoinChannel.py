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

from pyGBot import log
from pyGBot.Plugins.system.Commands import BaseCommand
from pyGBot.Plugins.system.Auth import AuthLevels as AL

class JoinChannel(BaseCommand):
    level = AL.Admin
    def __init__(self, bot, channel, user, args):
        if args == '':
            bot.noteout(user, 'Please specify a channel to join.')

        args = args.split(' ')
        if args[0].startswith('#'):
            if args[0] not in bot.channels:
                log.logger.info('Attempting to join channel %s' % args[0])
                if len(args) > 1:
                    bot.join(args[0], key=args[1])
                else:
                    bot.join(args[0])
            else:
                bot.noteout(user, 'I am already connected to that channel.')
        else:
            bot.noteout(user, 'Incorrect channel name. Channels must start with #')

