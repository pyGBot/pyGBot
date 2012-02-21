
from pyGBot.Plugins.games.fluxxfiles.fluxx import FluxxCard
from pyGBot.Plugins.games.fluxxfiles.goals import GoalCard
from pyGBot.Plugins.games.fluxxfiles.game import pretty_print_list

class RuleCard(FluxxCard):
    information = """
This rule goes into effect as soon as you play it.
Place this card face up in the center of the table.
Discard it when a newer rule contradicts it.
    """.strip()
    type = "Rule"
    def __init__(self, title, short_title, description):
        FluxxCard.__init__(self, title, short_title, description)
        self.draw_amount = -1
        self.play_amount = -1
        self.hand_limit = -1
        self.keeper_limit = -1
    
    def apply_rules(self, rules):
        pass
    
    def play(self, player):
        self.owner.game.rule_pile.receive(self)


class BasicRules(RuleCard):
    def __init__(self):
        RuleCard.__init__(self, "Draw 1, Play 1", "R_BASIC", """
Draw 1 card per turn.
Play 1 card per turn.
No Hand Limit.
No Keeper Limit.

Leave this card on the table even when these rules
are replaced by New Rule cards.
        """)
        
        self.information = """
Start by shuffling the deck and deal 3 cards to
each player. Place this card in the center of the
table.
        """
        self.draw_amount = 1
        self.play_amount = 1
        self.hand_limit = -1
        self.keeper_limit = -1

class DrawRuleCard(RuleCard):
    def __init__(self, amount):
        RuleCard.__init__(self, "Draw %d" % amount, "R_D%d" % amount, """
Draw %d cards per turn.

The person who played this card should immediately
draw extra cards (if needed) so that they have
drawn %d cards this turn.
        """ % (amount, amount))
        
        self.draw_amount = amount
        
    def apply_rules(self, rules):
        # Discard the current draw rule card.
        cards = [c for c in rules.cards if c.draw_amount > 1]
        rules.discard(cards)
    
class PlayRuleCard(RuleCard):
    def __init__(self, amount):
        RuleCard.__init__(self, "Play %s" % amount, "R_P%d" % amount,
        """
Play %s cards per turn.

If you have fewer than %d cards in your hand,
play all your cards.
        """ % (amount, amount))
        
        self.play_amount = amount
    
    def apply_rules(self, rules):
        # Discard the current play rule card.
        cards = [c for c in rules.cards if c.play_amount > 1 or hasattr(c, "magic")]
        rules.discard(cards)

class PlayAllMagic(object):
    def __add__(self, *a, **b):
        return self
    __radd__ = __add__
    magic = True

    def __str__(self):
        return "All"
    
class PlayAllRuleCard(PlayRuleCard):
    def __init__(self):
        PlayRuleCard.__init__(self, 0)
        RuleCard.__init__(self, "Play All",  "R_P0", """
Play all of the cards in your hand each turn.
        """)

        self.play_amount = PlayAllMagic()
        
class HandLimitRuleCard(RuleCard):
    def __init__(self, amount):
        RuleCard.__init__(self, "Hand Limit %d" % amount,
                          "R_LH%d" % amount, """
If it isn't your turn, you should only have %d cards
in your hand. If you have extra cards, discard them
immediately.

During your turn, you may ignore the Hand Limit, as
long as you discard all but %d of your cards when
you end your turn.
        """ % (amount, amount))

        self.hand_limit = amount
        
    def apply_rules(self, rules):
        # Discard the current hand limit rule card.
        cards = [c for c in rules.cards if c.hand_limit > -1]
        rules.discard(cards)
            
class KeeperLimitRuleCard(RuleCard):
    def __init__(self, amount):
        RuleCard.__init__(self, "Keeper Limit %d" % amount,
                          "R_LK%d" % amount, """
If it isn't your turn, you should only have %d Keepers
in play. Discard any extras immediately.

You may play new Keepers during your turn as long as
you discard all but %d at the end of your turn.
        """ % (amount, amount))

        self.keeper_limit = amount
        
    def apply_rules(self, rules):
        # Discard the current keeper limit rule card.
        cards = [c for c in rules.cards if c.keeper_limit > -1]
        rules.discard(cards)

class NoHandBonusRuleCard(RuleCard):
    def __init__(self):
        RuleCard.__init__(self, "No-Hand Bonus", "R_BH", """
If you have no cards in your hand at the start of your
turn, draw a new hand of 3 cards before observing
the current Draw rule.
        """)

class PoorBonusRuleCard(RuleCard):
    def __init__(self):
        RuleCard.__init__(self, "Poor Bonus", "R_BP", """
If you have fewer Keepers in than than anyone else,
draw 1 extra card.
        """)

class RichBonusRuleCard(RuleCard):
    def __init__(self):
        RuleCard.__init__(self, "Rich Bonus", "R_BR", """
If you have fewer Keepers in than than anyone else,
you may choose to play 1 extra card.
        """)

class InflationRuleCard(RuleCard):
    def __init__(self):
        RuleCard.__init__(self, "Inflation (X=X+1)", "R_I", """
Any time a numeral is seen on another card, add one
to that numeral. For example, 1 becomes 2, while one
remains one.""")

class DoubleAgendaRuleCard(RuleCard, GoalCard):
    
    goal1, goal2 = None, None
    
    def __init__(self):
        RuleCard.__init__(self, "Double Agenda", "R_DA", """
A second Goal can now be played. After this, whoever plays
a new Goal (or causes this card to be discarded) must
choose which of the current Goals to discard.

You win if you satisfy either Goal. (In the case of a tie,
continue playing until a clear winner emerges.)
        """)
        self.type = "Rule"
    
    def check_for_win(self, game):
        if self.goal1 is not None:
            self.goal1.check_for_win(game)
        if self.goal2 is not None:
            self.goal2.check_for_win(game)
    
    def replace_goal(self, new_goal, player):
        regex = "1|2|[gG]_[a-zA-Z]+"

        def callback(message):
            player = self.player
            choice = message.strip()
            if choice == "1" or self.goal1.short_title == choice.upper():
                player.plugin.pubout("%s replaced %s with %s." % \
                                         (player.name, self.goal1, self.new_goal))
                self.goal1 = self.new_goal
                player.halt_game = None
                return True
            elif choice == "2" or self.goal2.short_title == choice.upper():
                player.plugin.pubout("%s replaced %s with %s." % \
                                         (player.name, self.goal2, self.new_goal))
                self.goal2 = self.new_goal
                player.halt_game = None
                return True
            else:
                player.request_input("Which goal do you want to remove? (1 or 2)",
                                     (callback, regex))
        
        if self.goal1 is None:
            self.goal1 = new_goal
        elif self.goal2 is None:
            self.goal2 = new_goal
        else:
            self.new_goal = new_goal
            player.halt_game = self.title
            self.player = player
            return player.request_input(("The goals are 1: '%s' and 2: '%s'. " +
                                 "Which goal do you want to remove?") %
                                 (self.goal1, self.goal2), (callback, regex))
            
    def play(self, player):
        self.owner.cards.remove(self)
        self.goal1 = self.owner.game.current_goal
        if self.goal1 is None:
            self.owner.game.current_goal = self
        else:
            self.goal1.replace_goal(self, player)
    
    def __str__(self):
        s = pretty_print_list((self.goal1, self.goal2))
        if s != "":
            s = ": " + s
        return "Double Agenda (R_DA)%s" % s
    
class ReverseOrderRuleCard(RuleCard):
    def __init__(self):
        RuleCard.__init__(self, "Reverse Order", "R_RO", """
At the end of the turn in which this card is played,
turn order will proceeed in the opposite direction.

When this rule is discarded, the original turn order
is restored.
        """)
    def apply_rules(self, rules):
        rules.game.reverse_played = True

class FirstPlayRandomRuleCard(RuleCard):
    def __init__(self):
        RuleCard.__init__(self, "First Play Random", "R_FP", """
The first card you play must be chosed at random
from your hand by the player on your left.

Ignore this rule if, at the start of your turn, the
current Rule cards allow you to play only one card.
        """)

