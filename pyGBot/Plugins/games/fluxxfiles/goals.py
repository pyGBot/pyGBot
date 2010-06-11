
from pyGBot.Plugins.games.fluxxfiles.fluxx import FluxxCard
from pyGBot.Plugins.games.fluxxfiles.game import pretty_print_list

class GoalCard(FluxxCard):
    information = """
When you play this card, place it face up in the center
of the table. Discard the previous Goal, if any.
    """.strip()
    type = "Goal"
    def __init__(self, title, short_title, description):
        FluxxCard.__init__(self, title, short_title, description)

    def replace_goal(self, new_goal, player):
        self.owner.game.current_goal = new_goal
    
    def check_for_win(self, game):
        pass
    
    def play(self, player):
        g = player.game
        player.hand.cards.remove(self)
        self.owner = g
        
        potato = g.deck.find_card("C_RP")
        if potato.in_play:
            new = g.prev_player(potato.player)
            new.keepers.receive(potato)
            g.output("The Radioactive Potato changed hands from %s to %s!" \
                     % (old.name, new.name))
        if g.current_goal is None:
            g.current_goal = self
        else:
            g.current_goal.replace_goal(self, player)

class KeeperComboGoalCard(GoalCard):
    SHORT_TITLE_FORMAT="G_C"
    def __init__(self, title, *keepers):
        self._k = keepers
        self.SHORT_TITLE_FORMAT += "_%s" * len(keepers)
        GoalCard.__init__(self, title, self.SHORT_TITLE_FORMAT % keepers, "")
    
    def find_keeper(self, short_title):
        try:
            return self.owner.game.deck.find_card("K_"+short_title)[0]
        except KeyError:
            return self.owner.game.deck.find_card("C_"+short_title)[0]

    def keeper(self, id):
        return self.owner.game.deck.find_card(self._k[id])
    
    @property
    def description(self):
        num_keepers = len(self._k)
        return "The player who has %s on the table wins." % \
               pretty_print_list([self.find_keeper(i).title_uncapped \
                                  for i in self._k], use_both=True)

    @description.setter
    def description(self, value):
        pass

    def check_for_win(self, game):
        for player in game.players:
            win = True
            for k in self._k:
                if self.find_keeper(k) not in player.keepers: win = False
            if win: player.win()

class ExclusionKeeperGoalCard(KeeperComboGoalCard):
    SHORT_TITLE_FORMAT="G_E"
    
    @property
    def description(self):
        num_keepers = len(self._k)-1
        s = "If no one has %s on the table, then the player with "
        if num_keepers > 2: s += "%s, " * (num_keepers-1) + "and %s"
        elif num_keepers == 2: s += "both %s and %s"
        elif num_keepers == 1: s += "%s"
        else: return False # What are you doing if you want 0 keepers?
        s += " on the table wins."
        return s % ((self.find_keeper(self._k[-1]).title_uncapped,) + \
               tuple(self.find_keeper(i).title_uncapped for i in self._k[:-1]))
    
    @description.setter
    def description(self, value):
        pass
    
    def check_for_win(self, game):
        for player in game.players:
            if self.find_keeper(self._k[-1]) in player.keepers:
                return
        for player in game.players:
            win = True
            for k in self._k[:-1]:
                if "K_"+k not in player.keepers:
                    win = False
                    break
            if win: player.win()

class FiveKeepers(GoalCard):
    def __init__(self):
        GoalCard.__init__(self, "5 Keepers", "G_5K",
        """
If someone has 5 or more Keepers on the table,
then the player with the most Keepers in play wins.
""")

    def check_for_win(self, game):
        # Check for inflation.
        win_amount = 5 + game.rule_pile.inflation_amount
        for player in game.players:
            if len(player.keepers) >= win_amount:
                player.win()

class TenCardsInHand(GoalCard):
    def __init__(self):
        GoalCard.__init__(self, "Ten Cards In Hand", "G_TC",
        """
If someone has 10 or more cards in his or her hand,
then the player with the most cards in hand wins.
""")
    
    def check_for_win(self, game):
        # Check for inflation.
        win_amount = 10 + game.rule_pile.inflation_amount
        win = None
        for player in game.players:
            if len(player.hand) >= win_amount:
                if win is None:
                    win = player
                else:
                    return
        if win is not None:
            win.win()
            
class AllYouNeedIsLove(GoalCard):
    def __init__(self):
        GoalCard.__init__(self, "All you need is Love", "G_L",
        """
The player who has Love on the table wins, but only
if that player has no other Keepers on the table.
""")
    
    def check_for_win(self, game):
        for player in game.players:
            if len(player.keepers) == 1 and "K_LO" in player.keepers:
                player.win()

class PartySnacks(GoalCard):
    def __init__(self):
        GoalCard.__init__(self, "Party Snacks", "G_PS",
        """
You win if you have the Party and at least 1 food Keeper on
the table in front of you. (Cookies, Bread, Chocolate)
""")
    
    def check_for_win(self, game):
        for player in game.players:
            if "K_PS" in player.keepers and ("K_CO" in player.keepers or \
                                             "K_BR" in player.keepers or \
                                             "K_CH" in player.keepers):
                    player.win()
