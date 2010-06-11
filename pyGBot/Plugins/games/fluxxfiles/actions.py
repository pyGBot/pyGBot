
from pyGBot.Plugins.games.fluxxfiles.fluxx import FluxxCard
from pyGBot.Plugins.games.fluxxfiles.game import pretty_print_list, plural, pp_index
from random import choice


class ActionCard(FluxxCard):
    information = """
When you play this card, do whatever it says.
    """.strip()
    type = "Action"
    def __init__(self, title, short_title, description):
        FluxxCard.__init__(self, title, short_title, description)

    def play(self, player):
        self.do_action(player)
        player.game.discard(self)

    def do_action(self, player):
        pass

class RulesReset(ActionCard):
    
    def __init__(self):
        ActionCard.__init__(self, "Rules Reset", "A_RR", """
Reset to the Basic Rules.

Discard all New Rules cards, and leave only the original Basic Rules card in play.
        """)

    def do_action(self, player):
        rules = player.game.rule_pile
        cards = [card for card in rules if card.short_title != "R_BASIC"]
        rules.discard(cards)

rule_regex = "\d+|r_[a-z]+"

class TrashRule(ActionCard):
    
    def __init__(self):
        ActionCard.__init__(self, "Trash a New Rule", "A_TR", """
Select one of the New Rule cards in play and place it in the discard pile.
        """)

    def do_action(self, player):
        self.player = player
        rules_pile = player.game.rule_pile
        self.rules = [card for card in rules_pile if card.short_title != "R_BASIC"]
        player.halt_game = self.title

    def ask(self):
        
        def callback(message):
            player = self.player
            rule = message
            if rule.isdigit():
                rule = int(rule)
                num_rules = len(self.rules)
                if rule > num_rules:
                    self.player.output("There aren't that many rules in play!")
                    return self.ask()
                rule_picked = self.rules[rule-1]
            else:
                rule_picked = player.game.find_card(rule)
                if rule_picked not in self.rules:
                    player.output("You can't trash that rule.")
                    return self.ask()
            player.plugin.pubout("%s trashed %s." % (player.name, rule_picked))
            player.game.draw_discard.discard(rule_picked)
            player.halt_game = None
            return True

        if(len(self.rules) == 1):
            callback("1") # Just use that card
            return
        
        rules_str = pp_index(self.rules)
        self.player.request_input("Which rule do you want to trash? %s" % rules_str,
                                  (callback, rule_regex))

class NoLimits(ActionCard):
    
    def __init__(self):
        ActionCard.__init__(self, "No Limits", "A_NL", """
Discard all Hand and Keeper Limit rules currently in play.
        """)

    def do_action(self, player):
        rules = player.game.rule_pile
        rules.discard(card for card in rules if card.short_title[0:3] == "R_L")

class TakeAnotherTurn(ActionCard):
    
    def __init__(self):
        ActionCard.__init__(self, "Take Another Turn", "A_AT", """
Take another turn as soon as you finish this one.
        """)

    def do_action(self, player):
        player.game.another_turn_played = True

class Jackpot(ActionCard):

    def __init__(self):
        ActionCard.__init__(self, "Jackpot!", "A_J", """
Draw 3 extra cards!
        """)

    def do_action(self, player):
        handlen = len(player.hand)
        cards = player.draw(3 + player.game.rule_pile.inflation_amount, True)
        player.output("You drew: " + pp_index(cards, handlen))

class EverybodyGetsOne(ActionCard):
    
    regex = "(give |g )?(\d+|[akrgc]_[a-z]+) (to )?[a-z0-9_\-\[\]`^]+"
    
    def __init__(self):
        ActionCard.__init__(self, "Everybody gets 1", "A_EG1", """
Count the number of players in the game (including yourself).
Draw enough cards to give 1 card each to each player, then do so.
        """)
        self.cards = []

    def do_action(self, player):
        self.player = player
        self.draw_amount = (1 + player.game.rule_pile.inflation_amount)
        self.players = player.game.players
        self.num_players = len(self.players)
        self.total_cards = self.draw_amount * self.num_players
        self.cards = player.game.draw_cards(self.total_cards)
        self.cards_given = dict((a.name.lower(),0) for a in self.players)
        self.players_dict = dict((a.name.lower(),a) for a in self.players)
        self.ask()
    
    def ask(self):
        
         def callback(message):
            params = message.replace("give","") \
                            .replace("to","") \
                            .replace("!", "").split()
            if len(params) != 2:
                return self.player.output("Syntax:    %B[give] %Ucard%U [to] %Uplayer%U%B")
            card_picked, receiver = params
            rec_lower = receiver.lower()

            # Check if the player exists.
            if rec_lower not in self.players_dict:
                self.player.output("There is no player with that name.")
                return self.ask()

            # Figure out what card to give
            if card_picked.isdigit():
                card_picked = int(card_picked)
                handlen = len(self.cards)
                if card_picked > handlen:
                    self.player.output("You only have %d card%s to give." % \
                                  (handlen, plural(self.cards)))
                    return self.ask()
                card_picked = self.cards[card_picked-1]
            else:
                card_picked = self.player.game.find_card(card_picked.upper())
                if card_picked not in self.cards:
                    self.player.output("You didn't draw that card!")
                    return self.ask()
            # Check if you've already given that person enough cards
            if self.cards_given[rec_lower] == self.draw_amount:
                self.player.output("You already gave them %d cards." % self.draw_amount)
                return self.ask()
            # Send the card and delete from set that you drew
            hand = self.players_dict[rec_lower].hand
            hand.receive(card_picked)
            self.cards_given[rec_lower] += 1
            self.cards.remove(card_picked)

            # Notify player
            if receiver != self.player.name:
                self.players_dict[rec_lower].output("%s gave you %d: %s." \
                                  % (self.player.name, len(hand), card_picked))
                self.player.output("You gave %s to %s." % (card_picked, receiver))
            else:
                self.player.output("You gave yourself %d: %s." % (len(hand), card_picked))
            # Check if you're done yet
            if sum(self.cards_given.values()) == self.total_cards:
                self.player.halt_game = None
                return True
            return self.ask()
         
         self.player.halt_game = self.title
         self.player.request_input("Choose which cards to give to who: %s" % \
                                  pp_index(self.cards), (callback, self.regex))

keeper_regex = "\d+|[kc]_[a-z]+"

class TrashOrStealSomething(ActionCard):

    def do_action(self, player):
        self.player = player
        self.players = player.game.players
        self.keeper_list = []
        # For the chosen player
        self.ask()

    def ask(self):

        def callback(keeper):
            player, players, keeper_list = self.player, self.players, self.keeper_list
            if keeper.isdigit():
                keeper = int(keeper)
                num_keepers = len(keeper_list)
                if keeper > num_keepers:
                    player.output("There aren't that many keepers on the table!")
                    return self.ask()
                keeper_picked = self.keeper_list[keeper-1]
            else:
                keeper_picked = player.game.deck.find_card(keeper.upper())
                if keeper_picked not in self.keeper_list:
                    player.output("You can't %s that keeper." % (self.word))
                    return self.ask()
            player_name = keeper_picked.owner.player.name
            if player_name != player.name:
                player.plugin.pubout("%s %s %s's %s." % \
                                           (player.name, self.word_past, player_name, keeper_picked))
            else:
                player.plugin.pubout("%s %s their %s." % \
                                           (player.name, self.word_past, keeper_picked))
            self.do(keeper_picked)
            player.halt_game = None
            return True

        
        player, players, keeper_list = self.player, self.players, self.keeper_list
        player.halt_game = self.title
        s = ["Which keeper or creeper do you want to %s?" % self.word]
        for p in players:
            keepers = p.keepers
            if len(keepers) == 0: continue
            s.append(pp_index(keepers, len(self.keeper_list)+1))
        player.request_input('\n'.join(s)
                             (callback, keeper_regex))
    
class TrashSomething(ActionCard):

    def __init__(self):
        ActionCard.__init__(self, "Trash Something", "A_TK", """
Take your choice of any Keeper or Creeper from in front of
any player and put it on the discard pile.

If no one has any Keepers or Creepers, nothing happens when
you play this card.
        """)
        self.word = "trash"
        self.word_past = "trashed"

    def do(self, keeper_picked):
        self.player.game.discard(keeper_picked)
        

class StealSomething(ActionCard):

    def __init__(self):
        ActionCard.__init__(self, "Steal Something", "A_SK", """
Take your choice of any Keeper or Creeper from in front of
another player, and put it in front of you.
        """)
        self.word = "steal"
        self.word_past = "stole"

    def do(self, keeper_picked):
        self.player.keepers.receive(keeper_picked)

class EmptyTrash(ActionCard):
    
    def __init__(self):
        ActionCard.__init__(self, "Empty the Trash", "A_ET", """
Start a new discard pile with this card and shuffle the rest
of the discard pile back into the draw pile.
        """)
    
    def do_action(self, player):
        piles = player.game.draw_discard
        piles.draw_pile.receive(piles.discard_pile)
        piles.draw_pile.shuffle()

class UseWhatYouTake(ActionCard):
    
    def __init__(self):
        ActionCard.__init__(self, "Use What You Take", "A_UT", """
Take a card at random from another player's hand, and play it.
        """)
    
    def do_action(self, player):
        self.player = player
        self.players = [p for p in player.game.players if p != player]
        self.players_dict = dict((a.name.lower(),a) for a in self.players)
        player.halt_game = self.title
        self.ask()
    
    def ask(self):
        
        def callback(player_picked):
            player, players, players_dict = self.player, self.players, self.players_dict
            if player_picked.isdigit():
                player_picked = int(player_picked)
                num_players = len(players)
                if player_picked > num_players:
                    player.output("There aren't that many players!")
                    return self.ask()
                player_picked = players[player_picked-1]
            else:
                if player_picked.lower() not in players_dict:
                    player.output("They're not playing.")
                    return self.ask()
                player_picked = players_dict[player_picked.lower()]
            card_picked = choice(player_picked.hand)
            player_name = player_picked.name
            player.plugin.pubout("%s used %s's %s." % \
                                     (player.name, player_name, card_picked))
            player.hand.receive(card_picked) # So the card belongs to the player now.
            card_picked.play(player)
            player.halt_game = None
            return True

        if len(self.players) == 1:
            callback("1")
        else:
            player, players, players_dict = self.player, self.players, self.players_dict
            regex = "\d|" + "|".join(p.name for p in players)
            player.request_input("Whose player's card do you want to play? %s" % \
                                     pp_index(players), (callback, regex))

class DiscardDraw(ActionCard):
    
    def __init__(self):
        ActionCard.__init__(self, "Discard & Draw", "A_DD", """
Discard your entire hand, then draw as many cards as you discarded.

Do not count this card when determining how many replacement cards to draw.
        """)
    
    def do_action(self, player):
        hand = player.hand
        cards_in_hand = len(hand)
        player.game.draw_discard.discard(hand)
        cards = player.draw(cards_in_hand, True)
        player.output("You drew: " + pp_index(cards))

card_regex="\d|[kcgar]_[a-z0-9]+"

class DrawXUseY(ActionCard):
    
    draw_total = 0
    play_total = 0
    
    def do_action(self, player):
        self.player = player
        player.halt_game = self.title
        self.draw_amount = (self.draw_total + player.game.rule_pile.inflation_amount)
        self.cards = player.game.draw_cards(draw_amount)
        self.ask()
        
    def ask(self):
        
        def callback(card):
            player = self.player
            if card.isdigit():
                card = int(card)
                num_cards = len(self.cards)
                if card == 0:
                    player.output("You silly!")
                    return self.ask()
                if card > num_cards:
                    player.output("You didn't get that many cards!")
                    return self.ask()
                card_picked = self.cards[card-1]
            else:
                card_picked = player.game.find_card(card.upper())
                if card_picked not in self.cards:
                    player.output("You can't play that card.")
                    return self.ask()
            player.hand.receive(card_picked)
            card_picked.play(player)
            self.cards.remove(card_picked)

            if len(self.cards) == self.draw_total - self.play_total:
                player.game.draw_discard.discard(self.cards)
                player.halt_game = None
                return True
            self.ask()

        
        player = self.player
        player.request_input("What do you want to play? " + \
                                 pp_index(cards, len(self.player.hand)), \
                                 (callback, card_regex))

class DrawTwoUseThem(DrawXUseY):

    draw_total = 2
    play_total = 2
    
    def __init__(self):
        ActionCard.__init__(self, "Draw 2 and Use 'em", "A_D2", """
Set your hand aside.

Draw 2 cards, play them in the order you choose, then pick up your
hand and continue with your turn.

This card, and all cards played because of it, are counted as a single play.
        """)

class DrawThreePlayTwo(DrawXUseY):

    draw_total = 3
    play_total = 2
    
    def __init__(self):
        ActionCard.__init__(self, "Draw 3, play 2 of them", "A_D3P2", """
Set your hand aside.

Draw 3 cards and play 2 of them. Discard the last card, then pick up your hand and continue with your turn.

This card, and all cards played because of it, are counted as a single play.
        """)
