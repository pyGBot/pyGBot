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
from pyGBot import log

class Pot:
    def __init__(self, trigger = 0):
        log.logger.debug('Pot.__init__()')

        self.value = 0
        self.players = []
        self.trigger = trigger

    def award(self):
        from hand import Hand
        
        log.logger.debug('Pot.award()')

        hands = []
        for p in self.players:
            p.hand.evaluate()
            hands.append(p.hand)
            p.hand.seat = self.players.index(p)

        #DEBUG
        log.logger.debug('Pot.award: unsorted hands')
        for h in hands:
            log.logger.debug('%d: %s %s' % (h.seat, h, Hand.TYPE_STR[h.type]))
        #DEBUG

        hands.sort()
        hands.reverse()

        #DEBUG
        log.logger.debug('Pot.award: sorted hands')
        for h in hands:
            log.logger.debug('%d: %s %s' % (h.seat, h, Hand.TYPE_STR[h.type]))
        #DEBUG

        # Determine the number of winners
        hwinners = []
        hwinners.append(hands[0])
        for x in xrange(len(hands) - 1):
            h1 = hands[x]
            h2 = hands[x + 1]
            if h1 == h2:
                hwinners.append(h2)
            else:
                break

        winners = []
        for hw in hwinners:

            ###### Players on vacation can't win a pot
            #####if self.players[hw.seat].vacation > 1:
            #####    continue
            winners.append(self.players[hw.seat])

        ###### Everyone's on vacation, kill the tournament.
        #####if len(winners) == 0:
        #####    log.logger.critical('Pot.award:All winners on vacation!  Exiting.' % winners[0].nick)
        #####    sys.exit()

        log.logger.debug('Pot.award: winner %s' % winners[0].nick)            

        return winners

    def inpot(self, p):
        log.logger.debug('Pot.inpot()')

        result = False

        for player in self.players:
            if p.nick == player.nick:
                result = True

        return result
            
if __name__ == '__main__':
    from player import Player
    from hand import Hand
    from card import Card


    p1 = Player('AAAAAAAA', 'Player 1')
    p2 = Player('BBBBBBBB', 'Player 2')
    p3 = Player('CCCCCCCC', 'Player 3')

    p1.hand.addcard(Card(11))
    p1.hand.addcard(Card(41))

    p2.hand.addcard(Card(7))
    p2.hand.addcard(Card(48))

    p3.hand.addcard(Card(10))
    p3.hand.addcard(Card(4))

    p1.hand.addcard(Card(21))
    p2.hand.addcard(Card(21))
    p3.hand.addcard(Card(21))

    p1.hand.addcard(Card(29))
    p2.hand.addcard(Card(29))
    p3.hand.addcard(Card(29))

    p1.hand.addcard(Card(47))
    p2.hand.addcard(Card(47))
    p3.hand.addcard(Card(47))

    p1.hand.addcard(Card(6))
    p2.hand.addcard(Card(6))
    p3.hand.addcard(Card(6))    

    p1.hand.addcard(Card(39))
    p2.hand.addcard(Card(39))
    p3.hand.addcard(Card(39))    


    print 'P1:', p1.hand
    print 'P2:', p2.hand
    print 'P3:', p3.hand

    apot = Pot(50)
    apot.players.append(p1)
    apot.value += 50
    apot.players.append(p2)
    apot.value += 50
    apot.players.append(p3)
    apot.value += 50

    apot.award()
