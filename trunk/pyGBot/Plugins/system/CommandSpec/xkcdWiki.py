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

import random

from pyGBot import log
from pyGBot.Plugins.system.Commands import BaseCommand
from pyGBot.Plugins.system.Auth import AuthLevels as AL
from urllib import urlencode
from urllib2 import urlopen
import json

class xkcdWiki(BaseCommand):
    level = AL.User
    def __init__(self, bot, channel, user, args):
        if channel is None:
            out = bot.privout
            target = user
        else:
            out = bot.pubout
            target = channel
            
        search = "".join(args)
        existurl = "http://wiki.xkcd.com/wirc/api.php?action=query&titles=%s&format=json" % search.replace(" ", "%20")
        url = "http://wiki.xkcd.com/irc/%s" % search.replace(" ", "%20")

        if self.check_wiki_exists(existurl):
            out(target,"URL for XKCDWiki - %s: %s." % (search, self.tiny_url(url)))
        else:
            out(target,"Sorry, no XKCDWiki page exists for '%s'." % search)

    def check_wiki_exists(self, url):
        page = json.loads(urlopen(url).readline())
        if 'missing' in page['query']['pages'].values()[0]:
            return False
        else:
            return True

    def tiny_url(self, url):
        """ Query a Tinyurl service, if not available query an alternative one
            If the alternative service is not available, return the url """ 
            
        TINYURL = 'http://tinyurl.com/apicreate.php?%s'
        ISGD = 'http://is.gd/api.php?%s'
        
        try:
            url = urlopen(ISGD % urlencode({'longurl':url})).read()
        except:
            url = urlopen(TINYURL % urlencode({'url':url})).read()
        finally:
            return url