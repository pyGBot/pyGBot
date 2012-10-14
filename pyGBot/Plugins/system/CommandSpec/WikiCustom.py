##
##    WikiCustom Command - Template for Custom MediaWiki Lookup Command
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

class WikiCustom(BaseCommand):
    """ Wikipedia Lookup Command - Outputs the URL to the searched article, if
    it exists, and an excerpt of the beginning of the article.

    This command is a simple binding to the reference.Wiki plugin.

    You can use the code to this command as a template for making your own
    custom MediaWiki lookup commands. This is useful if you want one bot to
    have several commands that lookup different MediaWiki sites via
    pyGBot.reference.Wiki.

    To make a custom command for pyGBot.reference.Wiki, copy the
    WikiCustom.py file and rename it. Open this new file, and also rename
    the WikiCustom class. Then, inside the class, change the values
    wikiName, wikiUrl, wikiApi, and wikiBase for the MediaWiki site you
    want. (See the plugin documentation for details about these settings).

    Then, in your pyGBot.ini file, under [Plugins.system.Commands], add the
    line:

        cmd = YourCustomCommandName

    where YourCustomCommandName is the name of the class you changed
    earlier, and cmd is the command IRC users will use for that command.

    If you know Python, you can further customise the command by changing
    the __init__ method. However, this is not officially supported and at
    your own discretion."""

    # CUSTOM SETTINGS
    wikiName = "Wikipedia"
    wikiUrl  = "http://en.wikipedia.org"
    wikiApi  = "/w/api.php"
    wikiBase = "/wiki"
    maxMessageSize = -1

    # Don't change anything below unless you know what you're doing
    level = AuthLevels.User

    def __init__(self, bot, channel, user, args):
        """ Query the Wiki plugin for an article lookup and output the returned
        text. """

        # Get text to output
        params = {
            'query' : ''.join(args),
            'name'  : self.wikiName,
            'url'   : self.wikiUrl,
            'api'   : self.wikiApi,
            'base'  : self.wikiBase,
            'maxsize' : self.maxMessageSize
        }
        try:
            wikiplugin = bot.plugins['reference.Wiki']
        except KeyError:
            return
        else:
            response = wikiplugin.command(channel, user, params)
            bot.replyout(channel, user, response)
