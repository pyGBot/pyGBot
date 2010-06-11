
from pyGBot.Plugins.games.fluxxfiles.goals import *
from pyGBot.Plugins.games.fluxxfiles.rules import *
from pyGBot.Plugins.games.fluxxfiles.keepers import *
from pyGBot.Plugins.games.fluxxfiles.actions import *

from pyGBot.Plugins.games.fluxxfiles.game import Deck

class FluxxDeck(Deck):

    def __init__(self):
        self.cards = self.make_deck()
        # Workaround so we can look up the
        # descriptions of keepers without
        # a Game.
        self.game = self
        self.deck = self
        
    @staticmethod
    def make_deck():
        def make_rules():
            rules = [BasicRules()]
            rules += (DrawRuleCard(amount) for amount in (2, 3, 4, 5))
            rules += (PlayRuleCard(amount) for amount in (2, 3, 4))
            rules += (PlayAllRuleCard())
            rules += (HandLimitRuleCard(amount) for amount in (0, 1, 2))
            rules += (KeeperLimitRuleCard(amount) for amount in (2, 3, 4))
            rules += (NoHandBonusRuleCard(), PoorBonusRuleCard(), RichBonusRuleCard())
            rules += (InflationRuleCard(), ReverseOrderRuleCard())
            rules += (FirstPlayRandomRuleCard(), DoubleAgendaRuleCard())
            return rules
        
        def make_keepers():
            def m(t):
                if isinstance(t, str):
                    return t,
                return t
            
            return [KeeperCard(*m(t)) for t in ("Bread", "Chocolate",  "Cookies",
                                                "Dreams", "Love", "Milk", "Money",
                                                "Peace", "Sleep", ("Television", "TV"),
                                                "The Brain", "The Cosmos", "The Eye",
                                                "The Moon", "The Party", "The Rocket",
                                                "The Sun", "The Toaster", "Time")] + \
                   [CreeperCard("Radioactive Potato", "Any time the Goal changes, " +
                                "move this card in the counter-turn direction."),
                    CreeperCard("Death", "If you have this at the start of your " +
                                "turn, discard something else you have in play " +
                                "(a Keeper or a Creeper). You may discard this " +
                                 "anytime it stands alone."),
                    CreeperCard("Taxes", "If you have Money on the table, " +
                                "discard both that and this."),
                    CreeperCard("War")]

        def make_goals():
            return [KeeperComboGoalCard("Rocket Science", "TR", "TB"),
                    KeeperComboGoalCard("Time is Money", "TI", "MO"),
                    KeeperComboGoalCard("War = Death", "WA", "DE"),
                    KeeperComboGoalCard("Winning the Lottery", "DR", "MO"),
                    KeeperComboGoalCard("Squishy Chocolate", "TS", "CH"),
                    KeeperComboGoalCard("Milk and Cookies", "MI", "CO"),
                    KeeperComboGoalCard("Rocket to the Moon", "TR", "TM"),
                    KeeperComboGoalCard("Hearts and Minds", "LO", "TB"),
                    KeeperComboGoalCard("The Appliances", "TT", "TV"),
                    KeeperComboGoalCard("Hippyism", "PE", "LO"),
                    KeeperComboGoalCard("Night and Day", "TM", "TS"),
                    KeeperComboGoalCard("Baked Goods", "BR", "CO"),
                    KeeperComboGoalCard("Bed Time", "SL", "TI"),
                    KeeperComboGoalCard("Death by Chocolate", "DE", "CH"),
                    KeeperComboGoalCard("Toast", "BR", "TT"),
                    KeeperComboGoalCard("Chocolate Cookies", "CH", "CO"),
                    KeeperComboGoalCard("Chocolate Milk", "CH", "MI"),
                    KeeperComboGoalCard("Dreamland", "SL", "DR"),
                    KeeperComboGoalCard("Interstellar Spacecraft", "TR", "TC"),
                    KeeperComboGoalCard("Star Gazing", "TC", "TE"),
                    KeeperComboGoalCard("The Mind's Eye", "TB", "TE"),
                    KeeperComboGoalCard("Dough", "BR", "MO"),
                    KeeperComboGoalCard("All That Is Certain", "DE", "TA"),
                    # Custom ones
                    # KeeperComboGoalCard("A Good Investment", "TI", "MO", "TB"),
                    # KeeperComboGoalCard("Gluttony", "MI", "CH", "BR", "CO"),
                    FiveKeepers(),
                    TenCardsInHand(),
                    ExclusionKeeperGoalCard("The Brain (no TV)", "TB", "TV"),
                    ExclusionKeeperGoalCard("Peace (no War)", "PE", "WA"),
                    PartySnacks(),
                    AllYouNeedIsLove()]
                    
        def make_actions():
            return [EverybodyGetsOne(),
                    Jackpot(),
                    TakeAnotherTurn(),
                    NoLimits(),
                    TrashRule(),
                    TrashSomething(),
                    StealSomething(),
                    DiscardDraw(),
                    EmptyTrash(),
                    UseWhatYouTake(),
                    RulesReset(),
                    DrawTwoUseThem()]
        
        return make_rules() + make_keepers() + make_goals() + make_actions()


if __name__ == "__main__":
    # Test the FluxxDeck
    deck = FluxxDeck()
    for card in deck.cards:
        print card.card_info, "\n\n"
