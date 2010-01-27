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
from hand import Hand
from command import Command

class Player:
    MSG_T_ERROR = 0
    MSG_T_STATUS = 1
    MSG_T_CARDS = 2
    MSG_T_AAACK = 3
    MSG_T_HELP = 4
    MSG_T_NEWID = 5
    MSG_T_REMIND = 6
    MSG_T_GONE = 7
    MSG_T_BACK = 8
    MSG_HDR = {MSG_T_ERROR:'Error message',
               MSG_T_STATUS:'Status message',
               MSG_T_CARDS:'Your cards',
               MSG_T_AAACK:'Advance action acknowledgement',
               MSG_T_HELP:'Dealer commands',
               MSG_T_NEWID:'ID changed',
               MSG_T_REMIND:'Reminder',
               MSG_T_GONE:'Going on vacation',
               MSG_T_BACK:'Back from vacation'}

    def __init__(self, myid = 'INVALID!', nick = 'NoNick', level = 1):

        log.logger.debug('Player.__init__()')

        self.myid = myid
        self.pswd = ''
        self.nick = nick
        self.bankroll = 0
        self.oldbankroll = 0
        self.folded = True
        self.busted = False
        self.quit = False
        self.allin = False
        self.autofold = True
        self.won = 0
        self.lastbet = 0
        self.action = 0
        self.inplay = 0
        self.vacation = 0
        self.position = 0
        self.cmd = Command()
        self.hand = Hand()
        self.level = level

    #Sort based on total action
    def actionsort(self, other):
        log.logger.debug('Player.actionsort()')

        return cmp(self.inplay, other.inplay)

    # Note: This sorts in descending order
    def oldbrsort(self, other):
        log.logger.debug('Player.oldbrsort()')
        return cmp(other.oldbankroll, self.oldbankroll)


    def __str__(self):
        log.logger.debug('Player.__str__()')

        out = ''
        for thing in dir(self):
            attr = getattr(self, thing)
            if not callable(attr) and '__' not in thing:
                out = out + thing + '\t' + str(attr) + '\n'
        return out

    def active(self):
        log.logger.debug('Player.active()')

        return not (self.busted or self.folded)
