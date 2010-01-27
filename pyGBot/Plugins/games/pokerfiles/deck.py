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
from random import random, seed, shuffle
from struct import unpack
from card import Card
from pyGBot import log

class Deck:
    '''
    A standard 52 card deck
    '''

    error = 'deck.error'
    def __init__(self):
        log.logger.debug('Deck.__init__()')

        self.cards = range(0, 52)
        self.topcard = -1
    def __str__(self):
        buf = ''
        for card in self.cards:
            buf += '%d ' % card
        return buf.strip()

    def reseed(self):
        log.logger.debug('Deck.reseed()')

        ef = open('/dev/random', 'r')
        entropy = ef.read(29)
        #seed(hash(entropy))
        seed(entropy)
    def shuffle(self, newdeck = False):
        'Shuffle using Random.shuffle()'

        log.logger.debug('Deck.shuffle()')

        # start from a fresh deck, if requested
        if newdeck:
            self.cards.sort()
        self.topcard = -1
        shuffle(self.cards)

    def shuffle2(self, newdeck = False):
        'Shuffle using Knuth shuffle algorithm and /dev/random'

        log.logger.debug('Deck.shuffle2()')
        
        # start from a fresh deck, if requested
        if newdeck:
            self.cards.sort()
        self.topcard = -1

        for j in xrange(51, 0, -1):
            k = self.rand64k(j)
            self.cards[j], self.cards[k] = self.cards[k], self.cards[j]
            
    def rand64k(self, n = 51):
        '''Draw a random integer between 0 and n using the middle 16
        bit of 32 bits read from /dev/urandom.

        Thanks to DGH for the algorithm as well as general discussions
        of randomness.
        '''

        #log.logger.debug('Deck.rand4()')

        rf = open('/dev/urandom', 'r')

        rn = rf.read(4)

        # Convert to an unsigned int
        rn = unpack('I', rn)[0]

        # Shave off lower and upper 8 bits 
        rn = (rn >> 8) & 0x0000FFFF

        return (rn * n) >> 16

    def rand51(self):
        '''Draw a random integer between 0 and 51 using /dev/(u)random
        It is possible to substitute random for urandom should the
        need arise for a "guarantee" of "randomness".'''

        log.logger.debug('Deck.rand51()')

        rf = open('/dev/urandom', 'r')
        while True:
            byte = rf.read(1)

            # Convert byte to an unsigned int and mask off 6 bits
            byte = unpack('B', byte)[0] & 63

            # Redraw if the masked byte is > 51, otherwise return it
            if byte <= 51:
                rf.close()
                break
            else:
                continue

        return byte

    def nextcard(self):
        #log.logger.debug('Deck.nextcard()')

        if self.topcard == 51:
            raise Deck.error, 'no cards left in deck'
        self.topcard += 1
        return Card(self.cards[self.topcard])

if __name__ == '__main__':
    foo = Deck()
    #foo.reseed()
    for i in xrange(0, 10):
        print '-------------------------------'
        foo.shuffle2(True)
        for card in xrange(0,52):
            print foo.nextcard().face(),
            if not (card + 1) % 13:
                print
