##
##    Uno - a plugin for pyGBot
##    Copyright (C) 2008 Morgan Lokhorst-Blight
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

#TODO: Implement the 'Uno' rule
#      Also, ability to challenge draw-fours, possibly with !challenge
import random

from pyGBot import log
from pyGBot.BasePlugin import BasePlugin

class Uno(BasePlugin):
    colours = ['B', 'G', 'R', 'Y']
    numbers = ['0','1','2','3','4','5','6','7','8','9']
    specials = ['SK','D2','RV']
    wilds = ['WLD', 'WD4']
    
    aliases = {'WLD': ['WILD'], 'WD4': ['WILD4', 'DRAW4', 'WLD4']}
    
    colournames = {'B': 'Blue', 'G': 'Green', 'R': 'Red', 'Y': 'Yellow'}
    colourcodes = {'B': '12', 'G': '3', 'R': '4', 'Y': '8'}

    handsize = 7
    maxplayers = 10 #108 / (handsize + 1)

    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        self.game_running = False

    def activate(self, channel=None):
        if channel == None:
            return False

        self.game_running = False

        self.channel = channel

        self.reset()

    def reset(self):
        self.generate_deck()
        self.players = []
        self.playerhands = {}
        self.discards = []

        self.current_player = ""
        self.direction = 1
        self.draw2total = 0
        self.draw4 = False
        self.wild = False
        self.wildcolour = ""
        self.waitdraw = False
        self.drawcard = ""

        self.usecolour = True

    def pubout(self, message):
        self.bot.pubout(self.channel, message)

    def user_part(self, channel, user):
        if channel == self.channel and user in self.players:
            self.player_leave(channel, user)

    def user_kicked(self, channel, user, kicker, message=""):
        if channel == self.channel and user in self.players:
            self.player_leave(channel, user)

    def user_nickchange(self, username, newname):
        if username in self.players:
            index = self.players.index(username)
            self.players.remove(username)
            self.players.insert(index, newname)

    def user_quit(self, user, reason=""):
        if user in self.players:
            self.player_leave(self.channel, user)        

    def msg_channel(self, channel, user, message):
        if message.startswith('!') and channel == self.channel:
            cmd = message[1:].strip()
            self.process_cmd(channel, user, cmd)
        elif message.startswith(self.bot.nickname + ':'):
            cmd = message[len(self.bot.nickname + ':'):].strip()
            self.process_cmd(channel, user, cmd)

    def msg_private(self, user, message):
        cmd = message.strip()
        self.process_cmd(user, user, cmd)

    def reply(self, channel, user, msg):
        if channel == user:
            # Replying to privmsg
            self.bot.noteout(user, msg)
        else:
            self.pubout('%s: %s' % (user, msg))

    def process_cmd(self, channel, user, cmd):
        args = cmd.lower().split(' ',1)
        cmdname = args[0]
        if len(args) > 1:
            args = args[1]
        else:
            args = ""

        cmdname = 'cmd_' + cmdname
        if hasattr(self, cmdname):
            f = getattr(self, cmdname)
            f(channel, user, args)

    def cmd_join(self, channel, user, args):
        if not self.game_running:
            self.player_join(channel, user)
        else:
            self.reply(channel, user, "You cannot join while a game is in progress. Please wait for the next game.")

    def cmd_quit(self, channel, user, args):
        self.player_leave(channel, user)

    def cmd_start(self, channel, user, args):
        self.start_game(channel, user)

    def cmd_hand(self, channel, user, args):
        if self.game_running and user in self.players:
            self.show_cards(user)

    def cmd_top(self, channel, user, args):
        if self.game_running:
            self.show_discard(channel)

    def cmd_turn(self, channel, user, args):
        if self.game_running:
            self.pubout('Current Player: %s' % self.current_player)

    def cmd_order(self, channel, user, args):
        if not self.game_running:
            return
        
        outlist = []
        outlist.append(self.current_player)
        
        p = self.get_next_player()
        
        while p != self.current_player:
            outlist.append(p)
            p = self.get_next_player(p)
        
        self.pubout('Order of turns: %s' % ', '.join(outlist))

    def cmd_draw(self, channel, user, args):
        if not self.game_running:
            return

        if user not in self.players:
            return

        if user != self.current_player:
            #log.logger.info("%s tried to act out of turn. It is %s's turn." % (user, self.current_player))
            self.reply(channel, user, 'It is not your turn.')
            return

        if self.waitdraw:
            self.reply(channel, user, 'You must either !play or !pass.')
            return

        if self.draw2total > 0:
            draw = self.draw2total
        elif self.draw4 == True:
            draw = 4
        else:
            draw = 1

        drawcards = []
        for i in range(0,draw):
            if len(self.deck) <= 1:
                self.reshuffle_discards()

            drawcards.append(self.deck.pop())

        self.bot.noteout(user, "You draw: %s" % (' '.join([self.card_render(x) for x in drawcards])))
        self.playerhands[self.current_player] += drawcards
        self.show_cards(self.current_player)

        if draw == 1:
            self.bot.noteout(user, 'If you would like to play this card, type !play. If you wish to pass, type !pass.')
            self.waitdraw = True
            self.drawcard = drawcards[0]
            return
        
        if self.draw4 == True:
            self.draw4 = False

        if self.draw2total > 0:
            self.draw2total = 0

        self.draw = 0

        self.next_player(channel)

    def cmd_play(self, channel, user, args):
        if not self.game_running:
            return

        if user not in self.players:
            return

        if user != self.current_player:
            self.reply(channel, user, 'It is not your turn.')
            return

        args = args.split()

        card_to_play = None
        
        # bit of a special case if we're stacking Draw 2's
        if self.draw2total > 0:
            if len(args) >= 1 and self.card_normalise(args[0]).endswith('D2'):
                card_to_play = self.card_normalise(args[0])
            else:
                for card in self.playerhands[self.current_player]:
                    if card.endswith('D2'):
                        card_to_play = card
            self.bot.noteout(user,'You do not have any draw two cards. You must accept the draw with !draw.')
        elif self.draw4 == True:
            self.bot.noteout(user,'You must draw four cards.')
            card_to_play = None
        elif self.waitdraw == True:
            card_to_play = self.drawcard
        else:
            card_to_play = self.card_normalise(args[0])

        if card_to_play != None and card_to_play != "":
            if self.play_card(channel, user, card_to_play):
                self.first_turn = False
                self.waitdraw = False                
                if self.wild and len(args) >= 2:
                    self.set_wild(args[1])

                if not self.wild:
                    self.show_discard(channel)
                    self.next_player(channel)

        if self.wild:
            self.bot.noteout(self.current_player,'You must select a colour with the !wild command.')


    def cmd_pass(self, channel, user, args):
        if user not in self.players:
            return
        
        if self.game_running:
            if user == self.current_player and self.waitdraw:
                self.waitdraw = False
                self.next_player(channel)
            else:
                self.bot.noteout(user, 'You shall not pass!')

    def cmd_challenge(self, channel, user, args):
        pass
                             
    def cmd_wild(self, channel, user, args):
        if not self.game_running:
            return

        if user not in self.players:
            return

        if user != self.current_player:
            return
            
        args = args.split(' ')

        if self.wild == True:
            self.set_wild(args[0])

        if not self.first_turn:
            self.show_discard(channel)
            self.next_player(channel)
            
    def set_wild(self, arg):
        if arg[0].upper() in Uno.colours:
            self.pubout('Setting wild colour to %s' % Uno.colournames[arg[0].upper()])
            self.wildcolour = arg[0].upper()
            self.wild = False
        else:
            self.pubout('Invalid colour.')

    def card_normalise(self, card):
        card = card.upper()
        
        if len(card) <= 1:
            card = ""
        elif len(card) == 2:
            card = card[0] + ' ' + card[1]
        elif len(card) > 3:
            if card in Uno.aliases['WLD']:
                card = 'WLD'
            elif card in Uno.aliases['WD4']:
                card = 'WD4'
            else:
                card = ""

        return card
        
    def get_next_player(self, player = None, direction = None):
        if direction == None or direction < -1 or direction > 1:
            direction = self.direction

        if player == None or player not in self.players:
            currindex = self.players.index(self.current_player)
        else:
            currindex = self.players.index(player)

        if currindex == len(self.players) - 1 and direction == 1:
            currindex = 0
        elif currindex == 0 and direction == -1:
            currindex = len(self.players) - 1
        else:
            currindex += direction

        return self.players[currindex]
            
    def next_player(self, channel):
        self.current_player = self.get_next_player()
        self.first_turn = False
        self.pubout('%s\'s turn!' % self.current_player)

        self.show_cards(self.current_player)

        if self.draw2total > 0:
            self.bot.noteout(self.current_player,'You must either draw %d cards or play a draw two card from your hand. Type !draw to draw the cards, or use !play to play a draw two card, if you have one.' % self.draw2total)
        elif self.draw4 == True:
            self.bot.noteout(self.current_player,'You must draw four cards.')

    def skip_player(self):
        self.current_player = self.get_next_player()
        
    def do_reverse(self):
        self.direction *= -1

    def do_drawtwo(self):
        self.draw2total += 2

    def do_skip(self):
        self.skip_player()
        self.pubout('A Skip card was played, so %s\'s turn will be skipped.' % self.current_player)

    def start_game(self, channel, user):
        if user not in self.players:
            self.player_join(channel, user)

        if len(self.players) < 2:
            self.pubout('Unable to start game. Not enough players.')
            return

        self.game_running = True
        self.pubout('Starting game!')

        self.current_player = self.players[-1]

        self.deal_game(channel)


    def player_join(self, channel, player):
        if player not in self.players:
            if len(self.players) < Uno.maxplayers:
                self.pubout('%s has joined the game.' % player)
                self.players.append(player)
                #log.logger.info(repr(self.players))
            else:
                self.reply(channel, player, 'Sorry, there are too many players.')
        else:
            self.reply(channel, player, 'You are already in the game!')

    def player_leave(self, channel, player):
        if player in self.players:
            self.pubout('%s has left the game.' % player)

            if self.playerhands.has_key(player):
                self.deck += self.playerhands[player]
                del self.playerhands[player]

            if self.current_player == player:
                self.pubout("It was %s's turn." % player)
                self.next_player(channel)

            self.players.remove(player)
            if self.check_win_conditions(channel):
                return
        else:
            self.reply(channel, player, 'You are not in the game.')

    def generate_deck(self):
        suitcards = [' ' + x for x in Uno.numbers] * 2 + Uno.specials * 2
        suitcards.remove(' 0')
        suitcards.sort()

        self.deck = []
        for colour in Uno.colours:
            self.deck += [colour + x for x in suitcards]
        self.deck += Uno.wilds * 4

    def deal_game(self,channel):
        random.shuffle(self.deck)
        
        for player in self.players:
            self.playerhands[player] = []
            for i in range(0, Uno.handsize):
                self.playerhands[player].append(self.deck.pop())
            self.show_cards(player)

        self.discards.append(self.deck.pop())

        while self.discards[-1] == 'WD4':
            self.deck.insert(random.randint(0, len(self.deck) - 2), self.discards.pop())
            self.discards.append(self.deck.pop())
        if self.discards[-1][1:] == 'SK':
            self.do_skip()
        elif self.discards[-1][1:] == 'D2':
            self.do_drawtwo()
        elif self.discards[-1][1:] == 'RV':
            self.do_reverse()
        elif self.discards[-1] == 'WLD':
            self.wild = True

        self.show_discard(channel)
        self.next_player(channel)

        self.first_turn = True        
        
        if self.wild == True:
            self.bot.noteout(self.current_player,'You must select a colour with the !wild command. You may then play a card from your hand.')


    def reshuffle_discards(self):
        top = self.discards.pop()
        self.deck.extend(self.discards)
        self.discards = []

        random.shuffle(self.deck)
        
    def card_render(self, card):
        if self.usecolour:
            text = "[\x02"
            if card == "WLD":
                text += "\x033W\x034I\x038L\x0312D\x0F" # "WILD" in four different colours
            elif card == "WD4":
                text += "\x033W\x034L\x038D\x03124\x0F" # "WLD4" in four different colours
            else:
                code = Uno.colourcodes[card[0]]
                text += '\x03' + code + card + '\x0F'
            text += "\x0F]"
        else:
            text = "[%s]" % card

        return text

    def card_compare(self, x, y):
        if x in Uno.wilds and y in Uno.wilds:
            return Uno.wilds.index(x) - Uno.wilds.index(y)
        elif x in Uno.wilds and y not in Uno.wilds:
            return 1
        elif x not in Uno.wilds and y in Uno.wilds:
            return -1
        else:
            # NB This is not safe if strings are different lengths
            for c in range(0, len(x)):
                if x[c] < y[c]:
                    return -1
                elif x[c] > y[c]:
                    return 1
            return 0

    def show_cards(self, player):
        msg = ""
        self.playerhands[player].sort(cmp=self.card_compare)
        for card in self.playerhands[player]:
            msg += self.card_render(card) #"[" + card + "] "

        msg = msg.strip()
        self.bot.noteout(player,msg)

    def show_discard(self, channel):
        self.pubout("Top card: %s" % self.card_render(self.discards[-1]))
        if self.discards[-1][0] == 'W':
            if self.wildcolour != '':
                self.pubout('Wild colour: \x02\x03%s%s\x0F' % (Uno.colourcodes[self.wildcolour], Uno.colournames[self.wildcolour]))
            else:
                self.pubout('No wild colour chosen.')
        
    def play_card(self, channel, user, card):
        valid = False

        card = self.card_normalise(card)

        #log.logger.info('Attempting to play card %s for user %s' % (card, user))

        if card == "WLD" or card == "WD4":
            valid = True

        if len(card) < 3:
            self.bot.noteout(user, 'Invalid card.')
            valid = False
        elif card[0] == self.discards[-1][0]:
            # colour match
            valid = True
        elif card[1:] == self.discards[-1][1:]:
            # value match
            valid = True
        elif self.discards[-1][0] == 'W' and card[0] == self.wildcolour:
            valid = True

        if card not in self.playerhands[self.current_player]:
            self.bot.noteout(user, 'You do not have that card in your hand.')
            valid = False

        if valid:
            self.playerhands[user].remove(card)
            self.discards.append(card)

            if self.check_win_conditions(channel):
                return

            if card[1:] == 'SK':
                self.do_skip()
            elif card[1:] == 'D2':
                self.do_drawtwo()
            elif card[1:] == 'RV':
                self.do_reverse()
            elif card == 'WD4':
                self.wild = True
                self.draw4 = True
            elif card == "WLD":
                self.wild = True

            return True
        else:
            return False


    def check_win_conditions(self, channel):
        if not self.game_running:
            return False
        
        if len(self.playerhands[self.current_player]) == 0:
            self.pubout('We have a winner! %s has won the game.' % self.current_player)
            self.game_running = False
            self.reset()
            return True
        elif len(self.players) == 1:
            self.pubout('We have a winner by default! %s has won the game, since there is no one left to play against them.' % self.current_player)
            self.game_running = False
            self.reset()
            return True
        else:
            return False
