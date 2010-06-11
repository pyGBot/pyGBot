##
##    Fluxx - a plugin for pyGBot
##    Copyright (C) 2009 JP St. Pierre
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

from pyGBot import log
from pyGBot.BasePlugin import BasePlugin

from pyGBot.Plugins.games.fluxxfiles.fluxx import FluxxPlayer, FluxxGame
from pyGBot.Plugins.games.fluxxfiles.game import pretty_print_list, pp_index
from pyGBot.Plugins.games.fluxxfiles.deck import FluxxDeck

# IRC formatting
BOLD      ='\x02' # Bold
UNDERLINE ='\x1F' # Underline
REV_VIDEO ='\x16' # Reverse Video

# Used for looking up card descriptions.
dummy_deck = FluxxDeck()

YES_NO_RESPONSE = '(yes|true|no|false|0|1)'

class FluxxIRCGame(FluxxGame):
    def post_deal_hook(self):
        for p in self.players:
            p.output("You got: %s" % pp_index(p.hand))

class FluxxIRCUser(FluxxPlayer):

    _halt_game = None
    
    def __init__(self, name, plugin):
        FluxxPlayer.__init__(self, name)
        self.name = name
        self.plugin = plugin
        self.game = plugin.game
    
    def win(self):
        self.plugin.pubout("%s won the game!" % (self.name,))
        self.plugin.end()
        self.game = None
    
    def start_turn(self):
        
        def callback(message):
            if not message.isdigit():
                player.output("That is not a number")
                return ask()
            t = int(message)
            if 0 < t <= len(self.hand):
                card = self.hand.cards[t-1]
                card.play(self)
                self.plugin.pubout("%s played %s." % (self.name, card))
                self.play_amount += 1
                self.halt_game = None
                return True
            player.output("That is not between 1 and %d" % len(self.p.hand))
            return self

        def ask():
            player.request_input("Choose a number from 1 to %d" % len(self.hand), 
                                 (callback, '|'.join(str(n+1) for n in xrange(len(self.hand)))))
    
        log.logger.info("Starting %s's turn" % self.name)
        self.output("It is now your turn.")
        self.plugin.pubout("It is now %s's turn." % self.name)
        
        hand_str = pp_index(self.hand)
        if hand_str == "":
            hand_str = " no cards."
        else:
            hand_str = ": " + hand_str
        self.output('Your hand contains%s' % hand_str)
        
        rules = self.game.rule_pile
        if rules.no_hand_bonus(self) > 0:
            cards = self.draw(rules.no_hand_bonus(self))
            self.output(self.name, "You drew: " + pp_index(cards))
            
        if rules.is_first_play_random and len(self.hand) > 1 and self.game.rule_pile.draw_amount > 1:
            log.logger.info("FPR in effect")
            # First play random rules.
            t = self.game.turn-1
            if t < 0:
                player = self.game.players[-1]
            else:
                player = self.game.players[t]
            self.plugin.pubout(("%s must choose the first card from " +
                                 "%s's hand.") % (player.name, self.name))
            self.halt_game = "First Play Random"
            ask()
            
        d, p = self.can_draw_amount, self.can_play_amount
        self.draw_amount = self.play_amount = 0
        self.output("You can draw %d card%s, and play %s card%s." % \
                            (d, "" if d == 1 else "s", "all" if p == 0 else p, \
                                "" if p == 1 else "s"))
    
    def request_input(self, question, callback):
        self.output(question)
        self.plugin.user_handlers[self.name.lower()] = callback

    def output(self, message):
        self.plugin.privout(self.name, message)

    @property
    def halt_game(self):
        return self._halt_game

    @halt_game.setter
    def halt_game(self, value):
        self._halt_game = value
        if value is None:
            self.plugin.turn_postfix(self)
        
class Fluxx(BasePlugin):
    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        self.options = options
        self.users = {}
        self.user_handlers = {}

    def pubout(self, msg):
        self.privout(self.channel, msg)

    def privout(self, user, message):
        for msg in message.strip().splitlines():
            if "%S" in msg:
                msg = msg.replace("%S", "")
                if msg == '': msg = '   '
            else:
                msg = msg.strip()
            self.bot.privout(user, msg
                            .replace('%B', BOLD)
                            .replace('%U', UNDERLINE)
                            .replace('%V', REV_VIDEO))

    def noteout(self, user, msg):
        self.bot.noteout(user, msg)

    def activate(self, channel=None):
        self.channel = channel or '#'+self.options['channel']

    # Event handlers for other users
    def user_join(self, channel, username):
        log.logger.info("%s joined %s" % (username, channel))

    def user_part(self, channel, username):
        log.logger.info("%s left %s" % (username, channel))

    def user_quit(self, username, reason=""):
        self.user_part("", username)

    def user_nickchange(self, oldName, newName):
        log.logger.info("%s changed nicks to %s" % (oldName, newName))
        oldName, newName = oldName.lower(), newName.lower()
        if oldName in self.user_handlers:
            self.user_handlers[newName] = self.user_handlers[oldName]
            del self.user_handlers[oldName]
        if oldName in self.users:
            self.users[newName] = self.users[oldName]
            del self.users[oldName]

    # Event handlers for this bot
    def bot_connect(self):
        pass

    def bot_join(self, channel):
        log.logger.info("Joined %s" % channel)

    # def bot_kicked(self, channel, kicker="", reason=""):
    #     print "Kicked from %s by %s: %s" % (channel, kicker, message)
    #     def kickedFromCallback(message):
    #         if len(message) > 0 and message[0].lower() in "yt1":
    #             self.privout(kicker, "Okay, I'll go away. To start a new" +
    #                          "game in a new channel, type /msg %s !startgame " +
    #                          "#channel to me! To finish off this game at " +
    #                          "another time, /msg %s !startgame #channel %d" \
    #                              % (self.nickname, self.nickname, \
    #                                 self.channels[channel].game_no))
    #             del self.channels[channel]
    #         else:
    #             self.privout(kicker, "Okay, I'll join again with the same game.")
    #             self.join(channel)
    #         return True
    #     kicker = split_user(kicker)
    #     self.privout(kicker.nick, "You kicked me. Do you want me to " +
    #                  "stop playing Fluxx in %s? (y/n)" % channel)
    #     self.user_handlers[kicker.host] = (kickedFromCallback(), YES_NO_RESPONSE)

    def bot_disconnect(self):
        pass


    # Event handlers for incoming messages
    def msg_channel(self, channel, user, message):
        self.processmessage(channel, user, message)
    
    def msg_private(self, user, message):
        self.processmessage(self.bot.nickname, user, message, addressed=True)

    def channel_names(self, channel, nameslist):
        pass

    def processmessage(self, channel, user, message, addressed=False):
        log.logger.info("Received message from %s in %s: %s" % (user, channel, message))

        messageR = message
        
        if message.startswith(self.bot.nickname):
            messageR = message[len(self.bot.nickname):].strip()
            if len(message) and message[0] in ":,":
                messageR = messageR[1:].strip()
                addressed = True
                
        if message[0] == '!':
            messageR = message[1:].strip()
            addressed = True
            
        if addressed:
            L = messageR.split()
            command = L[0]
            if len(L) > 1:
                args = L[1:]
            else:
                args = []
            
            if command in command_aliases:
                command = command_aliases[command]
            if not self.check_callback(channel, user, message, True):
                if command not in command_handlers:
                    if channel == self.bot.nickname:
                        channel = user
                    return self.privout(channel, "Sorry %s, I don't know command '!%s'" % \
                                            (user, command))
                else:
                    command_handlers[command](self, channel, user, args)
            else:
                self.check_callback(channel, user, message)

    def end(self):
        self.game = None
        self.users = {}
        self.user_handlers = {}
        self.pubout("The game has ended.")
    
    def check_callback(self, channel, user, message, check=False):
        user = user.lower()
        if user in self.user_handlers:
            handler = self.user_handlers[user]
            if not callable(handler) and len(handler) == 2:
                handler, regex = handler
            else:
                regex = None
            if regex is None or re.match(regex, message, re.I):
                if check: return True
                if channel == self.bot.nickname:
                    if handler(message):
                        del self.user_handlers[user]
                else:
                    self.pubout(("Sorry %s, you must respond in a "
                                 "private message.") % user)

        if check: return False

    def help(self, channel, user, params):
        helpText = {
            'commands': """
            My commands are: cardinfo, draw, play, currentgoal,
                             listrules, listhand, listkeepers, queue,
                             help, search, startgame, endgame
            %S
            Say %B!help %UCOMMAND%U%B for help with each command.
            """,
            
            'startgame': """
            Syntax:    %B!startgame
            Start a game in this channel.
            Aliases:   !start, !s
            """,

            'endgame': """
            Syntax:    %B!endgame
            End the current game.
            Aliases:   !end, !e
            """,
            
            'cardinfo': """
            Syntax:    %B!cardinfo %Ushortname%U%B
            Find the description of a card by its internal name.
            For instance, the Keeper love has an internal name
            of 'K_LO'. You can find a card's internal name when
            it is in play by using !listhand, !listkeepers,
            !listrules or !currentgoal, or use !search to find
            a card.
            Aliases:   !info, !i
            """,
            
            'draw': """
            Syntax:    %B!draw%B
            Draw the maximum number of cards allowed from the draw pile.
            
            Syntax:    %B!draw %Unumcards%U%B
            Draw a number of cards from the draw pile.
            Aliases:   !d
            """,
            
            'play': """
            Syntax:    %B!play %Ucard%U%B
            Play card 'card'. Card can either be card number in
            your hand or an internal name like 'K_LO' for 'Love'.
            Aliases:   !p
            """,
            
            'currentgoal': """
            Syntax:    %B!currentgoal%B
            Say the current goal.
            Aliases:   !goal, !g
            """,
            
            'listrules': """
            Syntax:    %B!listrules%B
            List the current rules.
            Aliases:   !rules, !r
            """,
            
            'listhand': """
            Syntax:    %B!listhand%B
            List your current hand.
            Aliases:   !hand, !h
            """,
            
            'listkeepers': """
            Syntax:    %B!listkeepers%B
            List your current keeper pile.
            Syntax:    %B!listkeepers %Uusername%U%B
            List the keepers of 'username'.
            Aliases:   !keepers, !k
            """,
            
            'join': """
            Syntax:    %B!join%B
            Join the game.
            Aliases:   !j
            """,
            
            'help': """
            Syntax:    %B!help%B
            ...
            Aliases:   !?
            """,
            
            'search': """
            Syntax:    %B!search %Uparameters%U%B
            Search for a specific card.
            Aliases:   !find
            """}
        if len(params) == 0:
            command = ''
        else:
            command = params[0].strip().lower()
        if len(command) > 0 and command[0] == "!":
            command = command[1:]
        command = command.strip()
        if command in command_aliases:
            command = command_aliases[command]
        if command not in helpText:
            command = 'commands'
        if channel == self.bot.nickname:
            channel = user
        self.privout(channel, helpText[command])

    def _invalidCommandPrefix(noPrivate=False, needGameStarted=False,
                              needGameNotStarted=False, needUserInGame=False,
                              needCurrentTurn=False, needNoGame=False, needGame=False):
        def internal(func):
            def internal2(self, channel, user, params=[]):
                if channel == self.bot.nickname:
                    channel = user
                else:
                    self.channel = channel
                if noPrivate and channel == user:
                    return self.privout(channel, "You can not use this command " +
                                             "in a private message.")

                if needNoGame and getattr(self, "game", None) is not None:
                    return self.privout(channel, "You can not use this command " +
                                             "with a game starting.")

                if needGame and getattr(self, "game", None) is None:
                    return self.privout(channel, "You can not use this command " +
                                             "without a game starting or in progress.")
                
                hasGameStarted = getattr(self, "game", None) and self.game.started
                
                if needGameStarted and not hasGameStarted:
                    return self.privout(channel, "You can not use this command in a " +
                                             "channel without a game in progress.")
                
                if needGameNotStarted and hasGameStarted:
                    return self.privout(channel, "You can not use this command in a " +
                                             "channel with a game in progress.")
                
                if needUserInGame and (user.lower() not in self.users or not hasGameStarted):
                    return self.privout(channel, "You are not in the current game.")
                
                if needCurrentTurn and not self.users[user.lower()].is_turn:
                    return self.privout(channel, "It is not your turn.")
                
                return func(self, channel, user, params)
            return internal2
        return internal

    @_invalidCommandPrefix(noPrivate=True, needGameNotStarted=True)
    def start_game(self, msg_channel, user, params):
        def printHelp():
            self.privout(msg_channel, """
            Syntax:    %B!startgame
            Please say or message !help startgame for more information.
            """)
            
        def startGame_(debug):
            self.game = FluxxIRCGame()
            self.game.debug = debug
            self.pubout("A new Fluxx game has started.")
            self.pubout("Any players who wish to play Fluxx please say !join.")
            self.join(self.channel, user)
            self.privout(user, "When you are ready to start the game, say '!startgame'")

        if getattr(self, "game", None) is not None:
            self.pubout("The game is now starting. Please use !draw and !play to draw and play.")
            self.game.start_game()
        
        elif len(params) == 0:
            startGame_(False)
        elif len(params) == 1 and params[0] == "d3bugh4x0r":
            startGame_(True)
        else:
            return printHelp()

    @_invalidCommandPrefix(noPrivate=True, needGame=True, needUserInGame=True, needGameNotStarted=True)
    def quit(self, msg_channel, user, params):
        self.game.players.remove(self.users[user])

    @_invalidCommandPrefix(noPrivate=True)
    def status(self, msg_channel, user, params):
        if getattr(self, "game", None) is None:
            self.privout(msg_channel, "No game is in progress.")
        elif self.game.started:
            self.privout(msg_channel, "A game is in progress.")
        else:
            self.privout(msg_channel,
                         "A game is starting, the queue contains: " + \
                             pretty_print_list(self.game.players))
    
    @_invalidCommandPrefix(noPrivate=True, needGame=True)
    def end_game(self, msg_channel, user, params):
        self.end()

    def card_info(self, channel, user, params):
        def printHelp():
            self.privout(channel, """
            Syntax:    %B!cardinfo %Ushortname%U%B
            Please say or message !help cardinfo for more information.
            """)
            
        if channel == self.bot.nickname:
            channel = user
        
        if len(params) != 1:
            return printHelp()
        
        card = params[0].upper()
        if card in dummy_deck:
            self.privout(channel, dummy_deck.find_card(params[0].upper()).card_info)
        else:
            self.privout(channel, "Sorry, I could not find card '%s'" % card)

    def search(self, user, channel, params):
        def printHelp():
            self.privout(channel, """
            Syntax:    %B!search %Uparameters%U%B
            Please say or message !help search for more information.
            """)

        if channel == self.bot.nickname:
            channel = user

        search = ' '.join(params).lower()
        cards = []
        for card in dummy_deck.cards:
            if search in card.title.lower() or \
               search in card.short_title.lower() or \
               search in card.description.lower() or \
               search in card.type.lower():
                   cards.append(card)
        
        self.privout(channel, "Your search results for '%s'" % ' '.join(params))
        self.privout(channel, '%%S    %s\n'*len(cards) % tuple(cards))

    def turn_postfix(self, player):

        def callback():
            p_count = len(player.game.players)
            self.turn_count += 1
            if self.turn_count >= p_count - 1 and player.halt_game is None and \
                    player.draws_left <= 0 and \
                    (player.plays_left <= 0 or len(player.hand) <= 0):
                player.finish_turn()
        
        self.turn_count = 0
        if player.draws_left > 0 and player.plays_left <= 0: # Auto-draw for a player.
            handlen = len(player.hand)
            cards = player.draw(0)
            player.draw_amount += len(cards)
            player.output("You auto-drew: " + pp_index(cards, handlen))
        # Check for winnage.
        if player.game.current_goal is not None:
            player.game.current_goal.check_for_win(player.game)
        for p in player.game.players:
            if p != player:
                p.enforce_limits(callback)
        if len(player.game.players) == 1:
            callback()
        
    @_invalidCommandPrefix(needUserInGame=True, needCurrentTurn=True)
    def draw(self, channel, user, params):
        def printHelp():
            self.privout(channel, """
            Syntax:    %B!draw [%Unumcards%U]%B
            Please say or message !help draw for more information.
            """)
        if len(params) == 0:
            num_cards = 0
        elif len(params) == 1 and params[0].isdigit():
            num_cards = int(params[0])
        else:
            return printHelp()
        
        player = self.users[user.lower()]
        handlen = len(player.hand)
        if player.halt_game is not None:
            return self.privout(channel, ("You cannot draw a card while %s " + \
                                      "is in effect.") % player.halt_game)
        cards = player.draw(num_cards)
        if cards is None:
            return self.turn_postfix(player)
        player.draw_amount += len(cards)
        # Make sure to reply to user
        # Don't show the cards in public!
        self.privout(user, "You drew: " + pp_index(cards, handlen+1))
        if player.draws_left > 0:
            self.privout(user, "You can draw %d more card%s." % \
                    (player.draws_left, "" if player.draws_left else "s"))
        self.turn_postfix(player)
        return cards
    
    @_invalidCommandPrefix(needUserInGame=True, needCurrentTurn=True)
    def play(self, channel, user, params):
        def printHelp():
            self.privout(channel, """
            Syntax:    %B!play [%Ucard%U]%B
            Please say or message !help draw for more information.
            """)
        if len(params) != 1:
            return printHelp()
        card = params[0].upper()
        player = self.users[user.lower()]
        if player.plays_left <= 0:
            return self.privout(channel, "You cannot play another card.")
        if player.halt_game is not None:
            return self.privout(channel, ("You cannot play a card while %s " + \
                                     "is in effect.") % player.halt_game)
        hand = player.hand
        if len(hand) == 0:
            self.turn_postfix(player)
        if card.isdigit(): # Hand index
            card = int(card)
            handlen = len(hand)
            if card > handlen:
                return self.privout(user, "You only have %d card%s in your hand."
                                      % (handlen, "" if handlen == 1 else "s"))
            card = hand.cards[card-1]
        elif card not in hand: # Short name case 1.
            if card in dummy_deck:
                return self.privout(user, ("You do not have card '%s' in " +
                                            "your hand.") % card)
            else:
                return self.privout(channel, ("There is no such card '%s'. " +
                                          "Please use !help play to find " +
                                          "out how to find the short name " +
                                          "of a card.") % card)
        else: # Short name
            card = hand.find_card(card)

        self.pubout("%s played %s." % (user, card))
        card.play(player)
        player.play_amount += 1
        if player.plays_left > 0:
            self.privout(user, "You can play %d more card%s." % \
                    (player.plays_left, "" if player.plays_left == 1 else "s"))
        self.turn_postfix(player)
    
    @_invalidCommandPrefix(noPrivate=True, needGameNotStarted=True)
    def join(self, channel, user, params=[]):

        if user.lower() in self.users:
            return self.privout(channel, "%s was already in the queue!" % user)
        
        userobj = FluxxIRCUser(user, self)
        self.users[user.lower()] = userobj
        
        self.privout(channel, "%s was added to the queue." % user)
        self.game.add_player(userobj)
        
    @_invalidCommandPrefix(needGameStarted=True)
    def current_goal(self, channel, user, params):
        goal = self.users[user.lower()].game.current_goal
        if goal is None:
            self.privout(channel, "There is no goal yet.")
        else:
            self.privout(channel, "The current goal is %s" % goal)
        
    @_invalidCommandPrefix(needGameStarted=True)
    def list_rules(self, channel, user, params):
        rules = self.users[user.lower()].game.rule_pile
        hl = rules.hand_limit
        kl = rules.keeper_limit
        self.privout(channel, '''
The rules are: %s
Draw %d, Play %s, %sHand Limit%s, %sKeeper Limit%s. Bonuses are \
not added because they vary per player.''' % (rules,
                                              rules.draw_amount, rules.play_amount,
                                              "No " if hl == -1 else "",
                                              "" if hl == -1 else " %d" % hl,
                                              "No " if kl == -1 else "",
                                              "" if kl == -1 else " %d" % kl))
        
    @_invalidCommandPrefix(needGameStarted=True, needUserInGame=True)
    def list_hand(self, channel, user, params):
        hand_str = ["%d: %s" % (i+1, c) for i, c in \
                    enumerate(self.users[user.lower()].hand)]
        hand_str = pretty_print_list(hand_str)
        if hand_str == "":
            hand_str = " no cards."
        else:
            hand_str = ": " + hand_str
        self.privout(user, 'Your hand contains%s' % hand_str)
        
    @_invalidCommandPrefix(needGameStarted=True)
    def list_keepers(self, channel, user, params):
        def printHelp():
            self.privout(channel, """
            Syntax:    %B!listkeepers [%Uuser%U]%B
            Please say or message !help listkeepers for more information.
            """)
        if len(params) == 1:
            keepUser, keepUserStr = params[0].lower(), "%s's" % params[0]
        elif len(params) == 0:
            keepUser, keepUserStr = user.lower(), "Your"
        else:
            return printHelp()
        keep_str = pretty_print_list(self.users[keepUser].keepers.cards)
        if keep_str == "":
            keep_str = " no keepers."
        else:
            keep_str = ": " + keep_str
        if keepUser not in self.users or self.users[keepUser] not in \
               self.users[user.lower()].game.players:
            return self.privout(channel, "There is no user in this channel " +
                            "by the nickname '%s'" % keepUser)
        self.privout(channel, '%s keeper pile contains%s' % (keepUserStr, keep_str))

    def debug(self, channel, user, params):
        log.logger.info("%s tried to use the debug command!" % user)
        
        if not self.game.debug:
            return

        command = params[0]
        
        if command == "g": # give
            card, give_user = params[1], params[2].lower()
            self.users[give_user].hand.receive(self.game.deck.find_card(card))
            
        elif command == "p":
            card = params[1]
            g.deck.find_card(card).play(self.users[user])

        
command_handlers = {
    'endgame':        Fluxx.end_game,
    'startgame':      Fluxx.start_game,
    'cardinfo':       Fluxx.card_info,
    'draw':           Fluxx.draw,
    'play':           Fluxx.play,
    'currentgoal':    Fluxx.current_goal,
    'listrules':      Fluxx.list_rules,
    'listhand':       Fluxx.list_hand,
    'listkeepers':    Fluxx.list_keepers,
    'join':           Fluxx.join,
    'help':           Fluxx.help,
    'search':         Fluxx.search,
    'debug':          Fluxx.debug,
    'status':         Fluxx.status,
}
            
command_aliases = {
    'e':        'endgame',
    'end':      'endgame',
    's':        'startgame',
    'start':    'startgame',
    'i':        'cardinfo',
    'info':     'cardinfo',
    'd':        'draw',
    'p':        'play',
    'g':        'currentgoal',
    'goal':     'currentgoal',
    'r':        'listrules',
    'rules':    'listrules',
    'hand':     'listhand',
    'lh':       'listhand',
    'h':        'listhand',
    'keepers':  'listkeepers',
    'lk':       'listkeepers',
    'k':        'listkeepers',
    'j':        'join',
    '?':        'help',
    'u':        'status',
    'stats':    'status',
    'q':        'quit',
    'find':     'search',
}
