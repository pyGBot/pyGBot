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
import card

class Hand:
    "A seven card hand"

    TYPE_NP = 0
    TYPE_1P = 1
    TYPE_2P = 2
    TYPE_3K = 3
    TYPE_ST = 4
    TYPE_FL = 5
    TYPE_FH = 6
    TYPE_4K = 7
    TYPE_SF = 8
    TYPE_STR = {TYPE_NP:'No Pair', TYPE_1P:'One Pair',\
                TYPE_2P:'Two Pair', TYPE_3K:'Three of a Kind',\
                TYPE_ST:'Straight', TYPE_FL:'Flush',\
                TYPE_FH:'Full House', TYPE_4K:'Four of a Kind',\
                TYPE_SF:'Straight Flush'}
    def __init__(self):
        #log.logger.debug('Hand.__init__()')

        self.cards = []
        self.flushcard = None
        self.hi = 0
        self.kickers = []
        self.lo = 0
        self.seat = 0
        self.straighthi = 0
        self.type = Hand.TYPE_NP
    def __cmp__(self, other):
        #log.logger.debug('Hand.__cmp__()')

        result = 0

        if self.type == other.type:
            log.logger.debug('Hand.__cmp__:Hand types equal')
            if self.hi == other.hi:
                log.logger.debug('Hand.__cmp__:Hand hi equal')

                # straights and straight flushes with equal
                # high cards are equal
                if self.type == Hand.TYPE_ST or self.type == Hand.TYPE_SF:
                    result = 0
                elif self.type == Hand.TYPE_FH:
                    result = cmp(self.lo, other.lo)
                elif self.type == Hand.TYPE_2P:
                    if self.lo == other.lo:
                        result = self.checkkicker(other)
                    else:
                        result = cmp(self.lo, other.lo)
                else:
                    result = self.checkkicker(other)
            else:
                result = cmp(self.hi, other.hi)
        else:
            result = cmp(self.type, other.type)

        return result
    def __str__(self):
        #log.logger.debug('Hand.__str__()')

        buf = ''
        buf += '[Hand:'
        for c in self.cards:
            buf += '%s ' % c.face()
        buf = buf[:-1]
        buf += ']:Type=%d(%s)' % (self.type, Hand.TYPE_STR[self.type])
        return buf
    def addcard(self, acard):
        #log.logger.debug('Hand.addcard()')

        self.cards.append(acard)

    def card(self, card):
        #log.logger.debug('Hand.card()')

        return self.cards[card]

    def checkkicker(self, other):
        #log.logger.debug('Hand.checkkicker()')

        result = 0

        self.prockickers()
        other.prockickers()

        #DEBUG
        if len(self.kickers) > 7:
            log.logger.critical('Hand.checkkicker:Too many kickers in self')
        if len(other.kickers) > 7:
            log.logger.critical('Hand.checkkicker:Too many kickers in other')
        log.logger.debug('Self:')
        #for c in self.kickers:
        #    log.logger.debug('     %s' % c.face())
        #log.logger.debug('Other:')
        #for c in other.kickers:
        #    log.logger.debug('     %s' % c.face())
        #DEBUG

        if self.type == Hand.TYPE_2P or self.type == Hand.TYPE_4K:
            ncomps = 1
        elif self.type == Hand.TYPE_3K:
            ncomps = 2
        elif self.type == Hand.TYPE_1P:
            ncomps = 3
        elif self.type == Hand.TYPE_NP:
            ncomps = 4            
        elif self.type == Hand.TYPE_FL:
            ncomps = 5
        for x in xrange(ncomps):
            log.logger.debug('Hand.checkkicker:self  rank:%2d' %\
                             self.kickers[x].rank())
            log.logger.debug('Hand.checkkicker:other rank:%2d' %\
                             other.kickers[x].rank())

            if self.kickers[x].rank() == other.kickers[x].rank():
                continue
            else:
                result = cmp(self.kickers[x].rank(),
                             other.kickers[x].rank())
                break
        return result
            
    def muck(self):
        #log.logger.debug('Hand.muck()')

        self.cards = []
        self.type = Hand.TYPE_NP

    def prockickers(self):
        #log.logger.debug('Hand.prockickers()')

        self.kickers = []

        if self.type == Hand.TYPE_FL:
            for c in self.cards:
                if c.suit() == self.flushcard.suit():
                    self.kickers.append(c)
        elif self.type == Hand.TYPE_1P or self.type == Hand.TYPE_3K or\
                 self.type == Hand.TYPE_4K or self.type == Hand.TYPE_NP:
            for c in self.cards:
                if c.rank() != self.hi:
                    self.kickers.append(c)
        elif self.type == Hand.TYPE_2P:
            for c in self.cards:
                if c.rank() != self.hi and c.rank() != self.lo:
                    self.kickers.append(c)
        self.kickers.sort()
        self.kickers.reverse()

    def __isstraightflush(self):
        #log.logger.debug('Hand.__isstraightflush()')
        
        hist = []
        result = 0

        for card in self.cards:
            if card.suit() == self.flushcard.suit():
                hist.append(card)

        hist.sort()
        hist.reverse()

        newhr = rlast = hist[0].rank()
        i = seq = 1
        while i < len(hist):
            if hist[i].rank() == rlast - 1:
                seq += 1
                rlast = hist[i].rank()
                i += 1
            else:
                seq = 1
                newhr = rlast = hist[i].rank()
                i += 1            

            if seq == 5:
                break

        if seq == 5:
            self.straighthi = newhr
            result = 1

        elif seq == 4 and newhr == 3 and hist[0].rank() == 12:
            self.straighthi = newhr
            result = 1

        return result

    def __isstraight(self, rhist):
        #log.logger.debug('Hand.__isstraight()')

        hist = []
        rank = 0
        result = 0

        for r in rhist:
            if r > 0:
                hist.append(rank)
            rank += 1
        hist.sort()
        hist.reverse()

        #DEBUG
        #print 'isstraight:hist:%s' % hist
        #DEBUG

        # check for five sequential ranks
        seq = 1
        self.straighthi = hist[0]
        for r in xrange(len(hist) - 1):
            if hist[r] - hist[r + 1] == 1:
                seq += 1
                #DEBUG
                #print 'isstraight:seq:%d' % seq
                #DEBUG
                if self.straighthi == 0:
                    self.straighthi = hist[r]

                # check for five high straight
                if seq == 4 and self.straighthi == 3:
                    if hist[0] == 12:
                        seq = 5
                        self.straighthi = 3
                if seq == 5:
                    result = 1
            else:
                if seq < 5:
                    self.straighthi = 0
                    seq = 1

        return result

    def evaluate(self):
        #log.logger.debug('Hand.evaluate()')

        rhist = [0,0,0,0,0,0,0,0,0,0,0,0,0]
        shist = [0,0,0,0]
        flushtop = [0,0,0,0]
        hicard = 0
        bucketsum = 0
        hf = nhf = 0
        hfr = nhfr = 0

        # Fill rank histogram
        for card in self.cards:
            arank = card.rank()

            rhist[arank] += 1
            if arank > hicard:
                hicard = arank

            asuit = card.suit()
            shist[asuit] += 1

        # Sum buckets using cards as indices
        for card in self.cards:
            arank = card.rank()
            bucketsum += rhist[arank]
            freq = rhist[arank]
            asuit = card.suit()

            if shist[asuit] >= 5:
                self.type = Hand.TYPE_FL
                self.flushcard = card

                if arank > flushtop[asuit]:
                    flushtop[asuit] = arank

            if freq > hf:
                nhf = hf
                hf  = freq
                nhfr = hfr
                hfr = arank
            elif freq == hf:
                if arank > hfr:
                    nhf = hf
                    hf  = freq
                    nhfr = hfr
                    hfr = arank
                elif arank < hfr:
                    if freq > nhf or arank >= nhfr:
                        nhf = freq
                        nhfr = arank
            elif freq > nhf:
                nhf = freq
                nhfr = arank
            elif freq == nhf and arank >= nhfr:
                nhfr = arank

        self.hi = hfr
        self.lo = nhfr

        # 4 2 1 or 4 3
        if bucketsum == 21 or bucketsum == 25:
            self.type = Hand.TYPE_4K

        # 3 2 1 1 or 3 2 2
        elif bucketsum == 15 or bucketsum == 17:
            self.type = Hand.TYPE_FH

        # 3 3 1 or 4 1 1 1
        elif bucketsum == 19:
            if hf == 4:
                self.type = Hand.TYPE_4K
            else:
                self.type = Hand.TYPE_FH

        # 2 2 2 1 or 3 1 1 1 1
        elif bucketsum == 13:
            if hf == 2:
                self.type = Hand.TYPE_2P
            else:
                self.straighthi = hicard
                if self.type == Hand.TYPE_FL:
                    if self.__isstraightflush():
                        self.type = Hand.TYPE_SF
                        #DEBUG
                        #print 'straighthi: %d' %self.straighthi
                        #DEBUG
                        self.hi = self.straighthi
                    else:
                        self.hi = flushtop[self.flushcard.suit()]
                elif self.__isstraight(rhist):
                    self.type = Hand.TYPE_ST
                    #DEBUG
                    #print 'straighthi: %d' %self.straighthi
                    #DEBUG
                    self.hi = self.straighthi
                else:
                    self.type = Hand.TYPE_3K
                        
        # 2 2 1 1 1
        elif bucketsum == 11:
            self.straighthi = hicard
            if self.type == Hand.TYPE_FL:
                if self.__isstraightflush():
                    self.type = Hand.TYPE_SF
                    #DEBUG
                    #print 'straighthi: %d' %self.straighthi
                    #DEBUG
                    self.hi = self.straighthi
                else:
                    self.hi = flushtop[self.flushcard.suit()]
            elif self.__isstraight(rhist):
                self.type = Hand.TYPE_ST
                #DEBUG
                #print 'straighthi: %d' %self.straighthi
                #DEBUG
                self.hi = self.straighthi
            else:
                self.type = Hand.TYPE_2P

        # 2 1 1 1 1 1
        elif bucketsum == 9:
            self.straighthi = hicard
            if self.type == Hand.TYPE_FL:
                if self.__isstraightflush():
                    self.type = Hand.TYPE_SF
                    #DEBUG
                    #print 'straighthi: %d' %self.straighthi
                    #DEBUG
                    self.hi = self.straighthi
                else:
                    self.hi = flushtop[self.flushcard.suit()]
            elif self.__isstraight(rhist):
                self.type = Hand.TYPE_ST
                #DEBUG
                #print 'straighthi: %d' %self.straighthi
                #DEBUG
                self.hi = self.straighthi
            else:
                self.type = Hand.TYPE_1P

        # 1 1 1 1 1 1 1
        elif bucketsum == 7:
            self.straighthi = hicard
            if self.type == Hand.TYPE_FL:
                if self.__isstraightflush():
                    self.type = Hand.TYPE_SF
                    #DEBUG
                    #print 'straighthi: %d' %self.straighthi
                    #DEBUG
                    self.hi = self.straighthi
                else:
                    self.hi = flushtop[self.flushcard.suit()]
            elif self.__isstraight(rhist):
                self.type = Hand.TYPE_ST
                #DEBUG
                #print 'straighthi: %d' %self.straighthi
                #DEBUG
                self.hi = self.straighthi
            else:
                self.type = Hand.TYPE_NP
                self.hi = hicard

        return self.type

    def showhole(self, color = False):
        #log.logger.debug('Hand.showhole()')

        if len(self.cards) >= 2:
            return '%2s %2s' % (self.cards[0].face(color), self.cards[1].face(color))
        else:
            return ''

    def rankorderstr(self):
        #log.logger.debug('Hand.rankorderstr()')

        buf = '('

        hisym = card.ranksym(self.hi)
        losym = card.ranksym(self.lo)
        str8hisym = card.ranksym(self.straighthi)

        if self.type not in [ Hand.TYPE_ST, Hand.TYPE_SF, Hand.TYPE_FH ]:
            self.prockickers()

        if self.type == Hand.TYPE_NP:
            buf += '%s ' % hisym
            for i in xrange(4):
                buf += card.ranksym(self.kickers[i].rank())
                buf += ' '
            buf = buf.strip()
            buf += ')'
        elif self.type == Hand.TYPE_1P:
            buf += '%s %s ' % (hisym, hisym)
            for i in xrange(3):
                buf += card.ranksym(self.kickers[i].rank())
                buf += ' '
            buf = buf.strip()
            buf += ')'
        elif self.type == Hand.TYPE_2P:
            buf += '%s %s %s %s ' % (hisym, hisym, losym, losym)
            buf += '%s)' % card.ranksym(self.kickers[0].rank())
        elif self.type == Hand.TYPE_3K:
            buf += '%s %s %s ' % (hisym, hisym, hisym)
            for i in xrange(2):
                buf += card.ranksym(self.kickers[i].rank())
                buf += ' '
            buf = buf.strip()
            buf += ')'
        elif self.type == Hand.TYPE_ST or self.type == Hand.TYPE_SF:
            buf += '%s ' % str8hisym
            for i in xrange(self.straighthi-1, self.straighthi-5, -1):
                buf += card.ranksym(i)
                buf += ' '
            buf = buf.strip()
            buf += ')'
        elif self.type == Hand.TYPE_FL:
            tmp = self.cards[:]
            tmp.sort()
            tmp.reverse()
            suitcards = 0
            for i in xrange(7):
                if tmp[i].suit() == self.flushcard.suit():
                    buf += card.ranksym(tmp[i].rank())
                    buf += ' '
                    if suitcards == 4:
                        break
                    suitcards += 1;
            buf = buf.strip()
            buf += ')'
        elif self.type == Hand.TYPE_FH:
            buf += '%s %s %s %s %s)' % (hisym, hisym, hisym, losym, losym)
        elif self.type == Hand.TYPE_4K:
            buf += '%s %s %s %s ' % (hisym, hisym, hisym, hisym)
            buf += card.ranksym(self.kickers[0].rank())
            buf += ')'
        else:
            log.logger.critical('Hand.rankorder: bad hand type!')
            log.logger.critical('%s' % str(self))
            buf +=  '*** ERROR***)'

        return buf

    def handtest(self):

        from deck import Deck
        import time

        handhist=[0,0,0,0,0,0,0,0,0]

        t1 = 0
        t2 = 0
        td = 0
        ndecks = 0
        chunksize = 1000
        x = 0
        y = 0
        first = True
        for x in xrange(1000):

            if not x % chunksize:

                y = 0

                if not first:
                    t2 = time.time()
                else:
                    first = False
                ndecks += chunksize
                td += t2 - t1
                decks = []
                for d in range(chunksize):
                    decks.append(Deck())
                    decks[d].shuffle()
            
                t1 = time.time()
                
            atype = Hand.TYPE_NP
            foo = Hand()
            for card in xrange(7):
                foo.addcard(decks[y].nextcard())

            handhist[foo.evaluate()] += 1

            y += 1


        # Display hand statistics
        count = 0
        for atype in handhist:
            count += atype

        TNHC = 23294460.0
        TN1P = 58627800.0
        TN2P = 31433400.0
        TN3K =  6461620.0
        TNST =  6180020.0
        TNFL =  4047644.0
        TNFH =  3473184.0
        TN4K =   224848.0
        TNSF =    41584.0
        TNH = 133784560.0

        factor = count / TNH

        expected = factor * TNHC
        error = float(handhist[Hand.TYPE_NP] - expected)/expected * 100
        print '%20s: %7d (%5.0f) %+.2f%%' % ('No Pair', handhist[Hand.TYPE_NP],                                              expected, error)
        
        expected = factor * TN1P
        error = float(handhist[Hand.TYPE_1P] - expected)/expected * 100
        print '%20s: %7d (%5.0f) %+.2f%%' % ('One Pair',
                                              handhist[Hand.TYPE_1P],expected,error)
        expected = factor * TN2P
        error = float(handhist[Hand.TYPE_2P] - expected)/expected * 100
        print '%20s: %7d (%5.0f) %+.02f%%' % ('Two Pair',
                                              handhist[Hand.TYPE_2P],expected,error)
        expected = factor * TN3K
        error = float(handhist[Hand.TYPE_3K] - expected)/expected * 100
        print '%20s: %7d (%5.0f) %+.02f%%' % ('Three of a Kind',
                                              handhist[Hand.TYPE_3K],expected,error)
        expected = factor * TNST
        error = float(handhist[Hand.TYPE_ST] - expected)/expected * 100
        print '%20s: %7d (%5.0f) %+.02f%%' % ('Straight',
                                              handhist[Hand.TYPE_ST],expected,error)
        expected = factor * TNFL
        error = float(handhist[Hand.TYPE_FL] - expected)/expected * 100
        print '%20s: %7d (%5.0f) %+.02f%%' % ('Flush',
                                              handhist[Hand.TYPE_FL],expected,error)
        expected = factor * TNFH
        error = float(handhist[Hand.TYPE_FH] - expected)/expected * 100
        print '%20s: %7d (%5.0f) %+.02f%%' % ('Full House',
                                              handhist[Hand.TYPE_FH],expected,error)
        expected = factor * TN4K
        error = float(handhist[Hand.TYPE_4K] - expected)/expected * 100
        print '%20s: %7d (%5.0f) %+.02f%%' % ('Four of a Kind',
                                              handhist[Hand.TYPE_4K],expected,error)
        expected = factor * TNSF
        error = float(handhist[Hand.TYPE_SF] - expected)/expected * 100
        print '%20s: %7d (%5.0f) %+.02f%%' % ('Straight Flush',
                                              handhist[Hand.TYPE_SF],expected,error)
        #print '%28d total hands' % count

        print "processed %d hands in %d seconds" % (sum, td)

if __name__ == '__main__':

    #######  2  3  4  5  6  7  8  9  T  J  Q  K  A

    #CLUBS#  0  1  2  3  4  5  6  7  8  9 10 11 12
    #DIAMD# 13 14 15 16 17 18 19 20 21 22 23 24 25
    #HEART# 26 27 28 29 30 31 32 33 34 35 36 37 38
    #SPADE# 39 40 41 42 43 44 45 46 47 48 49 50 51

    handhist=[0,0,0,0,0,0,0,0,0]
    foo = Hand()
    count = 0
    for c1 in xrange(0, 46):
        for c2 in xrange(c1 + 1, 47):
            for c3 in xrange(c2 + 1, 48):
                for c4 in xrange(c3 + 1, 49):
                    for c5 in xrange(c4 + 1, 50):
                        for c6 in xrange(c5 + 1, 51):
                            for c7 in xrange(c6 + 1, 52):
                                foo.addcard(card.Card(c1))
                                foo.addcard(card.Card(c2))
                                foo.addcard(card.Card(c3))
                                foo.addcard(card.Card(c4))
                                foo.addcard(card.Card(c5))
                                foo.addcard(card.Card(c6))
                                foo.addcard(card.Card(c7))

                                handhist[foo.evaluate()] += 1

                                foo.muck()

                                count += 1
                                if not count % 1000:
                                    print count, ' hands counted'

                                    asum = 0
                                    for bucket in handhist:
                                        asum += bucket
                                    print asum, ' hands in histogram'

                                    TNHC = 23294460.0
                                    TN1P = 58627800.0
                                    TN2P = 31433400.0
                                    TN3K =  6461620.0
                                    TNST =  6180020.0
                                    TNFL =  4047644.0
                                    TNFH =  3473184.0
                                    TN4K =   224848.0
                                    TNSF =    41584.0
                                    TNH = 133784560.0

                                    print "%20s: %12d" % ('Straight Flush', handhist[Hand.TYPE_SF])
                                    print "%20s: %12d" % ('Four of a Kind', handhist[Hand.TYPE_4K])
                                    print "%20s: %12d" % ('Full House', handhist[Hand.TYPE_FH])
                                    print "%20s: %12d" % ('Flush', handhist[Hand.TYPE_FL])
                                    print "%20s: %12d" % ('Straight', handhist[Hand.TYPE_ST])
                                    print "%20s: %12d" % ('Three of a Kind', handhist[Hand.TYPE_3K])
                                    print "%20s: %12d" % ('Two Pair', handhist[Hand.TYPE_2P])
                                    print "%20s: %12d" % ('One Pair', handhist[Hand.TYPE_1P])
                                    print "%20s: %12d" % ('No Pair', handhist[Hand.TYPE_NP])        

    print count, ' hands counted'

    asum = 0
    for bucket in handhist:
        asum += bucket
    print asum, ' hands in histogram'
        
    TNHC = 23294460.0
    TN1P = 58627800.0
    TN2P = 31433400.0
    TN3K =  6461620.0
    TNST =  6180020.0
    TNFL =  4047644.0
    TNFH =  3473184.0
    TN4K =   224848.0
    TNSF =    41584.0
    TNH = 133784560.0

    print "%20s: %12d" % ('Straight Flush', handhist[Hand.TYPE_SF])
    print "%20s: %12d" % ('Four of a Kind', handhist[Hand.TYPE_4K])
    print "%20s: %12d" % ('Full House', handhist[Hand.TYPE_FH])
    print "%20s: %12d" % ('Flush', handhist[Hand.TYPE_FL])
    print "%20s: %12d" % ('Straight', handhist[Hand.TYPE_ST])
    print "%20s: %12d" % ('Three of a Kind', handhist[Hand.TYPE_3K])
    print "%20s: %12d" % ('Two Pair', handhist[Hand.TYPE_2P])
    print "%20s: %12d" % ('One Pair', handhist[Hand.TYPE_1P])
    print "%20s: %12d" % ('No Pair', handhist[Hand.TYPE_NP])        
