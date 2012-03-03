#
#    Copyright (C) 2004-2007 Paul Rotering
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA
import logging
import sys

formatter = logging.Formatter('%(asctime)s:%(name)s[%(process)d] %(levelname)s %(message)s')
cformat = logging.Formatter('%(asctime)s:%(message)s')

def addScreenHandler(logobj, format):
    """ Add stdout as a handler for a logger. """
    hdlr = logging.StreamHandler(sys.stdout)
    hdlr.setFormatter(format)
    logobj.addHandler(hdlr)

def addLogFileHandler(logobj, filename, format):
    """ Add a file handler to a logger. """
    try:
        hdlr = logging.FileHandler(filename)
    except IOError as e: # if directory not exist, try to create it
        # necessary imports to handle this
        import errno
        from os import makedirs
        from os.path import dirname, abspath
        
        if e.errno == errno.ENOENT: # if dir not exist
            print dirname(abspath(filename))
            try: makedirs(dirname(abspath(filename))) # create dir
            except: pass # guard vs. race cond: if other process created dir
            hdlr = logging.FileHandler(filename) # retry now
        else: raise # pass upward for other errno
    hdlr.setFormatter(format)
    logobj.addHandler(hdlr)

# Configure logging facility
logger = logging.getLogger('pyGBot')
logger.setLevel(logging.INFO)

chatlog = logging.getLogger('chat')
chatlog.setLevel(logging.INFO)
