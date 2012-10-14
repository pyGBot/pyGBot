##
##    Wiki Command - Wikipedia and MediaWiki Lookup Command
##    pyGBot.reference.Wiki - MediaWiki Lookup Plugin for pyGBot
##    Copyright (C) 2012 Marc-Alexandre Chan
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
from pyGBot.Plugins.system.Auth import AuthLevels

class Wiki(BaseCommand):
    """ Wikipedia Lookup Command - Outputs the URL to the searched article, if
    it exists, and an excerpt of the beginning of the article.

    This command is a simple binding to the reference.Wiki plugin."""

    level = AuthLevels.User

    def __init__(self, bot, channel, user, args):
        """ Query the Wiki plugin for an article lookup and output the returned
        text. """

        # Get text to output
        params = {
            'query' : ''.join(args)
        }
        try:
            wikiplugin = bot.plugins['reference.Wiki']
        except KeyError:
            return
        else:
            response = wikiplugin.command(channel, user, params)
            bot.replyout(channel, user, response)
