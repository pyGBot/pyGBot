#
##    pyGBot.reference.Wiki - MediaWiki Lookup Plugin for pyGBot
##    Based on system.CommandSpec.Wiki in pyGBot 0.1.5 by Morgan 
##        Lokhorst-Blight and Alex Soborov
##    Copyright (c) 2012 Marc-Alexandre Chan
##
##    pyGBot - Versatile IRC Bot
##    Copyright (C) 2008 Morgan Lokhorst-Blight, Alex Soborov
##
##    The following text applies to both pyGBot.reference.Wiki and pyGBot:
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
#

from pyGBot import log
from pyGBot import format
from pyGBot.BasePlugin import BasePlugin

from urllib import quote, urlencode
from urllib2 import urlopen, URLError
import re
import json

class Wiki(BasePlugin):
    """ MediaWiki Lookup Plugin - Looks up an article on any MediaWiki website
    (default Wikipedia). Returns the URL to the searched article and an excerpt
    of the lead-in section, if the article exists.
    
    This plugin is meant to be used with a Command (for the system.Commands
    plugin included with pyGBot). You can use the included Wiki command to
    lookup Wikipedia, to set a custom MediaWiki website using the INI file
    configuration, or write your own Command(s) if you want to be able to lookup
    articles from several MediaWiki websites or otherwise customise things even
    more.
    
    Features:
    - Uses system.Commands plugin to trigger on IRC user's commands
    - Command name, MediaWiki website configurable using the pyGBot.ini file
    - Possible to use several different MediaWiki websites through the same
      plugin by writing custom commands (template command included)
    - Plugin fetches URL and a short extract from the beginning of the article
      (total length of the message is configurable)
    - Checks whether an article exists before responding
    - Resolves redirects on the wiki automatically
    - Optional URL shortening via is.gd or tinyurl.com
    
    I) To lookup only Wikipedia:
        1) Copy this file to the pyGBot/Plugins/reference directory.
        2) Copy the Command file (also called Wiki.py) to the
           pyGBot/Plugins/system/CommandSpec directory.
        3) In your pyGBot.ini file, add this line:
                reference.Wiki =
           under BOTH the [Plugins] and [Plugins.system.Startup] sections.
        4) In your pyGBot.ini file, add this line:
                wp = Wiki
           under the [Plugins.system.Commands] section. This tells the Commands
           plugin about your Wiki command, and what users can use to call that
           command (in this case, it's "wp" - you can change it).
        5) Run or restart pyGBot (execute runpyGBot.py).
    
    II) To lookup any other MediaWiki website (or to customise the plugin):
        1) Follow the instructions in I) above.
        2) In your pyGBot.ini file, add the following:
                [Plugins.reference.Wiki]
                wikiName = Wikipedia
                wikiUrl = http://en.wikipedia.org
                wikiApi = /w/api.php
                wikiBase = /wiki
                maxMessageSize = 510
                shortUrl = False
        3) Change the values to your liking. All of these settings are optional,
           and will default to the values shown in step 2) if not specified.
           They have the following meanings:
                wikiName: Name of the wiki to look up
                wikiUrl: URL of the wiki website to look up
                wikiApi: URI to "api.php" on the wiki website. This is appended
                    to wikiUrl to get a full URL. Only some websites  need this
                    changed.
                wikiBase: URI to access the articles on the wiki website. This
                    and the article title are appended to wikiUrl to get each
                    article's URL. Only some websites need this changed.
                maxMessageSize: Maximum message length that can be sent over
                    IRC. The IRC spec is 510, but some networks have a lower
                    maximum.
                shortUrl: Whether to shorten URLs sent over IRC using TinyURL
                    is.gd. Should be either "True" or "False".
    
    III) To create Commands for two or more different MediaWiki sites:
        1) Follow the instructions in II) above. You can use the wiki website 
           configured there with the Command plugin for one MediaWiki website.
        2) To make commands for other MediaWiki websites, take a look at the
           "WikiCustom.py" file in Plugins/system/CommandSpec. You can copy
           this file, rename it, rename the WikiCustom class inside it and
           customise it for the MediaWiki website; it basically has the same
           configuration settings as the ones starting with wiki- in Step 3)
           above.
        3) Configure your custom command in the same way as Part I) Step 4)
           above, replacing "wp" with the command you want IRC users to use and
           "Wiki" with the name of your custom Command class/file.
        
    Although the functionality is provided, using custom-written commands is
    at your own discretion. It is not officially supported.
    
    Dependencies:
    - system.Commands plugin
    - system.CommandSpec.Wiki command (or a custom command script)
    """
    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        
        # default options
        self.useShortUrl    = False
        self.maxMessageSize = 510
        self.wikiName       = 'Wikipedia'
        self.wikiUrl        = 'http://en.wikipedia.org'
        self.wikiApi        = '/w/api.php'
        self.wikiBase       = '/wiki'
        self.wikiSave       =  {} # settings push/pop from here
        
        # private attributes
        self.active = False
        self.lastResponse = {}
        self.lastTitle = u""
        
        # retrieve options from configuration
        if 'shortUrl' in options:
            self.useShortUrl = (options['shortUrl'][0].upper()!='F')
        if 'maxMessageSize' in options:
            self.maxMessageSize = min(self.maxMessageSize,
                                      int(options['maxMessageSize']))
        if 'wikiName' in options:
            self.wikiName = options['wikiName'].strip()
        if 'wikiUrl' in options:
            self.wikiUrl = options['wikiUrl'].rstrip('/\\?')
        if 'wikiApi' in options:
            if options['wikiApi'][0] != '/':
                self.wikiApi = '/' + options['wikiApi'].rstrip('/\\?')
            else:
                self.wikiApi = options['wikiApi'].rstrip('/\\?')
        if 'wikiBase' in options:
            if options['wikiBase'][0] != '/':
                self.wikiBase = '/' + options['wikiBase'].rstrip('/\\?')
            else:
                self.wikiBase = options['wikiBase'].rstrip('/\\?')

    def activate(self, channel=None):
        """ Activate the plugin. """
        self.active = True
        return True

    def deactivate(self, channel=None):
        """ Deactivate the plugin. """
        self.active = False
        return True
    
    # Custom command handler (see Command plugin)
    def command(self, channel, user, args):
        """ Execute a command. Searches for an article on the wiki, and returns
        a string containing the article title, URL and a short extract (or an
        error message).
        
        The expected arguments args is a dictionary of the form
        {'query': searchterms, 'name': wikiName, 'url': wikiUrl,
        'api': wikiApi, 'base': wikiBase}, where searchterms is the
        search terms, and the other arguments have the same meaning as the
        configuration options of the same name. The first argument is
        required, but the latter arguments are optional and override the
        configuration settings for Wiki name, URL, etc. if present."""
        
        # if plugin inactive, exit
        if not self.active:
            return ""
        
        # for logging purposes
        if not channel:
            source = 'msg'
        else:
            source = channel
        
        # Set wiki settings if provided
        self.pushWiki()
        self.loadWiki(args)
        
        # Error if no query specified or invalid query
        if 'query' not in args:
            log.logger.info("reference.Wiki: No subject passed for lookup " +\
                "by %s in %s on %s <%s>",\
                user, source, format.encodeOut(self.wikiName), self.wikiUrl)
            return u"Please provide a subject to search %s" % self.wikiName
        
        # Start processing the command
        query = args['query'].strip()
        outputList = [] # [wikiname, articlename, (previewText), url]
        
        isFound = self.articleExists(query)
        
        if isFound:
            invalidArticle = False # for logging purposes
            resolvedTitle = self.getResolvedTitle(query)
            outputList.append( "".join([self.wikiName, " -"]) )
            outputList.append( "".join(["\x02", resolvedTitle, "\x02:"]) )
            
            if self.useShortUrl:
                outputList.append( self.getShortUrl(resolvedTitle) )
            else:
                outputList.append( self.getUrl(resolvedTitle) )
            
            # Preview length = max length - current length (all as bytes)
            # (+ 1 for additional " " needed to insert preview text)
            previewLen = min(510, self.maxMessageSize)\
                             - (len(format.encodeOut(u' '.join(outputList)))+1)
            # use query, not redirectTitle, to make use of cache and not redownload
            previewText = self.getPreview(query, previewLen)
            
            # if getPreview received malformed data, assume an invalid page
            if previewText is None:
                outputList = ["Sorry, I can't look that up on %s." % self.wikiName]
                log.logger.warning("reference.Wiki: Attempted lookup of " +\
                    "non-article '%s' by %s in %s on %s <%s>",\
                    format.encodeOut(query), user, source,\
                    format.encodeOut(self.wikiName), self.wikiUrl)
                invalidArticle = True # for logging purposes
            # if getPreview returned text, add to output
            elif len(previewText) > 0:
                outputList.insert(2, previewText)
            
            # If we didn't fall under the "I can't look that up" case, log a successful lookup
            if not invalidArticle:
                log.logger.info("reference.Wiki: Found article '%s' for " +\
                    "query '%s' by %s in %s on %s <%s>",\
                    format.encodeOut(resolvedTitle), format.encodeOut(query),\
                    user, source, format.encodeOut(self.wikiName), self.wikiUrl)
        
        elif isFound == False:
            outputList.append( u"Sorry, no %s page exists for '%s'."\
                               % (self.wikiName, query) )
            log.logger.info("reference.Wiki: No article found for query " +\
                            "'%s' by %s in %s on %s <%s>",\
                            format.encodeOut(query), user, source,\
                            format.encodeOut(self.wikiName), self.wikiUrl)
        else: # None, meaning an error occurred
            outputList.append(u"Sorry, an error occurred searching for %s page '%s'."\
                % (self.wikiName, format.encodeOut(query)))
            outputList.append(u"Maybe it works for you:")
            if self.useShortUrl:
                outputList.append( self.getShortUrl(query) )
            else:
                outputList.append( self.getUrl(query) )
            log.logger.error("reference.Wiki: An error occurred retrieving " +\
                             "or parsing the API response for query '%s' by " +\
                             "%s in %s on %s <%s>",\
                             format.encodeOut(query), user, source,\
                             format.encodeOut(self.wikiName), self.wikiUrl)
        
        # Restore options set in bot configuration
        self.popWiki()
        
        return u' '.join(outputList)
    
    def loadWiki(self, options):
        """ Load wiki settings from a dict. options should have the keys
        'name', 'url', 'api', and 'base', defined in the same way as args for
        the command() method. If any of those keys is not present, the
        associated setting is not changed. This method clears response cache."""
    
        if 'name' in options and options['name']:
            self.wikiName = options['name']
        if 'url'  in options and options['url']:
            self.wikiUrl  = options['url']
        if 'api'  in options and options['api']:
            self.wikiApi  = options['api']
        if 'base' in options and options['base']:
            self.wikiBase = options['base']
        if 'maxsize' in options and int(options['maxsize']) >= 0:
            self.maxMessageSize = int(options['maxsize'])
        
        # clear cache
        self.lastResponse = {}
        self.lastTitle = u""
        return True
    
    def pushWiki(self):
        """ Save wiki settings. Used for on-the-fly reconfiguration of the 
        wiki to access. Use popWiki() to restore settings. This method clears
        response cache. """
        self.wikiSave = {}
        self.wikiSave['name'] = self.wikiName
        self.wikiSave['url']  = self.wikiUrl
        self.wikiSave['api']  = self.wikiApi
        self.wikiSave['base'] = self.wikiBase
        self.wikiSave['maxsize'] = self.maxMessageSize
        
        # clear cache
        self.lastResponse = {}
        self.lastTitle = u""
        return True
    
    def popWiki(self):
        """ Restore saved wiki settings. Used for on-the-fly reconfiguration 
        of the wiki to access. Return True on success, False if wiki settings
        were not saved (pushed).  This method clears response cache. Use
        pushWiki() to save settings before using popWiki(). """
        if self.wikiSave:
            self.loadWiki(self.wikiSave)
            self.wikiSave = {}
            return True
        else:
            return False

    def articleExists(self, title):
        """Checks if an article with the given title exists on the wiki. Returns
        True if the article exists, None if a network or parsing error occurs,
        and False otherwise."""
        
        results = self.getApiResponse(title)
        
        try:
            # page not found
            if 'missing' in results['query']['pages'].values()[0]:
                return False
            else:
                return True
        except (IndexError, KeyError, TypeError):
            # Network error or bad response structure
            return None
        
    def getPreview(self, title, maxlen):
        """Get a preview of the article (the first few hundred characters). 
        This assumes the article exists (i.e. check self.articleExists first!)
        If an error accessing the article occurs, an empty string is returned.
        If the data received is malformed, None is returned."""
        
        # If preview length is 0, no preview; exit early
        if maxlen <= 0:
            return ""
        
        results = self.getApiResponse(title)
        
        # if getApiResponse() returns None, failed to retrieve or parse data
        if not results: return None
        
        try:
            htmlText = results['query']['pages'].values()[0]['revisions'][0]['*']
        except (KeyError, IndexError, TypeError) as e:
            log.logging.exception("reference.Wiki: A %s exception occurred " +\
                "while retrieving article text for '%s': %s",\
                e.__class__.__name__, format.encodeOut(title), str(e))
            return None
        except:
            log.logging.exception("reference.Wiki: An error occurred while " +\
                "retrieving the content of '%s' (maybe malformed JSON?)",\
                format.encodeOut(title))
            return None
        
        previewText = self.getFirstParagraph(htmlText)
        
        # encode: so smartTruncate() counts bytes, not Unicode chars
        # decode: reconverts it back to Unicode for return
        previewText = self.smartTruncate(
                        previewText.encode('utf-8', 'replace'),\
                        maxlen).decode('utf-8', 'replace')
        return previewText
        
    def getUrl(self, title):
        """Returns the URL of the article."""
        urlTitle = quote(format.encodeOut(
                    self.getResolvedTitle(title).replace(' ', '_')))
        return "%s%s/%s" % (self.wikiUrl, self.wikiBase, urlTitle)
        
    def getShortUrl(self, title):
        """ Query a URL shortening service and returns a shortened URL to the
        article. If no URL shortening service available, returns the URL. """
        
        url = self.getUrl(title)
            
        TINYURL_CREATEURL = 'http://tinyurl.com/apicreate.php?%s' % \
            urlencode({'longurl' : url})
        ISGD_CREATEURL = 'http://is.gd/api.php?%s' %\
            urlencode({'url' : url})
        
        try:
            url = urlopen(ISGD_CREATEURL).read()
        except:
            url = urlopen(TINYURL_CREATEURL).read()
        finally:
            return url
    
    def getResolvedTitle(self, title):
        """ Return the resolved article title after all redirects and
        normalisations. """
        
        response = self.getApiResponse(title)
        
        try:
            return response['query']['pages'].values()[0]['title']
        except:
            return title
    
    def getFirstParagraph(self, textHtml):
        """ Return the first paragraph of an HTML Wiki page as plain text. """
        # div/table removal (templates/infoboxes) helps in case there are <p>
        # tags inside these elements; fails on nesting, but okay as rough filter
        reTemplates  = re.compile(r"<(div|table)(\s[^>]+)?>(.*?)</\1>", re.S)
        htmlCleaned = reTemplates.sub("", textHtml)
        
        #  first paragraph element
        reParagraph  = re.compile(r"<p(\s[^>]+)?>(.*?)</p>", re.S)
        matchParagraph = reParagraph.search(htmlCleaned)
        if not matchParagraph: # If no paragraph found, there's no preview
            return ""
        return self.stripWikiHtml(matchParagraph.group(2))
        
    def stripWikiHtml(self, textHtml):
        """ Return a plaintext copy of the HTML Wiki test passed. Newlines are
        also removed. """
        
        textPlain = textHtml
        
        # Strip all tags
        reTags = re.compile(r"<.*?>", re.S)
        textPlain   = reTags.sub("", textPlain)
        
        # Remove Wikipedia footnote references and extra parenthetical info
        #reReferences = re.compile(r"\[\d*]")
        reReferences = re.compile(r"\s*\[.*?]|\s*\(.*?\)")
        textPlain         = reReferences.sub("", textPlain)
        
        # TODO: Improve entities conversion
        # Convert some common entities and remove rest
        reEntities = re.compile(r"&(?!amp;)#?[A-Za-z0-9]+;")
        textPlain = textPlain.replace('&gt;', '>').replace('&lt;', '<')\
                     .replace('&quot;', "'").replace('&nbsp;',u'\xA0')\
                     .replace('&#0160;',u'\xA0').replace('&#160;',u'\xA0')\
                     .replace('&mdash;',u'\u2014').replace('&#8212;',u'\u2014')\
                     .replace('&ndash;',u'\u2013').replace('&#8211;',u'\u2013')\
                     .replace('&#32;',' ')
        textPlain = reEntities.sub("?", textPlain)
        textPlain = textPlain.replace('&amp;', '&')
        
        # Remove multiple whitespace
        reWhitespace = re.compile(r"\s+")
        textPlain = textPlain.strip() # trim whitespace
        textPlain = reWhitespace.sub(" ", textPlain)
        
        return textPlain
        
    def smartTruncate(self, text, maxlen):
        """ Truncates text along word boundaries (spaces and punctuation) and
        inserts an ellipsis at the end of text truncated mid-sentence. """
        
        if len(text) > maxlen:
            # First truncate to length
            textFullTrunc = text[:maxlen-1]
            
            # get last non-whitespace, non-quote character
            lastFullChar = textFullTrunc.strip(' \t\r\n\'"')[-1]
            
            # If truncated at the end of a sentence, leave as-is
            if lastFullChar == '.'\
            or lastFullChar == '!'\
            or lastFullChar == '?':
                textTrunc = textFullTrunc
            
            # If string ends a word (last OR last+1 char is punct/whitespace)
            # Then strip non-sentence-final punctuation, and add ellipsis
            # [String is truncated 3 chars more for the ellipsis]
            elif len(textFullTrunc[-4:-2].strip(' \t\r\n;:,')) < 2:
                textTrunc = textFullTrunc[:-3].rstrip(' \t\r\n;:,') + "..."
            
            # Else take off the truncated word and add ellipsis
            else:
                textTrunc = textFullTrunc[:-3].rsplit(None, 1)[0]\
                            .rstrip(' \t\r\n;:,') + "..."
        else:
            textTrunc = text
        
        return textTrunc
    
    def getApiResponse(self, title):
        """ Make an API request to the Wiki for an article and return the parsed
        JSON response. The article content contained in the response is parsed
        as HTML, not raw wikicode. The response is cached for later use. """
        
        # if already cached, return that
        if title == self.lastTitle:
            return self.lastResponse
            
        queryParams = {
            'action' : 'query',
            'titles' : format.encodeOut(title),
            'prop'   : 'revisions',
            'rvprop' : 'content',
            'rvsection' : 0,
            'rvlimit': 1,
            'rvparse': 1,
            'redirects' : 1,
            'format' : 'json'
            }
        apiUrl = "%s%s?%s"%(self.wikiUrl, self.wikiApi, urlencode(queryParams))
        
        try:
            self.lastResponse = json.loads(urlopen(apiUrl).readline(), 'UTF-8')
            self.lastTitle = title
            return self.lastResponse
        except URLError as e:
            if hasattr(e, 'reason'):
                log.logging.error("reference.Wiki: Cannot access <%s>." +\
                    "Error %i: %s", apiUrl, e.reason[0], e.reason[1])
            elif hasattr(e, 'code'):
                log.logging.error("reference.Wiki: Cannot access <%s>. " +\
                    "Server returned status: %i", apiUrl, e.code)
            return None
        # TODO: What can json.loads raise anyway?
        except:
            log.logging.exception("reference.Wiki: An error occurred " +\
                "retrieving the content of '%s' <%s> (maybe malformed JSON?)",\
                format.encodeOut(title), apiUrl)
            return None
