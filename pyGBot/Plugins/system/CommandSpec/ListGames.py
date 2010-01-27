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

from pyGBot.Plugins.system.Commands import BaseCommand
from pyGBot.Plugins.system.Auth import AuthLevels as AL

class ListGames(BaseCommand):
    level = AL.User
    def __init__(self, bot, channel, user, args):
        args = args.split()

        avail = [p.split('.')[1] for p in bot.plugins.iterkeys() if p.startswith('games.')]
        bot.pubout(channel, 'Available games: %s' % ', '.join(avail))
        
        active = [p.split('.')[1] for p in bot.activeplugins if p.startswith('games.')]
        if len(active) > 0:
            bot.pubout(channel, 'Active game: %s' % active[0])
