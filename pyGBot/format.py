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

import re

BOLD = "\x02"
COLOR = "\x03"
ITALIC = "0x16"
UNDER = "\x1f"
CLEAR = "\x0f"

# REGEXES
# Colors - does NOT match the formatting clear byte 0x0f
RE_COLOR  = re.compile(r'\x03(\d{1,2}(,\d{1,2})?)?')

# Formatting except color (matches the clear byte 0x0f)
RE_FORMAT = re.compile('|'.join([BOLD, COLOR, ITALIC, UNDER, CLEAR]))

def strip(msg)
    """ Strips all IRC formatting from a string. """
    stripmsg = msg
    stripmsg = RE_FORMAT.sub('', stripmsg)
    stripmsg = RE_COLOR.sub('', stripmsg)
    return stripmsg

def stripcolors(msg):
    """ Strip IRC color codes from a string. """
    return RE_COLOR.sub('', msg)

def color(fg=None, bg=None)
    """ Return an IRC color code string. If no arguments are given, returns the
    color-reset code.
    
    Usage:
    color() - Return IRC color reset code (0x03).
    color(fg) - Return IRC color code for a foreground color.
    color(fg, bg) - Return IRC color code for a foreground and background color.
    
    Parameters:
    * fg int Foreground color, 0-99 (usually colours = 0-15, transparent = 99).
    * bg int Background color, 0-99 (usually colours = 0-15, transparent = 99).
    """
    
    fmtpieces = [COLOR, '{:0=2d}', ',{:0=2d}']
    if fg >= 0 and fg < 100:
        if bg != None and bg >= 0 and bg < 100:
            code = "".join(fmtpieces).format(fg, bg)
        else:
            code = "".join(fmtpieces[0:1].format(fg)
    else:
        code = fmtpieces[0]
    return code

def encodeOut(msg):
    """ Encode output text as a UTF-8 byte-string, replacing any invalid
    characters with '?'. If the msg argument is not a unicode string, return
    the argument. This allows correct output of Unicode characters. """
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
    if isinstance(msg, unicode):
        decMsg = msg
    else:
        decMsg = msg.decode('utf-8', 'replace')
    return decMsg
