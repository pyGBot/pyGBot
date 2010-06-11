
from pyGBot.Plugins.games.fluxxfiles.game import Card, CardPile, Player, pretty_print_list

class FluxxGame(object):

    is_removable = False
    
    def __init__(self):
        from pyGBot.Plugins.games.fluxxfiles.deck import FluxxDeck
        self.started = False
        self.finished = False
        self.debug = False
        self.deck = FluxxDeck()
        self.rule_pile = RulePile(self)
        self.draw_discard = DrawDiscard(self)
        self.players = []
        self.turn = 0
        self.current_goal = None
        self.game = self
        self.reverse_played = False
        self.another_turn_played = False

    def add_player(self, player):
        player.game = self
        self.players.append(player)
        
    def deal(self):
        # Set the basic rules card (R_BASIC) on the board.
        self.rule_pile.receive(self.deck.find_card("R_BASIC"))
        # Give all our undealt cards (every card except R_BASIC)
        # to the draw pile.
        self.draw_discard.draw_pile.receive(self.deck.undealt_cards)
        self.draw_discard.draw_pile.shuffle()
        for player in self.players:
            player.hand = FluxxHand()
        # Deal 3 cards to each player.
        self.draw_discard.deal(self.players, 3)
        self.post_deal_hook()
    
    def start_game(self):
        # Deal to our players.
        self.started = True
        self.deal()
        self.player.start_turn()

    @property
    def current_player(self):
        return self.players[self.turn]
    
    def get_player(self, player=None, modifier=1):
        num_players = len(self.players)
        if player is None:
            turn = self.turn
        else:
            try:
                # player is a player obj
                turn = self.players.index(player)
            except ValueError:
                # player is an index
                turn = player
        turn += modifier
        if turn < 0:
            return turn+num_players
        elif turn >= num_players:
            return turn-num_players
        return turn

    def next_player(self, player=None):
        return self.get_player(player, self.rule_pile.turn_order)

    def prev_player(self, player=None):
        return self.get_player(player, -self.rule_pile.turn_order)
    
    def next_turn(self):
        num_players = len(self.players)
        # Check if reverse order was just played, and if there's only two people
        if not ((self.reverse_played and num_players == 2) or self.another_turn_played):
            self.turn = self.next_player()
            
        self.players[self.turn].start_turn()
        
        self.reverse_played = False # Turn off reverse_played
        self.another_turn_played = False # Turn off another_turn_played
        
    def draw_cards(self, num_cards):
        # Utility function for us.
        return self.draw_discard.draw(num_cards)
    
    def discard(self, cards):
        # Utility function for us.
        print "Discarding %r" % cards
        self.draw_discard.discard(cards)

    @property
    def player(self):
        return self.players[self.turn]

    def post_deal_hook(self):
        pass

discard_regex = "(!(discard|d) )?([0-9 ]+)|([%s]_[a-z0-9_]+)"

class FluxxPlayer(Player):
    
    game = None
    draw_amount = 0
    play_amount = 0
    
    def __init__(self, name=None):
        Player.__init__(self, name)
        self.keepers = KeeperPile()
        self.keepers.player = self

    @property
    def can_draw_amount(self):
        return self.game.rule_pile.draw_amount + self.game.rule_pile.poor_bonus(self)

    @property
    def can_play_amount(self):
        return self.game.rule_pile.play_amount + self.game.rule_pile.rich_bonus(self)
    
    @property
    def draws_left(self):
        return self.can_draw_amount - self.draw_amount

    @property
    def plays_left(self):
        p = self.can_play_amount
        if hasattr(p, "magic"): # PlayAllRuleCard
            return len(self.hand)
        return p - self.play_amount
    
    @property
    def is_turn(self):
        return self.game.player == self
    
    def request_input(self, question, callback):
        # For the client to implement.
        pass
    
    def output(self):
        # For the client to implement.
        pass
    
    def start_turn(self):
        # For the client to implement.
        pass

    def win(self):
        # For the client to implement.
        pass
    
    def limit_callback(self, message, pile, limit, callee):
        message = message.strip().split()
        if message[0].startswith("!"):
            message = message[1:]
        discard = []
        no_find = []
        for s in message:
            if s.isdigit() and int(s) <= len(pile):
                discard.append(pile.cards[int(s)-1])
            elif s in pile:
                discard.append(pile.find_card(s))
            else:
                no_find.append(s)
        if len(pile) - len(discard) < limit:
            self.output("You cannot discard that many cards.")
            callee()

        if len(no_find) > 0:
            no_find = "Could not find card%s: %s" % ("" if len(no_find) == 1 else "s",
                                                     pretty_print_list(no_find))
        else:
            no_find = ""

        self.output("You discarded: %s.%s" % \
                    (pretty_print_list(discard),
                     no_find))
        self.game.discard(discard)
        if len(pile) > limit:
            callee()
            return False
        
        self.output("Okay, you are all set with the limit.")
        return True
        
    def enforce_hand_limit(self):
        
        def callback(message):
            r = self.game.rule_pile
            t = self.limit_callback(message, self.hand, r.hand_limit, self.enforce_hand_limit)
            self.enforce_keeper_limit()
            return t
        
        h = len(self.hand)
        r = self.game.rule_pile
        if r.hand_limit == 0 and h > 0:
            self.output("Your hand is over the limit of 0. " +
                        "Now discarding all of your cards.")
            self.game.discard(self.hand)
            
        if r.hand_limit > 0 and h > r.hand_limit:
            self.plugin.pubout("%s's hand is over the limit and must discard manually." % self.name)
            self.output("Your hand is over the limit.")
            hand = ["(%d) %s" % (i+1, c) for i, c in enumerate(self.hand)]
            self.output("You have: " + pretty_print_list(hand))
            i = h - r.hand_limit
            self.request_input("Please discard %d card%s." % (i, "" if i == 1 else "s"),
                               (callback, discard_regex % "RKGA"))
            return
        
        self.enforce_keeper_limit()

    def enforce_keeper_limit(self):
        def callback(message):
            r = self.game.rule_pile
            t = self.limit_callback(message, self.keepers, r.keeper_limit, \
                                        self.enforce_keeper_limit)
            self.callback()
            return t
        
        k = len(self.keepers.non_creepers)
        r = self.game.rule_pile
        if r.keeper_limit > 0 and k > r.keeper_limit:
            self.plugin.pubout("%s's keeper pile is over the limit and must discard manually." % self.name)
            self.output("Your keeper pile is over the limit.")
            keepers = ["(%d) %s" % (i+1, c) for i, c in enumerate(self.keepers)]
            self.output("You have: " + pretty_print_list(keepers))
            i = k - r.keeper_limit
            self.request_input("Please discard %d keeper%s." % \
                               (i, "" if i == 1 else "s"),
                               (callback, discard_regex % "K"))
            return
        self.callback()
    
    def enforce_limits(self, callback):
        # Enforce limits.
        
        # I should refactor this to not use direct calls
        # to request_input and instead use loose coupling,
        # but now is not the time.
        self.callback = callback
        
        self.enforce_hand_limit()

    def finish_turn(self):
        def callback():
            self.game.next_turn()
        
        self.enforce_limits(callback)
    
    def draw(self, num_cards=0, action=False):
        if not action:
            if num_cards == 0:
                num_cards = self.draws_left
            if self.draws_left < 1:
                self.output("You can not draw any more cards.")
                return None
            if num_cards > self.draws_left:
                self.output("You can not draw that many cards.")
                return None
        cards = self.game.draw_cards(num_cards)
        cards = self.hand.receive(cards)
        return cards
        
class KeeperPile(CardPile):
    @property
    def game(self):
        return self.player.game

    def receive_card(self, card):
        if "C_TA" in self and card.short_title == "K_MO":
            self.game.discard(self.find_card("C_TA"))
            self.game.channel.output(("%s had the Taxes and Money on the table " + \
                                      "so they are both discarded!") % self.player.name)
            return False
        elif "K_MO" in self and card.short_title == "C_TA":
            self.game.discard(self.find_card("K_MO"))
            self.game.channel.output(("%s had the Taxes and Money on the table " + \
                                      "so they are both discarded!") % self.player.name)
            return False
        return True
    
    @property
    def creepers(self):
        return [c for c in self.cards if c.is_creeper]
        
    @property
    def non_creepers(self):
        return [c for c in self.cards if not c.is_creeper]
    
    def __len__(self):
        return len([c for c in self.cards])

    def __repr__(self):
        return "%s's Keeper Pile" % (self.player.name)

class DrawDiscard(object):
    def __init__(self, game):
        self.draw_pile = CardPile("Draw Pile")
        self.discard_pile = CardPile("Discard Pile")
        self.game = self.draw_pile.game = self.discard_pile.game = game

    def discard(self, cards):
        return self.discard_pile.receive(cards)

    def draw(self, num_cards):
        if len(self.draw_pile) < num_cards:
            self.discard_pile.shuffle()
            self.draw_pile.receive(self.discard_pile)
        return self.draw_pile.draw(num_cards)

    def deal(self, piles, num_cards):
        return self.draw_pile.deal(piles, num_cards)

class RulePile(CardPile):
    def __init__(self, game):
        CardPile.__init__(self, "Rule Pile")
        self.game = game
        
    def receive_card(self, card):
        card.apply_rules(self)
        return True

    def discard(self, cards):
        self.game.discard(cards)

    @property
    def inflation_amount(self):
        return 1 if "R_I" in self else 0
    
    def rich_bonus(self, player):
        return (1 + self.inflation_amount) if ("R_BR" in self and \
               all(len(player.keepers) > len(p.keepers) for p in \
                   self.game.players)) else 0
    
    def poor_bonus(self, player):
        return (1 + self.inflation_amount) if ("R_BP" in self and \
               all(len(player.keepers) < len(p.keepers) for p in \
                   self.game.players)) else 0

    def no_hand_bonus(self, player):
        return (3 + self.inflation_amount) if \
               ("R_BH" in self and len(player.hand) == 0) else 0

    @property
    def draw_amount(self):
        return max(card.draw_amount for card in self.cards) + \
               self.inflation_amount

    @property
    def play_amount(self):
        cards = [card.play_amount for card in self.cards if \
                 card.short_title.startswith("R_P")] + [1]
        if -1 in cards:
            return -1
        return max(cards)

    @property
    def hand_limit(self):
        return max(card.hand_limit for card in self.cards) + self.inflation_amount
    
    @property
    def keeper_limit(self):
        return max(card.keeper_limit for card in self.cards) + self.inflation_amount

    @property
    def turn_order(self):
        return -1 if "R_RO" in self else 1

    @property
    def is_first_play_random(self):
        return "R_FP" in self and self.play_amount != -1 # Don't detect Play All.

class FluxxHand(CardPile):
    @property
    def game(self):
        return self.player.game
    
    def receive_card(self, card):
        if card.type == "Creeper":
            self.player.output("You got a Creeper! You got %s" % card)
            self.player.output("Redrawing another card for you.")
            self.player.plugin.pubout("%s got the Creeper %s while drawing!"\
                                          % (self.player.name, card))
            self.player.keepers.receive(card)
            self.player.draw_amount += 1
            card = self.game.draw_cards(1)[0]
            print card
            return card
        return True

    def __repr__(self):
        return "%s's Hand" % (self.player.name)

class FluxxCard(Card):
    def __init__(self, title, short_title, description):
        Card.__init__(self, title, short_title)
        self.description = description.strip()

    def play(self, player):
        pass
    
    def __str__(self):
        return "%s (%s)" % (self.title, self.short_title)

    @property
    def card_info(self):
        return """
%s (%s)
--------------------------------------
Card Type: %s
Information: %s
%s
        """.strip() % \
        (self.title, self.short_title, self.type,
         self.information, "Description: %s" % self.description \
         if self.description != "" else "")


