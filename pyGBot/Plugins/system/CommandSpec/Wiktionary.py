##
##    English Wiktionary Lookup Command
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

class Wiktionary(BaseCommand):
    """ English Wiktionary Lookup Command """
    
    # CUSTOM SETTINGS
    wikiName = "Wiktionary"
    wikiUrl  = "http://en.wiktionary.org"
    wikiApi  = "/w/api.php"
    wikiBase = "/wiki"
    maxMessageSize = 0
    
    # Don't change anything below unless you know what you're doing
    level = AuthLevels.User
    
    def __init__(self, bot, channel, user, args):
        """ Query the Wiki plugin for an article lookup and output the returned
        text. """
        
        # Get text to output
        params = {
            'query' : ''.join(args).lower(), # wiktionary uses lowercase
            'name'  : self.wikiName,
            'url'   : self.wikiUrl,
            'api'   : self.wikiApi,
            'base'  : self.wikiBase,
            'maxsize' : self.maxMessageSize
        }
        response = bot.plugins['reference.Wiki'].command(channel, user, params)
        if response: # can return nothing if plugin disabled
            bot.replyout(channel, user, response)
