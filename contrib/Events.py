# from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/410686
# Copyright (c) 2005 Zoran Isailovski
# Modification for pyGBot, Copyright (c) 2012 Marc-Alexandre Chan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE

######################################################################
## 
## Events
## 
######################################################################

from pyGBot import log
from sys import exc_info
from traceback import extract_tb, format_tb

class Events:
   def __getattr__(self, name):
      if hasattr(self.__class__, '__events__'):
         assert name in self.__class__.__events__, \
                "Event '%s' is not declared" % name
      self.__dict__[name] = ev = _EventSlot(name)
      return ev
   def __repr__(self): return 'Events' + str(list(self))
   __str__ = __repr__
   def __len__(self): return NotImplemented
   def __iter__(self):
      def gen(dictitems=self.__dict__.items()):
         for attr, val in dictitems:
            if isinstance(val, _EventSlot):
               yield val
      return gen()

class _EventSlot:
   def __init__(self, name):
      self.targets = []
      self.__name__ = name
   def __repr__(self):
      return 'event ' + self.__name__
   def __call__(self, *a, **kw):
      for f in self.targets:
         # pyGBot-specific: try/except block to catch and log exceptions
         try:
            f(*a, **kw)
         except: # log exceptions in event targets
            eclass, e, etrace = exc_info()
            efile, eline, efunc, esource = extract_tb(etrace)[-1]
            log.logger.error("%s: %s raised in '%s', file '%s', line %i",\
                eclass.__name__, str(e), efunc, efile, eline)
            log.logger.debug("    %s", esource)
            log.logger.debug("Traceback (most recent call last):\n" + ''.join(format_tb(etrace)))
   def __iadd__(self, f):
      self.targets.append(f)
      return self
   def __isub__(self, f):
      while f in self.targets: self.targets.remove(f)
      return self
